# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import base64
import hashlib
import os
import tempfile

import django
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required

from django.db.models.fields.files import FieldFile
from django.views.generic.base import View, TemplateView
import time

from mainapp.models import User, Author, Module, Chapter, Content, \
    ContentStatusType, ContentStatus, Faq, Task

from django.http import HttpResponse, HttpResponseBadRequest


class FakeField(object):
    storage = default_storage


fieldfile = FieldFile(None, FakeField, 'dummy.txt')


class HomePageView(TemplateView):
    template_name = 'mainapp/home.html'


# def get_context_data(self, **kwargs):
# context = super(HomePageView, self).get_context_data(**kwargs)
#    messages.info(self.request, 'hello http://example.com')
#    return context

class FaqPageView(TemplateView):
    template_name = 'mainapp/faq.html'

    def get_context_data(self, **kwargs):
        faqs_list = Faq.objects.all()
        return {'faqs': faqs_list}


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
                        contents_list = Content.objects.select_related() \
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
            # print(chapter)
            contents = Content.objects.filter(id=contents_id)
            # print(contents)
            chapter.add_contents_list(contents)
            chapters.append(chapter)
        return {'chapters': chapters,
                'chapter_id': chapter_id,
                'contents_id': contents_id}


class TasksPageView(TemplateView):
    template_name = 'mainapp/tasks.html'

    def get_context_data(self, **kwargs):
        tasks = Task.objects.select_related().filter(is_visible=True)
        return {'tasks': tasks}


class TaskPageView(TemplateView):
    template_name = 'mainapp/task.html'

    def get_context_data(self, **kwargs):
        task_id = kwargs['task_id']
        task_instance = Task.objects.filter(id=task_id).get()
        return {'task': task_instance}


class ContetUserStatusView(View):
    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponse(status=401)

        if not request.is_ajax():
            return HttpResponseBadRequest()

        user_id = request.GET.get('user_id', None)
        # print('user_id: {}'.format(user_id))
        content_id = request.GET.get('content_id', None)
        # print('content_id: {}'.format(content_id))
        status = request.GET.get('status', None)
        # print('status: {}'.format(status))

        # print('is_authenticated: {}'.format(request.user.is_authenticated()))
        # print('Raw Data: {}'.format(request.body))
        # print('Raw User Id: {}'.format(request.user.id))
        # print('request.is_ajax(): {}'.format(request.is_ajax()))

        if User.objects.filter(id__iexact=user_id).exists():
            # print('user EXISTS')

            if int(request.user.id) != int(user_id):
                # print('request.user.id != user_id')
                return HttpResponseBadRequest('wrong auth user in request')

            if Content.objects.filter(id__iexact=content_id).exists():
                # print('content EXISTS')
                if ContentStatusType.exists(status):
                    # print('status EXISTS')
                    user_instance = User.objects.filter(id=user_id).get()
                    content_instance = Content.objects.filter(id=content_id).get()

                    obj = ContentStatus.objects.filter(user=user_instance, content=content_instance)
                    if obj:
                        obj.update(status=str(status).lower(), updated_at=django.utils.timezone.now())
                        # print("update")
                    else:
                        obj = ContentStatus(user=user_instance,
                                            content=content_instance,
                                            status=str(status).lower())
                        obj.save()
                        # print("created")

                        #obj, created = ContentStatus.objects.update_or_create(user=user_instance,
                        #                                                      content=content_instance,
                        #                                                      status=str(status).lower())
                        ## print('ContentStatus created: {}'.format(created))
                        #cs.save()
                else:
                    # print('status NOT EXISTS')
                    return HttpResponseBadRequest('status NOT EXISTS')
            else:
                # print('content NOT EXISTS')
                return HttpResponseBadRequest('content NOT EXISTS')
        else:
            # print('user NOT EXISTS')
            return HttpResponseBadRequest('user NOT EXISTS')

        return HttpResponse('OK')


