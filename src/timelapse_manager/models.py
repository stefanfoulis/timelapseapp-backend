import datetime
import uuid

from django.contrib.postgres.fields import DateTimeRangeField
from functools import partial

from django.db import models
from django.db.models import Q, QuerySet

from timelapse_manager.storage import dsn_setting_configured_storage

from . import storage


class UUIDAuditedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CameraController(UUIDAuditedModel):
    """
    A unit that manages Cameras, like a RaspberryPi, iOS or Android device.
    It registers itself and can provide multiple cameras to the system.
    """

    name = models.CharField(blank=True, default="", max_length=255)
    notes = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.name}"


class Camera(UUIDAuditedModel):
    controller = models.ForeignKey(
        "CameraController", related_name="cameras", on_delete=models.CASCADE
    )
    name = models.CharField(blank=True, default="", max_length=255)
    notes = models.TextField(blank=True, default="")

    active_image_stream = models.ForeignKey(
        "Stream", blank=True, null=True, default=None, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.name}"


class Stream(UUIDAuditedModel):
    """
    Holds a Stream of Images together and usually represents a location and
    perspective from which images are created.
    This is separate from Camera because cameras may move around or be
    re-purposed for different Streams over time.
    """

    name = models.CharField(blank=True, default="", max_length=255)
    notes = models.TextField(blank=True, default="")
    location = models.TextField(blank=True, default="")

    cover_image = models.ForeignKey(
        "Image",
        null=True,
        default=None,
        blank=True,
        related_name="cover_of_streams",
        on_delete=models.SET_NULL,
    )

    auto_resize_original = models.BooleanField(
        default=False,
        help_text=(
            "if enabled, every original image submitted through the image"
            "intake will automatically be resized."
        ),
    )

    def __str__(self):
        return f"{self.name}"

    def create_days(self):
        created_days = []
        for date in self.images.all().dates("shot_at", "day"):
            day, created = Day.objects.get_or_create(stream=self, date=date)
            if created:
                created_days.append(day)
        return created_days

    def discover_images(self):
        from . import actions

        actions.discover_images(limit_cameras=[self])


class ImageManager(QuerySet):
    def with_missing_thumbnails(self, camera=None):
        qs = self.filter(original__isnull=False)
        if camera:
            qs = qs.filter(camera=camera)
        qs = qs.filter(
            (
                Q(scaled_at_160x120="")
                | Q(scaled_at_320x240="")
                | Q(scaled_at_640x480="")
            )
        )
        return qs

    def create_missing_thumbnails(self, camera=None):
        for img in self.with_missing_thumbnails(camera=camera).iterator():
            img.create_thumbnails()

    def with_faulty_scaled_filenames(self):
        return self.filter(
            Q(scaled_at_160x120__icontains=".original.")
            | Q(scaled_at_160x120__icontains=".JPG.")
            | Q(scaled_at_320x240__icontains=".original.")
            | Q(scaled_at_320x240__icontains=".JPG.")
            | Q(scaled_at_640x480__icontains=".original.")
            | Q(scaled_at_640x480__icontains=".JPG.")
        )

    def pick_closest(self, stream, shot_at, max_difference=None):
        """
        Picks closes available image. Raises DoesNotExists if no image is
        found within the range.
        This naïve implementation only looks forwards from the given shot_at
        datetime. A better version would also look into the past.
        """
        qs = self.filter(stream=stream, shot_at__gte=shot_at)
        if max_difference:
            qs = qs.filter(shot_at__lte=shot_at + max_difference)
        return qs.first()

    def create_or_update_from_url(self, url):
        from . import actions

        return actions.create_or_update_image_from_url(url=url)

    def create_or_update_images_from_urls(self, urls):
        from . import actions

        return actions.create_or_update_images_from_urls(urls=urls)


