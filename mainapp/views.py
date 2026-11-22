import base64
import binascii
import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic.base import View, TemplateView

from mainapp.models import User, Author, Module, Chapter, Content, \
    ContentStatusType, ContentStatus, Faq, Task, TaskSolution
from mainapp.sandbox import run_program, user_run_slot
from mainapp.sanitize import clean_html
from mainapp.utils import TaskCodeRun

logger = logging.getLogger(__name__)

MAIN_BLOCK = """
# main
if __name__ == '__main__':
    __run_tests()
# main
        """
# The browser sends base64 of the UTF-8 encoded program. Payloads that are not
# valid UTF-8 come from the former jQuery page (jquery.base64 sent latin-1 bytes)
# and are decoded the old way, so a page cached in a browser keeps working.
CODE_BLOCK_ENCODING = 'utf-8'
LEGACY_CODE_BLOCK_ENCODING = 'latin-1'


def decode_code_block(raw):
    try:
        return raw.decode(CODE_BLOCK_ENCODING)
    except UnicodeDecodeError:
        return raw.decode(LEGACY_CODE_BLOCK_ENCODING)


# Answers of the AJAX endpoints are plain text (program output, hints, statuses);
# the React UI reads them as text - a browser never renders them as a page.
TEXT_PLAIN = 'text/plain; charset=utf-8'


def text_response(body='', status=200):
    return HttpResponse(body, content_type=TEXT_PLAIN, status=status)


def bad_request(message=''):
    return text_response(message, status=400)


def tasks_visible_to(user):
    """Published tasks; unpublished ones only for the authors who may edit them."""
    tasks = Task.objects.all()
    if not user.has_perm('mainapp.change_task'):
        tasks = tasks.filter(is_visible=True)
    return tasks


def parse_timer(value):
    """``HH:MM:SS`` of the task stopwatch -> seconds (None when malformed)."""
    try:
        hours, minutes, seconds = (int(part) for part in str(value).split(':'))
    except ValueError:
        return None
    if not 0 <= hours <= 9999 or not 0 <= minutes < 60 or not 0 <= seconds < 60:
        return None
    return hours * 3600 + minutes * 60 + seconds


def is_ajax(request):
    """Replacement of ``HttpRequest.is_ajax()`` removed in Django 4.0."""
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class AjaxUserView(View):
    """Common guard of the AJAX endpoints: authenticated XHR request whose
    ``user_id`` parameter is the logged in user (legacy messages kept)."""

    def check_request(self, request, params):
        if not request.user.is_authenticated:
            return text_response(status=401)
        if not is_ajax(request):
            return bad_request()
        user_id = to_int(params.get('user_id'))
        if user_id is None or not User.objects.filter(id=user_id).exists():
            return bad_request('user NOT EXISTS')
        if request.user.id != user_id:
            return bad_request('wrong auth user in request')
        return None


class HomePageView(TemplateView):
    template_name = 'mainapp/home.html'


class FaqPageView(TemplateView):
    template_name = 'mainapp/faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faqs_list = Faq.objects.filter(is_visible=True)
        context.update({'faqs': faqs_list,
                        'faqs_props': {'faqs': [{'id': faq.id, 'question': faq.question,
                                                 'answer': clean_html(faq.answer)}
                                                for faq in faqs_list]}})
        return context


class CoursesListPageView(TemplateView):
    template_name = 'mainapp/courses_list.html'

    def get_context_data(self, **kwargs):
        module_id = kwargs.get('module_id')
        chapter_id = kwargs.get('chapter_id')

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
        context = super().get_context_data(**kwargs)
        context.update({'modules': modules,
                        'module_id': module_id,
                        'chapter_id': chapter_id,
                        'contents_list': contents_list})
        return context


class MentorsListPageView(TemplateView):
    template_name = 'mainapp/mentors_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mentors'] = Author.objects.filter(is_public_mentor=True)
        return context


