# -*- coding: utf-8 -*-
from django.conf.urls import include, url

from rest_framework import routers

from . import api

router = routers.DefaultRouter()
router.register("image-intake", api.ImageIntakeViewSet, base_name="")
router.register("images-intake", api.ImagesIntakeViewSet, base_name="")


urlpatterns = [
    url(r"^v1/", include(router.urls)),
    url(r"^v1/", include((router.urls, "timelapse_manager"), namespace="v1")),
    # Authentication views provided by DRF.
    url(
        r"^auth/",
        include(
            ("rest_framework.urls", "timelapse_manager"), namespace="rest_framework"
        ),
    ),
]
