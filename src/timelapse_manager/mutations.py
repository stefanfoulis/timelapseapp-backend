import graphene
from django.core.exceptions import ValidationError
from graphene import relay
from graphql_relay import from_global_id

from .schema import ImageNode
from . import models


def get_object(object_name, relayId, otherwise=None):
    try:
        return object_name.objects.get(pk=from_global_id(relayId)[1])
    except:
        return otherwise


def get_errors(e):
    # transform django errors to redux errors
    # django: {"key1": [value1], {"key2": [value2]}}
    # redux: ["key1", "value1", "key2", "value2"]
    fields = e.message_dict.keys()
    messages = ['; '.join(m) for m in e.message_dict.values()]
    errors = [i for pair in zip(fields, messages) for i in pair]
    return errors


class GenerateThumbnails(relay.ClientIDMutation):
    class Input:
        id = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    image = graphene.Field(ImageNode)

    @classmethod
    def mutate_and_get_payload(cls, context, info, **args):
        try:
            image = get_object(models.Image, args['id'])
            if image:
                image.create_thumbnails()
                return cls(image=image)
        except ValidationError as e:
            return cls(image=None, errors=get_errors(e))
