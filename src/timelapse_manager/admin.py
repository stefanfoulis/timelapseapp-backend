import datetime

from django.contrib import admin, messages
from django.db import models
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe

import eliot

from . import models, tasks, utils


@admin.register(models.CameraController)
class CameraControllerAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Camera)
class CameraAdmin(admin.ModelAdmin):
    raw_id_fields = ("controller", "active_image_stream")


@admin.register(models.Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    raw_id_fields = ("cover_image",)
    actions = (
        "create_days_for_existing_images_action",
        "create_days_for_oldest_existing_image_until_today_action",
    )

    def create_days_for_existing_images_action(self, request, queryset):
        for stream in queryset:
            days = stream.create_days()
            self.message_user(
                request,
                "{}: created {} days. Now has a total of {} days.".format(
                    stream, len(days), stream.days.all().count()
                ),
            )

    def create_days_for_oldest_existing_image_until_today_action(
        self, request, queryset
    ):
        for stream in queryset:
            day_one = stream.images.order_by("shot_at").first()
            if not day_one:
                self.message_user(
                    request, "{}: no existing images!", level=messages.WARNING
                )
                continue
            days = []
            start_on = day_one.shot_at.date()
            end_on = datetime.date.today()
            for date in utils.daterange(start_on=start_on, end_on=end_on):
                day, created = models.Day.objects.get_or_create(
                    stream=stream, date=date
                )
                if created:
                    days.append(day)
            self.message_user(
                request,
                "{}: created {} days. Now has a total of {} days. ({} - {})".format(
                    stream, len(days), stream.days.all().count(), start_on, end_on
                ),
            )


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = (
        "stream",
        "shot_at",
        "preview_html",
        "original",
        "scaled_at_640x480",
        "scaled_at_320x240",
        "scaled_at_160x120",
    )
    list_filter = (
        "stream",
        # TODO: filter by has original, has scaled
    )
    date_hierarchy = "shot_at"
    search_fields = (
        "original",
        # 'scaled_at_640x480',
        # 'scaled_at_640x480',
        # 'scaled_at_640x480',
    )
    raw_id_fields = ("stream",)
    actions = ("create_thumbnails_action",)

    def create_thumbnails_action(self, request, queryset):
        with eliot.start_action(
            action_type="timelapse:admin:create_thumbnails_action"
        ) as action:
            for obj in queryset:
                task_uuid = action.serialize_task_id().decode("ascii")
                print("=" * 30)
                print(task_uuid)
                print("-" * 30)
                tasks.create_thumbnails_for_image.delay(
                    image_id=str(obj.id), eliot_parent_uuid=task_uuid
                )

    def preview_html(self, obj):
        if obj.scaled_at_160x120:
            return format_html(
                '<img src="{}" style="width: 160px;"/>', obj.scaled_at_160x120.url
            )

    preview_html.allow_tags = True
    preview_html.short_description = ""


@admin.register(models.Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ("date", "stream", "cover_img", "keyframes_img", "image_counts_html")
    actions = (
        "set_keyframes_action",
        "create_keyframe_thumbnails_action",
        "set_keyframes_and_create_keyframe_thumbnails_action",
        "discover_images_action",
        "discover_images_and_process_action",
    )
    raw_id_fields = ("stream", "cover", "key_frames")
    ordering = ("-date",)
    list_filter = ("stream",)
    date_hierarchy = "date"

    def get_queryset(self, request):
        qs = (
            super(DayAdmin, self)
            .get_queryset(request)
            .select_related("cover")
            .prefetch_related("key_frames")
        )
        return qs

    def set_keyframes_action(self, request, queryset):
        for day in queryset:
            day.set_key_frames()

    def create_keyframe_thumbnails_action(self, request, queryset):
        for day in queryset:
            tasks.create_keyframe_thumbnails_on_day.delay(day_id=smart_text(day.id))

    def set_keyframes_and_create_keyframe_thumbnails_action(self, request, queryset):
        for day in queryset:
            tasks.set_keyframes_on_day.delay(
                day_id=smart_text(day.id), create_thumbnails=True
            )

    def discover_images_action(self, request, queryset):
        for day in queryset:
            tasks.discover_images_on_day.delay(day_id=smart_text(day.id))

    def discover_images_and_process_action(self, request, queryset):
        for day in queryset:
            tasks.discover_images_on_day.delay(
                day_id=smart_text(day.id),
                set_keyframes=True,
                create_keyframe_thumbnails=True,
            )

    def cover_img(self, obj):
        image = obj.cover
        if not image:
            return ""
        if image.scaled_at_160x120:
            img_html = '<img src="{img_src}" style="width: 160px; height: 120px" />'.format(
                img_src=image.scaled_at_160x120.url
            )
        else:
            img_html = '<div style="display: inline-block; border: 1px dashed gray; width: 160px; height: 120px; text-align: center">thumbnail missing</div>'
        if image.original:
            img_html = '<a href="{link}">{img_html}</a>'.format(
                link=image.original.url, img_html=img_html
            )
        return mark_safe(img_html)

    def keyframes_img(self, obj):
        html_list = []
        for image in obj.key_frames.all().order_by("shot_at"):
            if image.scaled_at_160x120:
                html = '<img src="{}" style="width: 160px; height: 120px" />'.format(
                    image.scaled_at_160x120.url
                )
            else:
                html = '<div style="display: inline-block; border: 1px dashed gray; width: 160px; height: 120px; text-align: center">thumbnail missing</div>'
            if image.original:
                html = '<a href="{link}">{img_html}</a>'.format(
                    link=image.original.url, img_html=html
                )
            html_list.append(html)
        return mark_safe("&nbsp;".join(html_list))

    def image_counts_html(self, obj):
        return mark_safe(
            "<br/>".join(
                [
                    "<em>{}</em>: {}".format(key, value)
                    for key, value in sorted(obj.image_counts().items())
                ]
            )
        )

    image_counts_html.short_description = "image counts"


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(models.TagTimerange)
class TagTimerangeAdmin(admin.ModelAdmin):
    list_display = ("tag", "at")
    readonly_fields = ("image_count", "duration")
    raw_id_fields = ("stream", "tag")


class MovieRenderingInline(admin.TabularInline):
    model = models.MovieRendering
    extra = 0
    readonly_fields = ("frame_count", "expected_frame_count", "admin_link")

    def get_queryset(self, request):
        return (
            super().get_queryset(request).annotate(frame_count=models.Count("frames"))
        )

    def frame_count(self, obj):
        return obj.frame_count

    def admin_link(self, obj):
        return '<a target="_blank" href="{}">edit</a>'.format(
            reverse(
                "admin:timelapse_manager_movierendering_change",
                args=("{}".format(obj.pk),),
            )
        )

    admin_link.allow_tags = True
    admin_link.short_description = ""


class MovieAdmin(admin.ModelAdmin):
    list_display = ("name", "tags_display", "image_count")
    readonly_fields = (
        "tags_html",
        "sequence_union_html",
        "realtime_duration",
        "movie_duration",
        "image_count",
    )
    inlines = (MovieRenderingInline,)
    filter_horizontal = ("tags",)

    def tags_html(self, obj):
        return "<br/>".join(
            [
                "{} -> {} {}".format(tag.start_at, tag.end_at, tag.name)
                for tag in obj.tag_instances
            ]
        )

    tags_html.allow_tags = True
    tags_html.short_description = "Tags"

    def sequence_union_html(self, obj):
        return "<br/>".join(
            [
                "{} -> {}".format(start_at, end_at)
                for start_at, end_at in obj.sequence_union
            ]
        )

    sequence_union_html.allow_tags = True
    sequence_union_html.short_description = "Union"


class MovieRenderingAdmin(admin.ModelAdmin):
    actions = ("create_frames_action", "render_action")
    list_display = ("__str__", "size", "frame_count", "expected_frame_count")
    readonly_fields = (
        "expected_frame_count",
        "wanted_frame_timestamps_html",
        "preview_html",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(frame_count=models.Count("frames"))

    def frame_count(self, obj):
        return obj.frame_count

    def wanted_frame_timestamps_html(self, obj):
        timestamps = list(obj.wanted_frame_timestamps)
        html_title = "<strong>{}</strong> frames<br/>".format(len(timestamps))
        html_ts = "<br/>".join(
            ["{}".format(timestamp) for timestamp in obj.wanted_frame_timestamps]
        )
        return html_title + html_ts

    wanted_frame_timestamps_html.allow_tags = True
    wanted_frame_timestamps_html.short_description = "wanted frame timestamps"

    def preview_html(self, obj):
        return """<img src="{}" />""".format(obj.file.url)

    preview_html.allow_tags = True

    def create_frames_action(self, request, queryset):
        for obj in queryset:
            obj.create_frames()

    def render_action(self, request, queryset):
        for obj in queryset:
            tasks.render_movie.delay(movie_rendering_id=str(obj.id))


class FrameAdmin(admin.ModelAdmin):
    list_filter = ("movie_rendering",)
    list_display = ("preview_html", "movie_rendering", "number", "realtime_timestamp")
    actions = ("create_thumbnails_action",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("image")

    def preview_html(self, obj):
        if obj.image.scaled_at_160x120:
            return '<img src="{}" />'.format(obj.image.scaled_at_160x120.url)
        else:
            return '<div style="width: 160px; height: 120px; border: 1px solid gray;"></div>'

    preview_html.allow_tags = True

    def create_thumbnails_action(self, request, queryset):
        for obj in queryset:
            tasks.create_thumbnails_for_image.delay(image_id=str(obj.image_id))
