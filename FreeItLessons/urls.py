"""FreeItLessons URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/stable/topics/http/urls/

The legacy (regex based) URLs are kept 1:1 - they are part of the public
interface (bookmarks, links inside course contents, AJAX calls in templates).
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import re_path

from mainapp.views import HomePageView, FaqPageView, CoursesListPageView, \
    MentorsListPageView, \
    ContetUserStatusView, ContetUserView, OpinionsView, \
    LearnerSupportView, TasksPageView, TaskPageView, \
    TaskCodeRunView, TaskCodeHintView, AchievementsView


urlpatterns = [
    re_path(r'^$',
            HomePageView.as_view(), name='home'),
    re_path(r'^faq\.html$',
            FaqPageView.as_view(), name='faq'),
    re_path(r'^kursy\.html$',
            CoursesListPageView.as_view(), name='courses_list'),
    re_path(r'^kursy/(?P<module_id>[0-9]+)\.html$',
            CoursesListPageView.as_view(), name='courses_list'),
    re_path(r'^kursy/(?P<module_id>[0-9]+)/rozdzial/(?P<chapter_id>[0-9]+)\.html$',
            CoursesListPageView.as_view(), name='course_detail'),
    re_path(r'^mentorzy\.html$',
            MentorsListPageView.as_view(), name='mentors_list'),
    re_path(r'^zadania\.html$',
            TasksPageView.as_view(), name='tasks_list'),
    re_path(r'^zadania/(?P<task_id>[0-9]+)\.html$',
            TaskPageView.as_view(), name='task_detail'),
    re_path(r'^admin/',
            admin.site.urls),
    re_path(r'^content/user/status/$',
            ContetUserStatusView.as_view()),
    re_path(r'^content/user/$',
            ContetUserView.as_view()),
    re_path(r'^opinions/$',
            OpinionsView.as_view(), name="opinions_list"),
    re_path(r'^achievements/$',
            AchievementsView.as_view(), name="achievements_list"),
    re_path(r'^learner-support/$',
            LearnerSupportView.as_view(), name="learner_support_list"),
    re_path(r'^zadania/task/code/run/$',
            TaskCodeRunView.as_view()),
    re_path(r'^zadania/task/code/hint/$',
            TaskCodeHintView.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