class Image(UUIDAuditedModel):
    sizes = ("640x480", "320x240", "160x120")
    SIZE_CHOICES = [(size, size) for size in sizes]
    stream = models.ForeignKey(Stream, related_name="images", on_delete=models.PROTECT)
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    shot_at = models.DateTimeField(null=True, blank=True, default=None, db_index=True)
    original = models.ImageField(
        null=True,
        blank=True,
        default="",
        max_length=255,
        db_index=True,
        storage=dsn_setting_configured_storage("TIMELAPSE_STORAGE_DSN"),
    )
    original_md5 = models.CharField(
        max_length=32, blank=True, default="", db_index=True
    )
    scaled_at_160x120 = models.ImageField(
        null=True,
        blank=True,
        default="",
        max_length=255,
        db_index=True,
        storage=dsn_setting_configured_storage("TIMELAPSE_STORAGE_DSN"),
        upload_to=partial(storage.upload_to_image, size="160x120"),
    )
    scaled_at_160x120_md5 = models.CharField(
        max_length=32, blank=True, default="", db_index=True
    )
    scaled_at_320x240 = models.ImageField(
        null=True,
        blank=True,
        default="",
        max_length=255,
        db_index=True,
        storage=dsn_setting_configured_storage("TIMELAPSE_STORAGE_DSN"),
        upload_to=partial(storage.upload_to_image, size="320x240"),
    )
    scaled_at_320x240_md5 = models.CharField(
        max_length=32, blank=True, default="", db_index=True
    )
    scaled_at_640x480 = models.ImageField(
        null=True,
        blank=True,
        default="",
        max_length=255,
        db_index=True,
        storage=dsn_setting_configured_storage("TIMELAPSE_STORAGE_DSN"),
        upload_to=partial(storage.upload_to_image, size="640x480"),
    )
    scaled_at_640x480_md5 = models.CharField(
        max_length=32, blank=True, default="", db_index=True
    )

    objects = ImageManager.as_manager()

    class Meta:
        unique_together = (("stream", "shot_at"),)
        ordering = ("shot_at",)

    def __str__(self):
        return self.original.name

    def create_thumbnails(self, force=False):
        from . import actions

        actions.create_thumbnails(self, force=force)
        self.save()

    @property
    def tags(self):
        return Tag.objects.filter(
            camera=self.camera, start_at__lte=self.shot_at, end_at__gte=self.shot_at
        )

    def get_file_for_size(self, size):
        if size == "original":
            return self.original or None
        assert size in ["160x120", "320x240", "640x480"]
        if not getattr(self, "scaled_at_{}".format(size)):
            if self.original:
                self.create_thumbnails()
            else:
                return None
        return getattr(self, "scaled_at_{}".format(size))


class TagTimerange(UUIDAuditedModel):
    stream = models.ForeignKey(Stream, related_name="tag_timeranges", on_delete=models.PROTECT)
    tag = models.ForeignKey("Tag", related_name="tag_timeranges", on_delete=models.PROTECT)
    at = DateTimeRangeField()

    class Meta:
        ordering = ("at",)

    def __str__(self):
        return f"{self.tag.name} ({self.at.lower} - {self.at.upper})"

    @property
    def images(self):
        return Image.objects.filter(
            stream=self.stream, shot_at__contained_by=self.at
        )

    @property
    def duration(self):
        if not (self.at and self.at.lower and self.at.upper):
            return None
        return self.at.upper - self.at.lower

    @property
    def image_count(self):
        return self.images.count()

    def get_q(self, fieldname):
        return Q(
            **{
                "{}__gte".format(fieldname): self.start_at,
                "{}__lte".format(fieldname): self.end_at,
            }
        )


class Tag(UUIDAuditedModel):
    name = models.CharField(max_length=255, unique=True, default="")
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name


class DayManager(QuerySet):
    def create_keyframe_thumbnails(self, force=False):
        for day in self:
            day.create_keyframe_thumbnails(force=force)


def create_for_range(self, stream, start_on, end_on=None):
    if end_on is None:
        end_on = start_on
    current_day = start_on
    while current_day <= end_on:
        self.get_or_create(stream=stream, date=current_day)
        current_day = current_day + datetime.timedelta(days=1)


class Day(UUIDAuditedModel):
    stream = models.ForeignKey(Stream, related_name="days", on_delete=models.PROTECT)
    date = models.DateField(db_index=True)
    cover = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        related_name="cover_for_days",
        on_delete=models.PROTECT,
    )
    key_frames = models.ManyToManyField(
        Image, blank=True, related_name="keyframe_for_days"
    )

    objects = DayManager.as_manager()

    class Meta:
        ordering = ("date",)
        unique_together = ("stream", "date")

    def __str__(self):
        return f"{self.date}"

    @property
    def images(self):
        return Image.objects.filter(stream_id=self.stream_id, shot_at__date=self.date)

    @property
    def image_count(self):
        return self.images.count()

    def image_counts(self):
        return self.images.aggregate(
            original=models.Count("original", distinct=True),
            scaled_at_160x120=models.Count("scaled_at_160x120", distinct=True),
            scaled_at_320x240=models.Count("scaled_at_320x240", distinct=True),
            scaled_at_640x480=models.Count("scaled_at_640x480", distinct=True),
        )

    def set_key_frames(self):
        from . import actions

        actions.set_keyframes_for_day(self)

    def create_keyframe_thumbnails(self, force=False):
        print("creating thumbnails for {}".format(self))
        if self.cover:
            self.cover.create_thumbnails(force=force)
        for key_frame in self.key_frames.all():
            key_frame.create_thumbnails(force=force)

    def discover_images(self):
        from . import actions

        actions.discover_images_on_day(steam=self.stream, day_name=str(self.date))


