# -*- coding: utf-8 -*-
from rest_framework import mixins, serializers, viewsets

from . import models


class ImageUrlSerializer(serializers.Serializer):
    image_url = serializers.CharField(max_length=1024, write_only=True)

    def create(self, validated_data):
        images = models.Image.objects.create_or_update_images_from_urls(
            urls=[validated_data["image_url"]]
        )
        return images[0]


class ImageIntakeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.Image.objects.none()
    serializer_class = ImageUrlSerializer


class ImageUrlsSerializer(serializers.Serializer):
    images = ImageUrlSerializer(many=True)

    def create(self, validated_data):
        images = models.Image.objects.create_or_update_images_from_urls(
            urls=[img["image_url"] for img in validated_data["images"]]
        )
        return {"images": []}


class ImagesIntakeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.Image.objects.none()
    serializer_class = ImageUrlsSerializer
