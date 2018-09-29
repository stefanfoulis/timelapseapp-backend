# -*- coding: utf-8 -*-
import graphene
from graphene import ObjectType
from graphene.relay import Node
from graphene_django.debug import DjangoDebug

import timelapse_manager.schema
import timelapse_manager.mutations


class Query(timelapse_manager.schema.Query, graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name="__debug")
    node = Node.Field()


class Mutation(ObjectType):
    create_thumbnails_for_image = timelapse_manager.mutations.GenerateThumbnails.Field()


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    types=[
        timelapse_manager.schema.UserNode,
        timelapse_manager.schema.DayNode,
        timelapse_manager.schema.ImageNode,
        timelapse_manager.schema.CameraNode,
        timelapse_manager.schema.StreamNode,
    ],
)
