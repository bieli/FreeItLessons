"""Behaviour tests of the public site, the AJAX endpoints and the admin.

They pin the business behaviour verified by the legacy-vs-new characterization
run (regression/) so it stays protected in the fast CI test suite as well.
"""
import base64
from urllib.parse import urlencode

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings

from mainapp.models import Author, Chapter, ChapterLevelType, Content, ContentStatus, \
    ContentType, Faq, Module, Task, TaskSolution

XHR = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

TESTS_CODE = """# tests
def __run_tests():
    assert 'cba' == reverse_chars('abc')
    print('ASSERTS TESTS - OK.')
# tests
"""
STARTER_CODE = "# unit\ndef reverse_chars(chars):\n    return chars\n# unit\n"
SOLUTION_CODE = "# unit\ndef reverse_chars(chars):\n    return chars[::-1]\n# unit\n"


def b64(text):
    return base64.b64encode(text.encode('utf-8')).decode('ascii')


class FixturesMixin:
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user('student', password='pass-Student-1', is_staff=True)
        cls.other = User.objects.create_user('other', password='pass-Other-1', is_staff=True)
        cls.admin = User.objects.create_superuser('admin', 'admin@example.com', 'pass-Admin-1')

        cls.mentor = Author.objects.create(name='Ada', surname='Lovelace', additional_info='mentor',
                                           is_public_mentor=True)
        Author.objects.create(name='Hidden', surname='Mentor', additional_info='x')

        cls.text = Content.objects.create(status=ContentType.TEXT, value='<p>Lesson body</p>',
                                          additional_text='A text')
        cls.link = Content.objects.create(status=ContentType.EXTERNAL_LINK, value='https://python.org',
                                          additional_text='B link')
        cls.chapter = Chapter.objects.create(name='Intro chapter', level=ChapterLevelType.BEGINNER,
                                             note='chapter note')
        cls.chapter.contents.add(cls.text, cls.link)
        cls.module = Module.objects.create(title='Python basics', comment='logo-python.png,new.png',
                                           is_enabled=True, achievements_desc='first steps')
        cls.module.contents.add(cls.chapter)
        Module.objects.create(title='Disabled module', is_enabled=False)

        Faq.objects.create(question='What is Python', answer='<b>A language</b>', my_order=1)

        cls.task = Task.objects.create(name='Reverse', desc='Reverse a string', code=STARTER_CODE,
                                       tests=TESTS_CODE, points=10, is_visible=True, my_order=1,
                                       intro='', suggestion_1='<p>use slicing</p>', suggestion_2='two',
                                       suggestion_3='three', suggestion_4='four', suggestion_5='solution')
        cls.hidden_task = Task.objects.create(name='Hidden task', desc='-', code='', tests='',
                                              is_visible=False, my_order=2)


