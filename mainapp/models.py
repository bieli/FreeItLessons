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
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.DO_NOTHING)
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
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.DO_NOTHING)
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
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.DO_NOTHING)

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
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.DO_NOTHING)
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
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.DO_NOTHING)
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
    GOOD = 'good'
    DONE = 'done'

    @staticmethod
    def exists(type_name):
        return hasattr(ContentStatusType, str(type_name).upper()) 


CONTENT_STATUS_TYPE_CHOICES = (
    (ContentStatusType.NEW, 'New'),
    (ContentStatusType.DOIT, 'Doit'),
    (ContentStatusType.HELP, 'Help'),
    (ContentStatusType.GOOD, 'Good'),
    (ContentStatusType.DONE, 'Done'),
)

class ContentStatus(models.Model):
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.DO_NOTHING)
    content = models.ForeignKey(Content, null=False, blank=False, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=4,
                              choices=CONTENT_STATUS_TYPE_CHOICES,
                              default=ContentStatusType.NEW)
    created_at = models.DateTimeField(default=django.utils.timezone.now)
    updated_at = AutoDateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return self.status

    @staticmethod
    def get_opinions_by_user_id(user_id):
        q = '''SELECT id, status, COUNT(status) AS status_count 
               FROM mainapp_contentstatus
               WHERE user_id=%s
               GROUP BY status'''
        return ContentStatus.objects.raw(q, [user_id])


class Faq(models.Model):
    question = models.CharField(max_length=128)
    answer = models.TextField(max_length=4000)
    is_visible = models.BooleanField(default=False)
    my_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta(object):
        ordering = ('my_order',)

    def __str__(self):
        return self.question


class Task(models.Model):
    name = models.CharField(max_length=128)
    is_visible = models.BooleanField(default=False)
    desc = models.TextField(max_length=1024)
    intro = models.TextField(max_length=1024, null=True, blank=True)
    code = models.TextField(max_length=4000)
    tests = models.TextField(max_length=4000)
    suggestion_1 = models.TextField(max_length=1024, null=True, blank=True)
    suggestion_2 = models.TextField(max_length=1024, null=True, blank=True)
    suggestion_3 = models.TextField(max_length=1024, null=True, blank=True)
    suggestion_4 = models.TextField(max_length=1024, null=True, blank=True)
    suggestion_5 = models.TextField(max_length=1024, null=True, blank=True)
    level = models.PositiveIntegerField(default=0, blank=False, null=False)
    points = models.PositiveIntegerField(default=5, blank=False, null=False)
    #created_at: datetime
    #created_by: relatet to User
    #reviewd_at: datetime
    #reviewd_by: relatet to User
    my_order = models.PositiveIntegerField(default=1, blank=False, null=False)

    class Meta(object):
        ordering = ('my_order',)

    def __str__(self):
        return "[{}] {}".format(self.id, self.name)


class TaskSolution(models.Model):
    MAX_HINT_NO = 5

    task = models.ForeignKey(Task, null=False, blank=False, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.DO_NOTHING)
    is_finished = models.BooleanField(default=False)
    suggestions_count = models.PositiveIntegerField(default=0, blank=False, null=False)
    solution_code_block = models.TextField(max_length=4000)
    solution_additional_tests_code_block = models.TextField(max_length=4000, blank=False, null=False)
    student_comments = models.TextField(max_length=256, blank=False, null=False)
    is_surrender = models.BooleanField(default=False)
    time_spent_seconds = models.PositiveIntegerField(null=False, default=0)

    @staticmethod
    def save_or_update(task_id, user_id, is_finished, hint_id, time_spent_seconds=1):
        try:
            ts = TaskSolution.objects.filter(task_id__exact=task_id, user_id__exact=user_id).get()
        except Exception as err:
            ts = TaskSolution()
            ts.user_id = int(user_id)
            ts.task_id = int(task_id)

        if hint_id > 0:
            ts.hint_id = hint_id
        if is_finished:
            ts.is_finished = is_finished

        print("ts:", ts)

        if ts:
            ts.time_spent_seconds = time_spent_seconds

            # TODO: what ifthere no record in DB
            print("ts: {}".format(ts))

            if hint_id > 0:
                if hint_id > ts.suggestions_count:
                    ts.suggestions_count = hint_id
                if hint_id == TaskSolution.MAX_HINT_NO:
                    ts.is_surrender = True
                else:
                    ts.is_surrender = False
            else:
                ts.suggestions_count = 0
            ts.save()

    def __str__(self):
        return 'TaskSolution(user_id: {}, task_id: {}, is_finished: {}, time_spent_seconds: {})'\
            .format(self.user_id, self.task_id, self.is_finished, self.time_spent_seconds)