class TasksPageView(LoginRequiredMixin, TemplateView):
    template_name = 'mainapp/tasks.html'

    def get_context_data(self, **kwargs):
        tasks_data = Task.objects.order_by('my_order').select_related().filter(is_visible=True)
        tasks = []
        for task in tasks_data:
            try:
                task_solution = TaskSolution.objects.get(task_id=task.id, user_id=self.request.user.id)
            except TaskSolution.DoesNotExist:
                task_solution = None

            tasks.append({
                'id': task.id,
                'points': task.points,
                'name': task.name,
                'task_solution': task_solution,
            })
        context = super().get_context_data(**kwargs)
        context['tasks'] = tasks
        return context


class TaskPageView(TemplateView):
    template_name = 'mainapp/task.html'

    def _get_asserts_from_tests_code(self, tests_code):
        asserts = []
        for assert_line in str(tests_code).split("\n"):
            if 'assert ' in assert_line:
                asserts.append(assert_line.strip())
        return asserts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_instance = get_object_or_404(tasks_visible_to(self.request.user), id=kwargs['task_id'])
        asserts = self._get_asserts_from_tests_code(task_instance.tests)
        context.update({'task': task_instance,
                        'asserts': asserts,
                        'task_props': {'taskId': task_instance.id, 'code': task_instance.code,
                                       'tests': task_instance.tests, 'asserts': asserts}})
        return context


class ContetUserStatusView(AjaxUserView):
    """Stores the student's opinion about a course content (state change: POST + CSRF)."""

    def post(self, request):
        error = self.check_request(request, request.POST)
        if error:
            return error

        content_id = to_int(request.POST.get('content_id'))
        status = request.POST.get('status', None)

        content_instance = Content.objects.filter(id=content_id).first() if content_id else None
        if content_instance is None:
            return bad_request('content NOT EXISTS')
        if not ContentStatusType.exists(status):
            return bad_request('status NOT EXISTS')

        status = str(status).lower()
        obj = ContentStatus.objects.filter(user=request.user, content=content_instance)
        if obj:
            obj.update(status=status, updated_at=timezone.now())
        else:
            ContentStatus.objects.create(user=request.user, content=content_instance, status=status)
        return text_response('OK')


class TaskCodeRunView(AjaxUserView):
    TIMEOUT_MESSAGE = "Time limit exceeded !\nPlease check your code (infinite loop ?) and run again !"
    BUSY_MESSAGE = "Your previous program is still running !\nPlease wait for its result and run again !"

    def _prepare_result(self, result, tmp_filename, replaced_filename='program.py'):
        result = result.decode("utf-8", errors="replace")
        return result.replace(tmp_filename, replaced_filename)

    def run_python_code(self, code, task, user_id):
        """``code`` are the bytes sent by the browser; the tests ALWAYS come
        from the database - client supplied tests are never executed."""
        code_text = decode_code_block(code)
        if not TaskCodeRun.is_code_block_secure(code_text):
            return "Unexpected instructions !\nPlease rewrite your code and run again !", -1

        source = code_text + "\n\n" + task.tests + "\n\n" + MAIN_BLOCK + "\n\n"
        run = run_program(source)
        if run.timed_out:
            logger.warning('code run timed out: user=%s task=%s', user_id, task.id)
            return self.TIMEOUT_MESSAGE, -1

        result = self._prepare_result(run.stdout.rstrip() + run.stderr.rstrip(), run.program_path)
        if run.returncode == 0:
            ts_obj, created = TaskSolution.objects.update_or_create(user_id=user_id, task=task)
            ts_obj.solution_code_block = code_text
            ts_obj.save()
        return result, run.returncode

    def post(self, request):
        error = self.check_request(request, request.POST)
        if error:
            return error

        task = tasks_visible_to(request.user).filter(id=to_int(request.POST.get('task_id')) or 0).first()
        if task is None:
            return bad_request('task NOT EXISTS')
        hint_id = to_int(request.POST.get('hint_id', 0))
        if hint_id is None or not 0 <= hint_id <= TaskSolution.MAX_HINT_NO:
            return bad_request('wrong hint_id')
        encoded = request.POST.get('code', '')
        if len(encoded) > (settings.CODE_RUN_MAX_CODE_KB * 1024 + 2) // 3 * 4:
            return bad_request('code too long')
        try:
            code = base64.b64decode(encoded.encode('ascii'), validate=False)
        except (binascii.Error, UnicodeEncodeError):
            return bad_request('wrong code')
        time_spent_seconds = parse_timer(request.POST.get('timer', ''))
        if time_spent_seconds is None:
            return bad_request('wrong timer')

        # one program per student at a time: the runs of a single account
        # cannot occupy all the server workers
        with user_run_slot(request.user.id) as acquired:
            if not acquired:
                return text_response(self.BUSY_MESSAGE, status=429)
            result, returncode = self.run_python_code(code, task, request.user.id)
        is_finished = returncode == 0
        TaskSolution.save_or_update(task.id, request.user.id, is_finished, hint_id,
                                    time_spent_seconds=time_spent_seconds)
        return text_response(result)