class PublicPagesTest(FixturesMixin, TestCase):
    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['frontend_context']['isAuthenticated'])
        for island in ('NavBar', 'RotatingStatusIcons', 'FloatingBackground'):
            self.assertContains(response, 'data-island="%s"' % island)

    def test_faq(self):
        response = self.client.get('/faq.html')
        self.assertContains(response, 'data-island="FaqAccordion" data-props-id="faq-props"')
        self.assertEqual(response.context['faqs_props']['faqs'],
                         [{'id': 1, 'question': 'What is Python', 'answer': '<b>A language</b>'}])
        # props are embedded with json_script: HTML special characters are escaped
        self.assertContains(response, '\\u003Cb\\u003EA language\\u003C/b\\u003E')

    def test_pages_load_the_react_bundle_and_no_jquery(self):
        for path in ('/', '/faq.html', '/kursy.html', '/kursy/%d/rozdzial/%d.html' % (self.module.id, self.chapter.id),
                     '/mentorzy.html'):
            response = self.client.get(path)
            self.assertContains(response, '<script type="module" src="/static/mainapp/dist/app.js"></script>')
            self.assertContains(response, 'id="frontend-context"')
            self.assertNotContains(response, 'jquery')
            self.assertNotContains(response, 'bootstrap.min.js')

    def test_courses_list_shows_enabled_modules_only(self):
        response = self.client.get('/kursy.html')
        self.assertContains(response, 'Python basics')
        self.assertContains(response, 'Intro chapter')
        self.assertNotContains(response, 'Disabled module')
        self.assertContains(response, 'mainapp/img/logo-python.png')

    def test_module_page(self):
        response = self.client.get('/kursy/%d.html' % self.module.id)
        self.assertContains(response, 'first steps')

    def test_chapter_page_renders_contents(self):
        response = self.client.get('/kursy/%d/rozdzial/%d.html' % (self.module.id, self.chapter.id))
        self.assertContains(response, '<div data-island="ContentBlock" data-content-id="%d">'
                                      '<template><p>Lesson body</p></template></div>' % self.text.id)
        self.assertContains(response, 'href="https://python.org"')

    def test_mentors_lists_public_mentors_only(self):
        response = self.client.get('/mentorzy.html')
        self.assertContains(response, 'Ada')
        self.assertNotContains(response, 'Hidden')

    def test_tasks_require_login(self):
        response = self.client.get('/zadania.html')
        self.assertRedirects(response, '/admin/login/?next=/zadania.html', fetch_redirect_response=False)

    def test_achievements_require_login(self):
        response = self.client.get('/achievements/')
        self.assertRedirects(response, '/admin/login/?next=/achievements/', fetch_redirect_response=False)

    def test_unknown_task_is_404(self):
        self.assertEqual(self.client.get('/zadania/999999.html').status_code, 404)

    def test_source_code_is_not_published_as_static(self):
        for path in ('/static/views.py', '/static/models.py', '/static/templates/mainapp/base.html'):
            self.assertEqual(self.client.get(path).status_code, 404, path)

    def test_static_files_are_served(self):
        response = self.client.get('/static/mainapp/img/new.png')
        self.assertEqual(response.status_code, 200)


class StudentPagesTest(FixturesMixin, TestCase):
    def setUp(self):
        self.client.force_login(self.student)

    def test_tasks_list_shows_visible_tasks(self):
        response = self.client.get('/zadania.html')
        self.assertContains(response, 'Reverse')
        self.assertNotContains(response, 'Hidden task')

    def test_task_page_props(self):
        response = self.client.get('/zadania/%d.html' % self.task.id)
        self.assertContains(response, 'data-island="TaskWorkspace" data-props-id="task-props"')
        self.assertEqual(response.context['task_props'], {
            'taskId': self.task.id, 'code': STARTER_CODE, 'tests': TESTS_CODE,
            'asserts': ["assert 'cba' == reverse_chars('abc')"]})

    def test_frontend_context_of_logged_in_user(self):
        response = self.client.get('/')
        context = response.context['frontend_context']
        self.assertEqual((context['isAuthenticated'], context['userId'], context['username']),
                         (True, self.student.id, 'student'))
        self.assertTrue(context['csrfToken'])
        self.assertEqual(context['staticUrl'], '/static/')

    def test_logout_via_post(self):
        self.assertEqual(self.client.post('/admin/logout/').status_code, 200)
        self.assertFalse(self.client.get('/').context['frontend_context']['isAuthenticated'])

    def test_achievements_and_opinions_pages(self):
        TaskSolution.objects.create(task=self.task, user=self.student, is_finished=True, suggestions_count=2)
        ContentStatus.objects.create(user=self.student, content=self.text, status='good')
        response = self.client.get('/achievements/')
        self.assertEqual(response.context['points_summary'], 8)
        self.assertEqual(response.context['max_points_summary'], 10)
        self.assertEqual(response.context['points_percents'], '80')
        response = self.client.get('/opinions/')
        self.assertContains(response, 'mainapp/img/good.png')


