# Generated by Django 2.1.1 on 2018-09-29 11:01

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("timelapse_manager", "0002_stream_cover_image")]

    operations = [
        migrations.CreateModel(
            name="TagTimerange",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("start_at", models.DateTimeField()),
                ("end_at", models.DateTimeField()),
                (
                    "stream",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tag_timeranges",
                        to="timelapse_manager.Stream",
                    ),
                ),
            ],
            options={"ordering": ("start_at", "end_at")},
        ),
        migrations.CreateModel(
            name="VideoClip",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True, default=None)),
                ("speed_factor", models.FloatField(default=4000.0)),
                (
                    "stream",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="video_clips",
                        to="timelapse_manager.Stream",
                    ),
                ),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.AlterModelOptions(name="movie", options={}),
        migrations.AlterModelOptions(name="tag", options={}),
        migrations.RemoveField(model_name="movie", name="camera"),
        migrations.RemoveField(model_name="movie", name="description"),
        migrations.RemoveField(model_name="movie", name="speed_factor"),
        migrations.RemoveField(model_name="movie", name="tags"),
        migrations.RemoveField(model_name="tag", name="end_at"),
        migrations.RemoveField(model_name="tag", name="start_at"),
        migrations.RemoveField(model_name="tag", name="stream"),
        migrations.AddField(
            model_name="tag",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="tag",
            name="name",
            field=models.CharField(default="", max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="movie",
            name="name",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.DeleteModel(name="TagInfo"),
        migrations.AddField(
            model_name="videoclip",
            name="tags",
            field=models.ManyToManyField(
                blank=True, related_name="video_clips", to="timelapse_manager.Tag"
            ),
        ),
        migrations.AddField(
            model_name="tagtimerange",
            name="tag",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="tag_timeranges",
                to="timelapse_manager.Tag",
            ),
        ),
    ]
