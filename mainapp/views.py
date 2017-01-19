# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.files.storage import default_storage

from django.db.models.fields.files import FieldFile
from django.views.generic.base import TemplateView

from mainapp.models import Author, Module, Chapter, Content


class FakeField(object):
    storage = default_storage


fieldfile = FieldFile(None, FakeField, 'dummy.txt')


class HomePageView(TemplateView):
    template_name = 'mainapp/home.html'


# def get_context_data(self, **kwargs):
#    context = super(HomePageView, self).get_context_data(**kwargs)
#    messages.info(self.request, 'hello http://example.com')
#    return context

class FaqPageView(TemplateView):
    template_name = 'mainapp/faq.html'


class CoursesListPageView(TemplateView):
    template_name = 'mainapp/courses_list.html'
    id1 = 1

    def get_context_data(self, **kwargs):
        try:
            module_id = kwargs['module_id']
        except KeyError:
            module_id = None

        try:
            chapter_id = kwargs['chapter_id']
        except KeyError:
            chapter_id = None

        modules = []
        contents_list = []
        modules_tmp = Module.objects.select_related().filter(is_enabled=True)
        for module in modules_tmp:
            module.add_chapters([])
            chapters = Chapter.objects.select_related().filter(module__id=module.id)
            if chapter_id is not None:
                for chapter in chapters:
                    if int(chapter.id) == int(chapter_id):
                        module.add_chapter(chapter)
                        contents_list = Content.objects.select_related()\
                            .filter(chapter=chapter).order_by('additional_text')
            else:
                module.add_chapters(chapters)
            module.prepare_icons_list_from_comment()
            if module_id is None or int(module.id) == int(module_id):
                modules.append(module)
        return {'modules': modules,
                'module_id': module_id,
                'chapter_id': chapter_id,
                'contents_list': contents_list}


class MentorsListPageView(TemplateView):
    template_name = 'mainapp/mentors_list.html'

    def get_context_data(self, **kwargs):
        return {'mentors': Author.objects.filter(is_public_mentor=True)}


class CourseDetailPageView(TemplateView):
    template_name = 'mainapp/course_detail.html'

    def get_context_data(self, **kwargs):
        # module_id = kwargs['module_id']
        chapter_id = kwargs['chapter_id']
        contents_id = kwargs['contents_id']
        chapters = []
        chapters_tmp = Chapter.objects.filter(id=chapter_id)
        # chapters_tmp = Chapter.objects.select_related().filter(module__id=module_id)
        for chapter in chapters_tmp:
            print(chapter)
            contents = Content.objects.filter(id=contents_id)
            print(contents)
            chapter.add_contents_list(contents)
            chapters.append(chapter)
        return {'chapters': chapters,
                'chapter_id': chapter_id,
                'contents_id': contents_id}
