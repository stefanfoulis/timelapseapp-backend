# -*- coding: utf-8 -*-
from django.contrib.auth import models as auth_models
from django.db.models import Q

import graphene
from graphene.relay import Node
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from . import models, schema_filters


def get_url(instance, fieldname):
    field = getattr(instance, fieldname)
    if field:
        return field.url
    return ""


class ImageNode(DjangoObjectType):
    class Meta:
        model = models.Image
        interfaces = (Node,)

    original_url = graphene.String()
    scaled_at_160x120_url = graphene.String()
    scaled_at_320x240_url = graphene.String()
    scaled_at_640x480_url = graphene.String()

    def resolve_original_url(self, info):
        return get_url(self, "original")

    def resolve_scaled_at_160x120_url(self, info):
        return get_url(self, "scaled_at_160x120")

    def resolve_scaled_at_320x240_url(self, info):
        return get_url(self, "scaled_at_320x240")

    def resolve_scaled_at_640x480_url(self, info):
        return get_url(self, "scaled_at_640x480")


class DayNode(DjangoObjectType):
    class Meta:
        model = models.Day
        interfaces = (Node,)

    images = DjangoFilterConnectionField(
        ImageNode, filterset_class=schema_filters.ImageFilter
    )
    key_frames = DjangoFilterConnectionField(
        ImageNode, filterset_class=schema_filters.ImageFilter
    )

    def resolve_images(self, info):
        return self.images.all()

    def resolve_key_frames(self, info):
        return self.key_frames.all()


class CameraControllerNode(DjangoObjectType):
    class Meta:
        model = models.CameraController
        interfaces = (Node,)
        filter_fields = {"name": ["exact", "icontains", "istartswith"]}


class CameraNode(DjangoObjectType):
    class Meta:
        model = models.Camera
        interfaces = (Node,)
        filter_fields = {"name": ["exact", "icontains", "istartswith"]}


class StreamNode(DjangoObjectType):
    class Meta:
        model = models.Stream
        interfaces = (Node,)
        filter_fields = {"name": ["exact", "icontains", "istartswith"]}

    days = DjangoFilterConnectionField(
        DayNode, filterset_class=schema_filters.DayFilter
    )
    images = DjangoFilterConnectionField(
        ImageNode, filterset_class=schema_filters.ImageFilter
    )
    latest_image = graphene.Field(ImageNode)

    def resolve_latest_image(self, info):
        return (
            models.Image.objects.exclude(
                Q(original="")
                | Q(scaled_at_160x120="")
                | Q(scaled_at_320x240="")
                | Q(scaled_at_640x480="")
            )
            .order_by("-shot_at")
            .first()
        )


class UserNode(DjangoObjectType):
    class Meta:
        model = auth_models.User
        interfaces = (Node,)

    only_fields = ("username", "first_name", "last_name", "email", "images")
    exclude_fields = ("password",)
    images = DjangoFilterConnectionField(
        ImageNode, filterset_class=schema_filters.ImageFilter
    )
    latest_image = graphene.Field(ImageNode)

    def resolve_images(self, info, first=None):
        first = first or 10
        return models.Image.objects.all().order_by("-shot_at")[:first]

    def resolve_latest_image(self, info):
        return (
            models.Image.objects.exclude(
                Q(original="")
                | Q(scaled_at_160x120="")
                | Q(scaled_at_320x240="")
                | Q(scaled_at_640x480="")
            )
            .order_by("-shot_at")
            .first()
        )


class Query(graphene.AbstractType):
    image = Node.Field(ImageNode)
    all_images = DjangoFilterConnectionField(
        ImageNode, filterset_class=schema_filters.ImageFilter
    )

    camera_controller = Node.Field(CameraControllerNode)
    all_camera_controllers = DjangoFilterConnectionField(CameraControllerNode)

    camera = Node.Field(CameraNode)
    all_cameras = DjangoFilterConnectionField(CameraNode)

    stream = Node.Field(StreamNode)
    all_streams = DjangoFilterConnectionField(StreamNode)

    day = Node.Field(DayNode)
    all_days = DjangoFilterConnectionField(
        DayNode, filterset_class=schema_filters.DayFilter
    )

    viewer = graphene.Field(UserNode)

    def resolve_viewer(self, info):
        if info.context.user.is_anonymous:
            return None
        return info.context.user