class TaskCodeRunView(View):
    def _security_check(self, result):
        print("result: ", result)
        if 'import ' in result:
            print("AAAAAAa\n\n")
            return False

        if ' loader' in result:
            return False

        # if 'os.' in result:
        #     return False
        #
        # if 'sys.' in result:
        #     return False

        return True

    def _prepare_result(self, result, tmp_filename, replaced_filename='program.py'):
        result = result.decode("utf-8")
        result = result.replace(tmp_filename, replaced_filename)
        # if 'AssertionError' in result and ' assert ' in result:
        #     assert_pos = result.index(' assert ')
        #     result = result[assert_pos:].replace('AssertionError', '').strip()
        return str(result)

    def run_python_code(self, code, task_id, tests, user_id):
        from subprocess import Popen, PIPE
        # cmd = "python3.4 test003.py"
        # p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        # out, err = p.communicate()
        # print("Return code: ", p.returncode)
        # print(out.rstrip(), err.rstrip())
        result = ''
        main = """
# main
if __name__ == '__main__':
    __run_tests()
# main
        """
        hash = hashlib.sha1(bytes(code)).hexdigest()
        tmp_filename = "/tmp/{}-{}-{}-{}".format(user_id, task_id, time.time(), hash)
        # tmp_filename = "{}/tmp/{}-{}-{}-{}".format(settings.STATIC_ROOT, user_id, task_id, time.time(), hash)
        with open(tmp_filename, 'w+') as tmpfile:
            tmpfile.write(code.decode('latin-1'))
            tmpfile.write("\n\n")
            tmpfile.write(tests.decode('latin-1'))
            tmpfile.write("\n\n")
            tmpfile.write(main)
            tmpfile.write("\n\n")
            # tmpfile.write("def __run_tests():\n  print('aaaa from TEMFILE !!!')")
            tmpfile.flush()
            tmpfile.close()


            result = ''
            if not self._security_check(str(code)):
                result = "Unexpected instructions !\nPlease rewrite your code and run again !"
            else:
                try:
                    cmd = "%s %s" % ("/usr/bin/python3.4", tmp_filename)
                    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
                    out, err = p.communicate()
                    print("Return code: ", p.returncode)
                    print(out.rstrip(), err.rstrip())
                    result = out.rstrip() + err.rstrip()
                except:
                    result = 'ERR: 2'

                # try:
                # os.unlink(tmp_filename)
                # except:
                #     pass

                result = self._prepare_result(result, tmp_filename)

        return result

    def post(self, request):
        if not request.user.is_authenticated():
            return HttpResponse(status=401)

        if not request.is_ajax():
            return HttpResponseBadRequest()

        user_id = request.POST.get('user_id', None)
        # print('user_id: {}'.format(user_id))

        if User.objects.filter(id__iexact=user_id).exists():
            # print('user EXISTS')

            if int(request.user.id) != int(user_id):
                # print('request.user.id != user_id')
                return HttpResponseBadRequest('wrong auth user in request')

            content_type = request.META['CONTENT_TYPE'].replace('application/x-www-form-urlencoded; charset=', '')
            # print('content_type: {}'.format(content_type))
            task_id = request.POST.get('task_id', None)
            # print('task_id: {}'.format(task_id))
            codeb64 = request.POST.get('code', None)
            code = base64.decodebytes(bytes(codeb64.encode(content_type)))
            print('code: {}'.format(code))
            testsb64 = request.POST.get('tests', None)
            tests = base64.decodebytes(bytes(testsb64.encode(content_type)))
            print('tests: {}'.format(tests))

            result = self.run_python_code(code, task_id, tests, user_id)
        else:
            # print('user NOT EXISTS')
            return HttpResponseBadRequest('user NOT EXISTS')

        return HttpResponse(result)



