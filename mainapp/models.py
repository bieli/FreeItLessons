import datetime
import django

from django.db import models
from django.contrib.auth.models import User
from django_enumfield import enum


class AutoDateTimeField(models.DateTimeField):
    def pre_save(self, model_instance, add):
        return datetime.datetime.now()

class Author(models.Model):
    name = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)
    optional_email = models.EmailField(unique=True, null=True, blank=True)
    author = models.ForeignKey(User, null=True, blank=True)
    additional_info = models.TextField(max_length=256)
    image_link = models.CharField(max_length=256, null=True, blank=True)
    blog_link = models.CharField(max_length=256, null=True, blank=True)
    linkedin_link = models.CharField(max_length=256, null=True, blank=True)
    external_link = models.CharField(max_length=256, null=True, blank=True)
    is_public_mentor = models.BooleanField(default=False)
    #created_at = models.DateField(default=django.utils.timezone.now)
    #updated_at = AutoDateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return "{} {}".format(self.name, self.surname)


class ContentType(enum.Enum):
    TEXT = 1
    IMAGE = 2
    MOVIE = 3
    EXTERNAL_LINK = 4
    DOWNLOAD_LINK = 5
    NOTE = 6
    FORM = 7

    # _transitions = {
    #     DEAD: (ALIVE,),
    #     REANIMATED: (DEAD,)
    # }


class Content(models.Model):
    status = enum.EnumField(ContentType)
    value = models.TextField(max_length=4000)
    additional_text = models.CharField(max_length=512)
    author = models.ForeignKey(Author, null=True, blank=True)
    #created_at = models.DateField(default=django.utils.timezone.now)
    #updated_at = AutoDateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return self.additional_text

    class Meta:
        ordering = ('additional_text',)


class ChapterLevelType(enum.Enum):
    BEGINNER = 1
    DEVELOPER = 2
    EXPERT = 3


class Curiosity(models.Model):
    title = models.CharField(max_length=128)
    contents = models.ManyToManyField(Content)
    author = models.ForeignKey(Author, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title',)


class Chapter(models.Model):
    contents = models.ManyToManyField(Content)
    name = models.CharField(max_length=128, blank=True)
    sort_order = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    level = enum.EnumField(ChapterLevelType)
    note = models.TextField(max_length=256)
    author = models.ForeignKey(Author, null=True, blank=True)
    #created_at = models.DateField(default=django.utils.timezone.now)
    #updated_at = AutoDateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Module(models.Model):
    contents = models.ManyToManyField(Chapter)
    title = models.CharField(max_length=128)
    comment = models.CharField(max_length=1024, blank=True)
    sort_order = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    author = models.ForeignKey(Author, null=True, blank=True)
    curiosities = models.ManyToManyField(Curiosity)
    achievements_desc = models.CharField(max_length=256, blank=True)
    is_enabled = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0, editable=False)
    finished_count = models.PositiveIntegerField(default=0, editable=False)
    chapters = []
    contents_list = []
    icons_list = []
    #created_at = models.DateField(default=django.utils.timezone.now)
    #updated_at = AutoDateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title',)

    def add_chapters(self, chapters):
        self.chapters = chapters

    def add_chapter(self, chapter):
        self.chapters.append(chapter)

    def add_content(self, content):
        self.contents_list = content

    def add_contents(self, contents):
        self.contents_list.append(contents)

    def prepare_icons_list_from_comment(self):
        self.icons_list = self.comment.split(',')


class ContentStatusType():
    NEW = 'new'
    DOIT = 'doit'
    HELP = 'help'
    DONE = 'done'

    @staticmethod
    def exists(type_name):
        return hasattr(ContentStatusType, str(type_name).upper()) 


CONTENT_STATUS_TYPE_CHOICES = (
    (ContentStatusType.NEW, 'New'),
    (ContentStatusType.DOIT, 'Doit'),
    (ContentStatusType.HELP, 'Help'),
    (ContentStatusType.DONE, 'Done'),
)

class ContentStatus(models.Model):
    user = models.ForeignKey(User, null=False, blank=False)
    content = models.ForeignKey(Content, null=False, blank=False)
    status = models.CharField(max_length=4,
                              choices=CONTENT_STATUS_TYPE_CHOICES,
                              default=ContentStatusType.NEW)
    created_at = models.DateTimeField(default=django.utils.timezone.now)
    updated_at = AutoDateTimeField(default=django.utils.timezone.now)

