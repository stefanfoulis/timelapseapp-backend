# -*- coding: utf-8 -*-
from django.db.models import ImageField

import django_filters

from . import models


class DayFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(lookup_expr="iexact")
    date_year = django_filters.NumberFilter(field_name="date", lookup_expr="year")
    date_year_gte = django_filters.NumberFilter(
        field_name="date", lookup_expr="year__gte"
    )
    date_year_lte = django_filters.NumberFilter(
        field_name="date", lookup_expr="year__lte"
    )

    class Meta:
        model = models.Day
        fields = ("date",)
        order_by = True


class ImageFilter(django_filters.FilterSet):
    shot_at_gte = django_filters.DateTimeFilter(field_name="shot_at", lookup_expr="gte")
    shot_at_lte = django_filters.DateTimeFilter(field_name="shot_at", lookup_expr="lte")

    class Meta:
        model = models.Image
        fields = {
            "name": ["exact", "icontains", "istartswith"],
            "shot_at": ["exact"],
            "original": ["icontains", "istartswith"],
            "original_md5": ["exact", "icontains", "istartswith"],
        }
        filter_overrides = {ImageField: {"filter_class": django_filters.CharFilter}}
        order_by = True