class TaskCodeHintView(AjaxUserView):
    def post(self, request):
        error = self.check_request(request, request.POST)
        if error:
            return error

        task = tasks_visible_to(request.user).filter(id=to_int(request.POST.get('task_id')) or 0).first()
        if task is None:
            return bad_request('task NOT EXISTS')
        hint_id = to_int(request.POST.get('hint_id', 0))
        if hint_id is None or hint_id < 1:
            return bad_request('Unexpected hint_id !')
        if hint_id > TaskSolution.MAX_HINT_NO:
            return bad_request('Unexpected (too high) hint_id !')

        result = clean_html(getattr(task, 'suggestion_%d' % hint_id))
        TaskSolution.save_or_update(task.id, request.user.id, False, hint_id)
        return text_response(result)


class ContetUserView(AjaxUserView):
    def get(self, request):
        error = self.check_request(request, request.GET)
        if error:
            return error

        content_id = to_int(request.GET.get('content_id'))
        cs = ContentStatus.objects.filter(user=request.user, content_id=content_id).first()
        if cs is None:
            return bad_request('content NOT EXISTS')
        return text_response(cs.status)


class OpinionsView(TemplateView):
    template_name = 'mainapp/opinions_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['opinions'] = ContentStatus.get_opinions_by_user_id(self.request.user.id)
        return context


ACHIEVEMENT_QUERY = """
    SELECT
        ts.id as id,
        t.name as task_name,
        ts.user_id as user_id,
        SUM(t.points - ts.suggestions_count) as summary,
        t.points as max_points,
        ts.suggestions_count,
        ts.task_id as task_id,
        ts.is_finished as is_finished
    FROM mainapp_tasksolution as ts
    JOIN mainapp_task as t
    ON (t.id = ts.task_id)
    WHERE ts.user_id = %s AND ts.task_id = %s
"""


class AchievementsView(LoginRequiredMixin, TemplateView):
    template_name = 'mainapp/achievements_list.html'

    def get_context_data(self, **kwargs):
        tasks_achievements = []
        tasks = Task.objects.order_by('my_order').select_related().filter(is_visible=True)
        points_summary = 0
        max_points_summary = 0

        for task in tasks:
            achievements = TaskSolution.objects.raw(ACHIEVEMENT_QUERY, [self.request.user.id, task.id])
            summary = achievements[0].summary if achievements[0].is_finished else 0
            if summary is None:
                continue
            tasks_achievements.append({
                "task_id": task.id,
                "summary": summary,
                "is_finished": achievements[0].is_finished,
                "task_name": achievements[0].task_name,
                "max_points": achievements[0].max_points
            })
            points_summary += summary
            if achievements[0].max_points is not None:
                max_points_summary += achievements[0].max_points
        context = super().get_context_data(**kwargs)
        context.update({'tasks_achievements': tasks_achievements,
                        "points_summary": points_summary,
                        "max_points_summary": max_points_summary,
                        "points_percents": "%d" % (self._calc_summary(points_summary, max_points_summary))})
        return context

    def _calc_summary(self, points_summary, max_points_summary):
        try:
            return (points_summary / max_points_summary) * 100
        except ZeroDivisionError:
            return 0


class LearnerSupportView(TemplateView):
    template_name = 'mainapp/learner_support_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = {}
        return context
