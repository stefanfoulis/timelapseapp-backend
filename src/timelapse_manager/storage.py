# -*- coding: utf-8 -*-
import os
import six
import furl
import posixpath

import boto3

from django.conf import settings
from django.core.files.storage import get_storage_class, FileSystemStorage
from django.utils.functional import LazyObject
from django.utils.text import slugify

import django.core.files.storage
import storages.backends.s3boto3


SCHEMES = {
    's3': 'timelapse_manager.storage.S3Storage',
    'file': 'timelapse_manager.storage.FileSystemStorage',
}


class FileSystemStorage(django.core.files.storage.FileSystemStorage):
    def __init__(self, dsn):
        base_url = dsn.args.get('url')
        super(FileSystemStorage, self).__init__(
            location=six.text_type(dsn.path),
            base_url=base_url,
        )
        if base_url is None:
            self.base_url = None


class S3Storage(storages.backends.s3boto3.S3Boto3Storage):
    addressing_styles = {
        'subdomain': 'virtual',
        'ordinary': 'path',
    }

    def __init__(self, dsn):
        protocols = dsn.scheme.split('+')
        if len(protocols) >= 2:
            # s3+http:// -> protocol=http
            # s3+https:// -> protocol=https
            # s3+xyz+https:// -> protocol=https
            protocol = protocols[-1]
        else:
            # s3:// -> protocol=https
            protocol = 'https'

        endpoint_url = furl.furl().set(
            scheme=protocol,
            host=dsn.host,
            port=dsn.port,
        )
        bucket_name = dsn.args.get('bucket_name')
        if bucket_name is None:
            # AWS style bucket name extraction
            bucket_name, endpoint_url.host = endpoint_url.host.split('.', 1)

        addressing_style = dsn.args.get('calling_format')
        if addressing_style:
            addressing_style = self.addressing_styles[addressing_style]
        else:
            addressing_style = 'virtual'
        config = dict(
            access_key=dsn.username,
            secret_key=dsn.password,
            bucket_name=bucket_name,
            endpoint_url=endpoint_url.url,
            addressing_style=addressing_style,
            location=six.text_type(dsn.path).lstrip('/'),
            custom_domain=furl.furl(dsn.args.get('url')).netloc,
            default_acl=dsn.args.get('acl', 'private'),
            querystring_auth=False,
        )
        if dsn.args.get('region_name'):
            config['region_name'] = dsn.args.get('region_name')

        if dsn.args.get('auth'):
            config['signature_version'] = dsn.args.get('auth')
        from pprint import pprint as pp
        pp(config)
        super(S3Storage, self).__init__(**config)

    def listdir(self, path):
        # Stolen and slightly adapted from
        # https://github.com/etianen/django-s3-storage/blob/24fde40dfdb7e7125827e5e9f39239bd79b2f6f7/django_s3_storage/storage.py#L299-L317
        # The default implementation of listdir will take minutes to list 1
        # directory in the root of a bucket if the bucket has millions of
        # objects.
        # This version is efficient.
        path = self._get_key_name(path)
        path = "" if path == "." else path + "/"
        # Look through the paths, parsing out directories and paths.
        files = []
        dirs = []
        paginator = self.client.get_paginator("list_objects_v2")
        pages = paginator.paginate(
            Bucket=self.bucket_name,
            Delimiter="/",
            Prefix=path,
        )
        for page in pages:
            for entry in page.get("Contents", ()):
                files.append(posixpath.relpath(entry["Key"], path))
            for entry in page.get("CommonPrefixes", ()):
                dirs.append(posixpath.relpath(entry["Prefix"], path))
        # All done!
        return dirs, files

    @property
    def client(self):
        # Variant of
        # https://github.com/etianen/django-s3-storage/blob/24fde40dfdb7e7125827e5e9f39239bd79b2f6f7/django_s3_storage/storage.py#L137-L140
        # because our custom listdir needs it.
        client = getattr(self._connections, 'client', None)
        if client is None:
            self._connections.client = boto3.client(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                aws_session_token=self.security_token,
                region_name=self.region_name,
                use_ssl=self.use_ssl,
                endpoint_url=self.endpoint_url,
                config=self.config
            )
        return self._connections.client

    def _get_key_name(self, name):
        # Stolen from
        # https://github.com/etianen/django-s3-storage/blob/24fde40dfdb7e7125827e5e9f39239bd79b2f6f7/django_s3_storage/storage.py#L166-L169
        # for listdir. Adapted slightly.
        if name.startswith("/"):
            name = name[1:]
        return posixpath.normpath(
            posixpath.join(
                self.location,
                name.replace(os.sep, "/"),
            ),
        )


class NotImplementedStorage(django.core.files.storage.Storage):
    def open(self, name, mode='rb'):
        raise NotImplementedError

    def save(self, name, content, max_length=None):
        raise NotImplementedError

    def get_valid_name(self, name):
        raise NotImplementedError

    def get_available_name(self, name, max_length=None):
        raise NotImplementedError


class _DSNConfiguredStorage(LazyObject):
    def _setup(self):
        dsn = getattr(settings, self._setting_name, None)
        if not dsn:
            self._wrapped = NotImplementedStorage()
        else:
            url = furl.furl(dsn)
            backend_name = url.scheme.split('+')[0]
            storage_class = django.core.files.storage.get_storage_class(SCHEMES[backend_name])
            # Django >= 1.9 now knows about LazyObject and sets them up before
            # serializing them. To work around this behavior, the storage class
            # itself needs to be deconstructible.
            storage_class = type(storage_class.__name__, (storage_class,), {
                'deconstruct': self._deconstructor,
            })
            self._wrapped = storage_class(url)


def dsn_configured_storage(setting_name):
    path = '{}.{}'.format(
        dsn_configured_storage.__module__,
        dsn_configured_storage.__name__,
    )
    return type('DSNConfiguredStorage', (_DSNConfiguredStorage,), {
        '_setting_name': setting_name,
        '_deconstructor': lambda self: (path, [setting_name], {}),
    })()


timelapse_storage = dsn_configured_storage('TIMELAPSE_STORAGE_DSN')


def structured_data_to_image_filename(data):
    return '{shot_at}.{original_name}.{size}.{md5sum}.JPG'.format(**data)


def upload_to_thumbnail(instance, filename, size=None):
    from . import utils
    original_path = instance.original.name
    original_name = os.path.basename(original_path)
    filename = '{shot_at}.{original_name}.{size}.{md5sum}.JPG'.format(
        shot_at=utils.datetime_to_datetimestr(instance.shot_at),
        original_name=instance.name,
        size=size,
        md5sum=getattr(instance, 'scaled_at_{}_md5'.format(size)),
    )
    return '{camera}/{size}/{day}/{filename}'.format(
        size=size,
        day=original_name[:10],
        filename=filename,
        camera=instance.camera.name,
    )


def upload_to_movie_rendering(instance, filename):
    extension = os.path.splitext(filename)[1][1:]
    filename = '{name}.{size}.{md5sum}.{extension}'.format(
        name=slugify(instance.movie.name),
        size=instance.size,
        md5sum=instance.file_md5,
        extension=extension,
    )
    return 'movies/{camera}/{size}/{filename}'.format(
        size=instance.size,
        filename=filename,
        camera=instance.movie.camera.name,
    )