class ContetUserView(View):
    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponse(status=401)

        if not request.is_ajax():
            return HttpResponseBadRequest()

        user_id = request.GET.get('user_id', None)
        # print('user_id: {}'.format(user_id))
        content_id = request.GET.get('content_id', None)
        # print('content_id: {}'.format(content_id))

        # print('is_authenticated: {}'.format(request.user.is_authenticated()))
        # print('Raw Data: {}'.format(request.body))
        # print('Raw User Id: {}'.format(request.user.id))
        # print('request.is_ajax(): {}'.format(request.is_ajax()))

        if User.objects.filter(id__iexact=user_id).exists():
            # print('user EXISTS')

            if int(request.user.id) != int(user_id):
                # print('request.user.id != user_id')
                return HttpResponseBadRequest('wrong auth user in request')

            user_instance = User.objects.filter(id=user_id).get()
            content_instance = Content.objects.filter(id=content_id).get()

            obj = ContentStatus.objects.filter(user=user_instance, content=content_instance)
            if obj:
                cs = obj.get()
                # print('content - id {}, data: {}'.format(content_id, cs))
                # print('status: {}'.format(cs.status))
                return HttpResponse(cs.status)
                #return HttpResponse('OK')
            else:
                # print('content NOT EXISTS')
                return HttpResponseBadRequest('content NOT EXISTS')
        else:
            # print('user NOT EXISTS')
            return HttpResponseBadRequest('user NOT EXISTS')


class OpinionsView(TemplateView):
    template_name = 'mainapp/opinions_list.html'

    def get_context_data(self, **kwargs):
        opinions = ContentStatus.get_opinions_by_user_id(self.request.user.id)
        ## print("opinions: {}".format(opinions))
        ## print("opinions.columns: {}".format(opinions.columns))
        #for item in opinions:
        #    # print("status: {}, status_count: {}".format(item.status, item.status_count))
        return {'opinions': opinions}


class LearnerSupportView(TemplateView):
    template_name = 'mainapp/learner_support_list.html'

    def get_context_data(self, **kwargs):
        #items = LearnerSupport.get_all_by_user_id(self.request.user.id)
        items = {}
        # print("items: {}".format(items))
        return {'items': items}


"""
# from django.views.decorators.csrf import csrf_exempt
# import json

class ContetUserStatusAjaxView2(TemplateView):
  template_name = 'mainapp/empty.html'


  def get_context_data(self, **kwargs):
      # print('kwargs: {}'.format(kwargs))

      user_id = kwargs['user_id']
      if User.objects.filter(id__iexact=user_id).exists():
          # print('user EXISTS')
      
          # request.user.is_authenticated():

          content_id = kwargs['content_id']
          if Content.objects.filter(id__iexact=content_id).exists():
              # print('content EXISTS')
              status = kwargs['status']
          else:
              # print('content NOT EXISTS')
      else:
          # print('user NOT EXISTS')

      return {'respons': user_id}


  #def post(self, request):
  #    return HttpResponse(json.dumps({'key': 'value'}), mimetype="application/json")

  # @login_required
  # @csrf_exempt
  def content_user_status(request):
      #return HttpResponse("OK")
      #if not request.user.is_authenticated():
      #    return HttpResponse(status=401)

      user_id = request.GET.get('user_id', None)
      # print('user_id: "%d"' % user_id)

      # print('Raw Data: "%s"' % request.body)

      if request.is_ajax():
          if request.method == 'GET':
              user_id = request.GET.get('user_id', None)

              # print('Raw Data: "%s"' % request.body)
              #if user_id:
              #    if User.objects.filter(userid__iexact=user_id).exists():
              #        cs = ContentStatus(user=user_id, content=content_id, status=selected_status)
              #        cs.save()
              return HttpResponse("OK")

      return HttpResponseBadRequest()

  #def get_context_data(self, **kwargs):
  #    # module_id = kwargs['module_id']
  #    # print(kwargs)
  #    return {'test_results': 123}
"""