class ContentStatusAjaxTest(FixturesMixin, TestCase):
    url = '/content/user/status/'
    read_url = '/content/user/'

    def params(self, **kw):
        data = {'user_id': self.student.id, 'content_id': self.text.id, 'status': 'good'}
        data.update(kw)
        return data

    def test_anonymous_is_rejected(self):
        self.assertEqual(self.client.post(self.url, self.params(), **XHR).status_code, 401)
        self.assertEqual(self.client.get(self.read_url, self.params(), **XHR).status_code, 401)

    def test_create_update_and_read_status(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.post(self.url, self.params(), **XHR).content, b'OK')
        self.assertEqual(self.client.get(self.read_url, self.params(), **XHR).content, b'good')
        self.assertEqual(self.client.post(self.url, self.params(status='HELP'), **XHR).content, b'OK')
        self.assertEqual(self.client.get(self.read_url, self.params(), **XHR).content, b'help')
        self.assertEqual(ContentStatus.objects.filter(user=self.student).count(), 1)

    def test_validation(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.post(self.url, self.params()).status_code, 400)
        cases = [
            (self.params(status='bogus'), b'status NOT EXISTS'),
            (self.params(content_id=999999), b'content NOT EXISTS'),
            (self.params(content_id='abc'), b'content NOT EXISTS'),
            (self.params(user_id=self.other.id), b'wrong auth user in request'),
            (self.params(user_id=999999), b'user NOT EXISTS'),
            (self.params(user_id='abc'), b'user NOT EXISTS'),
        ]
        for params, message in cases:
            response = self.client.post(self.url, params, **XHR)
            self.assertEqual((response.status_code, response.content), (400, message))
        for content_id in (self.link.id, 999999, 'abc'):
            response = self.client.get(self.read_url, self.params(content_id=content_id), **XHR)
            self.assertEqual((response.status_code, response.content), (400, b'content NOT EXISTS'))

    def test_state_change_requires_post_with_csrf_token(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(self.url, self.params(), **XHR).status_code, 405)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.student)
        self.assertEqual(csrf_client.post(self.url, self.params(), **XHR).status_code, 403)
        csrf_client.get('/kursy/%d/rozdzial/%d.html' % (self.module.id, self.chapter.id))
        token = csrf_client.cookies['csrftoken'].value
        response = csrf_client.post(self.url, self.params(csrfmiddlewaretoken=token), **XHR)
        self.assertEqual(response.content, b'OK')
        self.assertFalse(ContentStatus.objects.filter(status='done').exists())


