# -*- coding: utf-8 -*-
from django.urls import path
from django_addon.utils import i18n_patterns
import django_addons.urls
# import graphene_django.views

# from schema import schema


urlpatterns = [
    # add your own patterns here
    # url(r'^api/', include('timelapse_manager.api_urls')),
    # url(
    #     r'^graphql',
    #     graphene_django.views.GraphQLView.as_view(schema=schema, graphiql=True),
    # ),
] + django_addons.urls.patterns() + i18n_patterns(
    # add your own i18n patterns here
    *django_addons.urls.i18n_patterns()  # MUST be the last entry!
)