class VideoClip(UUIDAuditedModel):
    stream = models.ForeignKey(Stream, related_name="video_clips", on_delete=models.PROTECT)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, default=None)

    speed_factor = models.FloatField(default=4000.0)
    tags = models.ManyToManyField(Tag, related_name="video_clips", blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    @property
    def tag_timeranges(self):
        return TagTimerange.objects.filter(tag__in=self.tags.all())

    @property
    def sequence_union(self):
        # adapted from http://stackoverflow.com/a/15273749/245810
        ranges = self.tag_timeranges.values_list("start_at", "end_at")
        union = []
        for begin, end in sorted(ranges):
            # TODO: make sure not using ">= begin-1" is ok
            if union and union[-1][1] >= begin:
                union[-1] = (min(union[-1][0], begin), max(union[-1][1], end))
            else:
                union.append((begin, end))
        return union

    @property
    def realtime_duration(self):
        duration = datetime.timedelta(0)
        for start_at, end_at in self.sequence_union:
            duration += end_at - start_at
        return duration

    @property
    def movie_duration(self):
        return self.realtime_duration / self.speed_factor

    @property
    def images(self):
        union_ranges = self.sequence_union
        qs = Image.objects.filter(stream=self.stream)
        q = Q(name__isnull=True)  # it is always false
        for start_at, end_at in union_ranges:
            q = q | Q(shot_at__gte=start_at, shot_at__lte=end_at)
        return qs.filter(q).distinct()

    @property
    def tags_display(self):
        return ", ".join(
            [
                "{} ({} -> {})".format(tag.name, tag.at.lower, tag.at.upper)
                for tag in self.tags.all()
            ]
        )

    @property
    def image_count(self):
        return self.images.count()


class Movie(UUIDAuditedModel):
    name = models.CharField(max_length=255, default='', blank=True)


class MovieRendering(UUIDAuditedModel):
    movie = models.ForeignKey(
        Movie, related_name="renderings", on_delete=models.PROTECT
    )
    size = models.CharField(
        max_length=32,
        choices=[(imgsize, imgsize) for imgsize in Image.sizes],
        default="160x120",
    )
    fps = models.FloatField(default=15.0)
    format = models.CharField(default="mp4", max_length=255)
    file = models.FileField(
        null=True,
        blank=True,
        default="",
        max_length=255,
        db_index=True,
        storage=dsn_setting_configured_storage("TIMELAPSE_STORAGE_DSN"),
        upload_to=storage.upload_to_movie_rendering,
    )
    file_md5 = models.CharField(max_length=32, blank=True, default="", db_index=True)

    def __str__(self):
        return "{}: {} {}fps".format(self.movie, self.format, self.fps)

    @property
    def expected_frame_count(self):
        movie_duration = self.movie.movie_duration
        fps = self.fps
        return movie_duration.total_seconds() * fps

    @property
    def wanted_frame_timestamps(self):
        for start_at, end_at in self.movie.sequence_union:
            realtime_duration = (end_at - start_at).total_seconds()
            target_duration = realtime_duration / self.movie.speed_factor
            wanted_image_count = target_duration * self.fps
            wanted_image_every_realtime_seconds = realtime_duration / wanted_image_count
            current_timestamp = start_at
            while current_timestamp <= end_at:
                yield current_timestamp
                current_timestamp += datetime.timedelta(
                    seconds=wanted_image_every_realtime_seconds
                )

    def create_frames(self):
        from . import actions

        return actions.create_frames_for_movie_rendering(movie_rendering=self)

    def render(self):
        from . import actions

        return actions.render_movie(movie_rendering=self)


class Frame(UUIDAuditedModel):
    movie_rendering = models.ForeignKey(
        MovieRendering, related_name="frames", on_delete=models.PROTECT
    )
    number = models.PositiveIntegerField()
    realtime_timestamp = models.DateTimeField()
    image = models.ForeignKey(
        Image, related_name="frames", null=True, blank=True, on_delete=models.PROTECT
    )

    class Meta:
        ordering = ("movie_rendering", "number")

    def pick_image(self):
        self.image = Image.objects.pick_closest(
            stream=self.movie_rendering.movie.stream,
            shot_at=self.realtime_timestamp,
            max_difference=datetime.timedelta(hours=1),
        )