class TaskAjaxTest(FixturesMixin, TestCase):
    run_url = '/zadania/task/code/run/'
    hint_url = '/zadania/task/code/hint/'

    def setUp(self):
        self.client.force_login(self.student)

    def run_code(self, code, **kw):
        data = {'user_id': self.student.id, 'task_id': self.task.id, 'hint_id': 0, 'timer': '00:01:05',
                'code': b64(code), 'tests': b64(TESTS_CODE)}
        data.update(kw)
        # posted exactly like jQuery.ajax() in task.html does
        return self.client.post(self.run_url, urlencode(data), **XHR,
                                content_type='application/x-www-form-urlencoded; charset=UTF-8')

    def test_correct_solution_finishes_task(self):
        response = self.run_code(SOLUTION_CODE)
        self.assertEqual(response.content.decode().strip(), 'ASSERTS TESTS - OK.')
        solution = TaskSolution.objects.get(task=self.task, user=self.student)
        self.assertTrue(solution.is_finished)
        self.assertEqual(solution.time_spent_seconds, 65)
        self.assertEqual(solution.solution_code_block, SOLUTION_CODE)

    def test_failing_solution_returns_traceback(self):
        response = self.run_code(STARTER_CODE)
        self.assertIn('AssertionError', response.content.decode())
        self.assertIn('program.py', response.content.decode())
        self.assertFalse(TaskSolution.objects.get(task=self.task, user=self.student).is_finished)

    def test_forbidden_instructions_are_not_executed(self):
        response = self.run_code('import os\n' + SOLUTION_CODE)
        self.assertIn('Unexpected instructions', response.content.decode())

    def test_requests_are_validated(self):
        self.assertEqual(self.run_code(SOLUTION_CODE, user_id=self.other.id).status_code, 400)
        for bad in ({'user_id': 'abc'}, {'task_id': 'abc'}, {'task_id': 999999}, {'hint_id': 'x'},
                    {'timer': 'oops'}):
            self.assertEqual(self.run_code(SOLUTION_CODE, **bad).status_code, 400, bad)
        self.client.logout()
        self.assertEqual(self.run_code(SOLUTION_CODE).status_code, 401)

    def test_client_supplied_tests_are_ignored(self):
        fake = "# tests\ndef __run_tests():\n    print('ASSERTS TESTS - OK.')\n# tests\n"
        response = self.run_code(STARTER_CODE, tests=b64(fake))
        self.assertIn('AssertionError', response.content.decode())
        self.assertFalse(TaskSolution.objects.get(task=self.task, user=self.student).is_finished)

    @override_settings(CODE_RUN_TIMEOUT_SECONDS=2)
    def test_infinite_loop_is_stopped(self):
        code = "# unit\ndef reverse_chars(chars):\n    while True:\n        pass\n# unit\n"
        response = self.run_code(code)
        self.assertIn('Time limit exceeded', response.content.decode())
        self.assertFalse(TaskSolution.objects.get(task=self.task, user=self.student).is_finished)

    def test_blacklist_bypass_cannot_run_commands(self):
        code = ("m = getattr(__builtins__, '__imp' + 'ort__')('o' + 's')\n"
                "getattr(m, 'sy' + 'stem')('echo SHELL-' + 'EXECUTED')\n" + SOLUTION_CODE)
        output = self.run_code(code).content.decode()
        self.assertNotIn('SHELL-EXECUTED', output)
        self.assertNotIn('sandbox_bootstrap', output)
        self.assertIn('PermissionError: Operation not allowed in exercises: os.system', output)

    def test_program_cannot_read_server_files_or_secrets(self):
        code = ("print(getattr(__builtins__, 'op' + 'en')('/etc/hostname').read())\n" + SOLUTION_CODE)
        self.assertIn('PermissionError', self.run_code(code).content.decode())
        code = ("m = getattr(__builtins__, '__imp' + 'ort__')('o' + 's')\n"
                "print('ENV:', sorted(getattr(m, 'environ')))\n" + SOLUTION_CODE)
        output = self.run_code(code).content.decode()
        self.assertNotIn('DJANGO_SECRET_KEY', output)

    def test_hints(self):
        data = {'user_id': self.student.id, 'task_id': self.task.id}
        response = self.client.post(self.hint_url, dict(data, hint_id=1), **XHR)
        self.assertEqual(response.content, b'<p>use slicing</p>')
        self.assertEqual(TaskSolution.objects.get(task=self.task, user=self.student).suggestions_count, 1)
        response = self.client.post(self.hint_url, dict(data, hint_id=5), **XHR)
        self.assertEqual(response.content, b'solution')
        self.assertTrue(TaskSolution.objects.get(task=self.task, user=self.student).is_surrender)
        response = self.client.post(self.hint_url, dict(data, hint_id=6), **XHR)
        self.assertEqual(response.status_code, 400)
        for bad in ({'hint_id': 0}, {'hint_id': 'x'}, {'task_id': 999999}):
            self.assertEqual(self.client.post(self.hint_url, dict(data, **bad), **XHR).status_code, 400, bad)


@override_settings(STORAGES={'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class AdminTest(FixturesMixin, TestCase):
    def setUp(self):
        self.client.force_login(self.admin)

    def test_changelists_and_forms(self):
        for model in ('author', 'module', 'chapter', 'content', 'curiosity', 'contentstatus',
                      'faq', 'task', 'tasksolution'):
            self.assertEqual(self.client.get('/admin/mainapp/%s/' % model).status_code, 200, model)
            self.assertEqual(self.client.get('/admin/mainapp/%s/add/' % model).status_code, 200, model)

    def test_content_status_admin_link(self):
        ContentStatus.objects.create(user=self.student, content=self.text, status='done')
        response = self.client.get('/admin/mainapp/contentstatus/')
        self.assertContains(response, '<a href="/admin/mainapp/content/%d/?_to_field=id&amp;_popup=1" '
                                      'target="_blank">A text</a>' % self.text.id, html=True)

    def test_content_status_admin_loads_the_chart_bundle(self):
        response = self.client.get('/admin/mainapp/contentstatus/')
        self.assertContains(response, '<script src="/static/mainapp/dist/admin.js" type="module"></script>')
        self.assertNotContains(response, 'gstatic.com/charts')

    def test_author_admin_sets_owner(self):
        response = self.client.post('/admin/mainapp/author/add/', {
            'name': 'Grace', 'surname': 'Hopper', 'additional_info': 'COBOL'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Author.objects.get(name='Grace').author, self.admin)
