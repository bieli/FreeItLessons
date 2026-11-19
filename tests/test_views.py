"""Behaviour tests of the public site, the AJAX endpoints and the admin.

They pin the business behaviour verified by the legacy-vs-new characterization
run (regression/) so it stays protected in the fast CI test suite as well.
"""
import base64
from urllib.parse import urlencode

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

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
        self.assertContains(response, 'Zaloguj się')

    def test_faq(self):
        response = self.client.get('/faq.html')
        self.assertContains(response, 'What is Python')
        self.assertContains(response, '<b>A language</b>')

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
        self.assertContains(response, '<p>Lesson body</p>')
        self.assertContains(response, 'href="https://python.org"')

    def test_mentors_lists_public_mentors_only(self):
        response = self.client.get('/mentorzy.html')
        self.assertContains(response, 'Ada')
        self.assertNotContains(response, 'Hidden')

    def test_tasks_require_login(self):
        response = self.client.get('/zadania.html')
        self.assertEqual(response.status_code, 302)

    def test_static_files_are_served(self):
        response = self.client.get('/static/mainapp/js/jquery.base64.min.js')
        self.assertEqual(response.status_code, 200)


class StudentPagesTest(FixturesMixin, TestCase):
    def setUp(self):
        self.client.force_login(self.student)

    def test_tasks_list_shows_visible_tasks(self):
        response = self.client.get('/zadania.html')
        self.assertContains(response, 'Reverse')
        self.assertNotContains(response, 'Hidden task')

    def test_task_page_lists_asserts(self):
        response = self.client.get('/zadania/%d.html' % self.task.id)
        self.assertContains(response, "assert &#x27;cba&#x27; == reverse_chars(&#x27;abc&#x27;)")

    def test_header_shows_user_menu(self):
        response = self.client.get('/')
        self.assertContains(response, 'Zalogowany <b>student</b>')
        self.assertContains(response, 'name="logged-user-id" value="%d"' % self.student.id)

    def test_logout_is_a_post_form(self):
        response = self.client.get('/')
        self.assertContains(response, '<form id="logout-form" method="post" action="/admin/logout/"')
        self.assertEqual(self.client.post('/admin/logout/').status_code, 200)
        self.assertContains(self.client.get('/'), 'Zaloguj się')

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
        self.assertEqual(self.client.get(self.url, self.params(), **XHR).status_code, 401)
        self.assertEqual(self.client.get(self.read_url, self.params(), **XHR).status_code, 401)

    def test_create_update_and_read_status(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(self.url, self.params(), **XHR).content, b'OK')
        self.assertEqual(self.client.get(self.read_url, self.params(), **XHR).content, b'good')
        self.assertEqual(self.client.get(self.url, self.params(status='HELP'), **XHR).content, b'OK')
        self.assertEqual(self.client.get(self.read_url, self.params(), **XHR).content, b'help')
        self.assertEqual(ContentStatus.objects.filter(user=self.student).count(), 1)

    def test_validation(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(self.url, self.params()).status_code, 400)
        cases = [
            (self.params(status='bogus'), b'status NOT EXISTS'),
            (self.params(content_id=999999), b'content NOT EXISTS'),
            (self.params(user_id=self.other.id), b'wrong auth user in request'),
            (self.params(user_id=999999), b'user NOT EXISTS'),
        ]
        for params, message in cases:
            response = self.client.get(self.url, params, **XHR)
            self.assertEqual((response.status_code, response.content), (400, message))
        response = self.client.get(self.read_url, self.params(content_id=self.link.id), **XHR)
        self.assertEqual((response.status_code, response.content), (400, b'content NOT EXISTS'))


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
        self.client.logout()
        self.assertEqual(self.run_code(SOLUTION_CODE).status_code, 401)

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

    def test_author_admin_sets_owner(self):
        response = self.client.post('/admin/mainapp/author/add/', {
            'name': 'Grace', 'surname': 'Hopper', 'additional_info': 'COBOL'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Author.objects.get(name='Grace').author, self.admin)
