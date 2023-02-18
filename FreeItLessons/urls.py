"""FreeItLessons URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from mainapp.views import HomePageView, FaqPageView, CoursesListPageView,\
                          MentorsListPageView, \
                          ContetUserStatusView, ContetUserView, OpinionsView, \
                          LearnerSupportView, TasksPageView, TaskPageView, \
                          TaskCodeRunView, TaskCodeHintView, AchievementsView


urlpatterns = [
    url(r'^$',
        HomePageView.as_view(), name='home'),
    url(r'^faq\.html$',
        FaqPageView.as_view(), name='faq'),
    url(r'^kursy\.html$',
        CoursesListPageView.as_view(), name='courses_list'),
    url(r'^kursy/(?P<module_id>[0-9]+)\.html$',
        CoursesListPageView.as_view(), name='courses_list'),
    url(r'^kursy/(?P<module_id>[0-9]+)/rozdzial/(?P<chapter_id>[0-9]+)\.html$',
        CoursesListPageView.as_view(), name='course_detail'),
    url(r'^mentorzy\.html$',
        MentorsListPageView.as_view(), name='mentors_list'),
    url(r'^zadania\.html$',
        TasksPageView.as_view(), name='tasks_list'),
    url(r'^zadania/(?P<task_id>[0-9]+)\.html$',
        TaskPageView.as_view(), name='task_detail'),
    url(r'^admin/',
        include(admin.site.urls)),
    url(r'^content/user/status/$',
        ContetUserStatusView.as_view()),
    url(r'^content/user/$',
        ContetUserView.as_view()),
    url(r'^opinions/$',
        OpinionsView.as_view(), name="opinions_list"),
    url(r'^achievements/$',
        AchievementsView.as_view(), name="achievements_list"),
    url(r'^learner-support/$',
        LearnerSupportView.as_view(), name="learner_support_list"),
    url(r'^zadania/task/code/run/$',
        TaskCodeRunView.as_view()),
    url(r'^zadania/task/code/hint/$',
        TaskCodeHintView.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
