from django.urls import path, include
from django_addon.utils import i18n_patterns
import django_addons.urls
import graphene_django.views

from schema import schema


urlpatterns = [
    # add your own patterns here
    path('chat/', include('chat.urls')),
    path('api/', include('timelapse_manager.api_urls')),
    path(
        'graphql/',
        graphene_django.views.GraphQLView.as_view(schema=schema, graphiql=True),
    ),
] + django_addons.urls.patterns() + i18n_patterns(
    # add your own i18n patterns here
    *django_addons.urls.i18n_patterns()  # MUST be the last entry!
)
