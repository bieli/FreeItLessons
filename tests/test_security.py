"""Security fixes on top of the Django 6 refactoring (see the "Security" section
of README.md): unpublished content, author HTML, the code runner and headers."""
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase, override_settings

from mainapp.models import Author, Content, Faq, Task, TaskSolution
from mainapp.sandbox import user_run_slot
from mainapp.sanitize import clean_html, safe_url
from tests.test_views import FixturesMixin, SOLUTION_CODE, STARTER_CODE, TESTS_CODE, XHR, b64


class CleanHtmlTest(SimpleTestCase):
    def test_formatting_of_the_course_material_is_kept(self):
        html = ('<p class="lead">Intro <b>bold</b> <i>it</i><br></p><ul><li>one</li></ul>'
                '<pre style="color:red">print(1)</pre>'
                '<table border="1"><tbody><tr><td style="text-align:center" width="50">x</td></tr></tbody></table>'
                '<img src="https://example.com/a.png" width="10" alt="a">')
        self.assertEqual(clean_html(html), html)
        self.assertEqual(clean_html('<p style="text-align: center;">x</p>'), '<p style="text-align:center">x</p>')
        self.assertEqual(clean_html('<a href="https://python.org" target="_blank">py</a>'),
                         '<a href="https://python.org" target="_blank" rel="noopener noreferrer">py</a>')
        self.assertEqual(clean_html('<a href="/mentorzy.html">m</a>'),
                         '<a href="/mentorzy.html" rel="noopener noreferrer">m</a>')

    def test_active_content_is_removed(self):
        cases = {
            '<script>alert(1)</script>ok': 'ok',
            '<img src="x" onerror="alert(1)">': '<img src="x">',
            '<a href="javascript:alert(1)">x</a>': '<a rel="noopener noreferrer">x</a>',
            '<iframe src="https://evil.example"></iframe>ok': 'ok',
            '<form action="https://evil.example"><input name="password"></form>': '',
            '<p style="position: fixed; color: red">x</p>': '<p style="color:red">x</p>',
            '<svg onload="alert(1)"></svg>': '',
        }
        for dirty, clean in cases.items():
            self.assertEqual(clean_html(dirty), clean, dirty)
        self.assertIsNone(clean_html(None))

    def test_safe_url(self):
        for url in ('https://python.org', 'http://example.com/a', '/static/x.png', 'kursy.html',
                    'mailto:mentor@example.com', ''):
            self.assertEqual(safe_url(url), url)
        for url in ('javascript:alert(1)', ' JavaScript:alert(1)', 'java\tscript:alert(1)',
                    'data:text/html,<script>alert(1)</script>', 'vbscript:x'):
            self.assertEqual(safe_url(url), '#', url)


class UnpublishedContentTest(FixturesMixin, TestCase):
    def test_hidden_faq_entries_are_not_shown(self):
        response = self.client.get('/faq.html')
        self.assertEqual([faq['question'] for faq in response.context['faqs_props']['faqs']], ['What is Python'])
        self.assertNotContains(response, 'Draft question')

    def test_hidden_task_is_not_available_to_students(self):
        self.client.force_login(self.student)  # staff account without the "change task" permission
        self.assertEqual(self.client.get('/zadania/%d.html' % self.hidden_task.id).status_code, 404)
        data = {'user_id': self.student.id, 'task_id': self.hidden_task.id}
        response = self.client.post('/zadania/task/code/hint/', dict(data, hint_id=1), **XHR)
        self.assertEqual((response.status_code, response.content), (400, b'task NOT EXISTS'))
        response = self.client.post('/zadania/task/code/run/', dict(data, hint_id=0, timer='00:00:01',
                                                                    code=b64('print(1)')), **XHR)
        self.assertEqual((response.status_code, response.content), (400, b'task NOT EXISTS'))
        self.assertFalse(TaskSolution.objects.filter(task=self.hidden_task).exists())

    def test_authors_can_preview_hidden_task(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get('/zadania/%d.html' % self.hidden_task.id).status_code, 200)


class AuthorHtmlTest(FixturesMixin, TestCase):
    XSS = '<p>Lesson</p><script>alert(1)</script><img src="x" onerror="alert(2)">'

    def test_course_content_is_cleaned(self):
        Content.objects.filter(id=self.text.id).update(value=self.XSS)
        response = self.client.get('/kursy/%d/rozdzial/%d.html' % (self.module.id, self.chapter.id))
        self.assertContains(response, 'data-html="&lt;p&gt;Lesson&lt;/p&gt;&lt;img src=&quot;x&quot;&gt;"')
        self.assertNotContains(response, 'alert(')

    def test_link_contents_and_mentor_links_cannot_run_javascript(self):
        Content.objects.filter(id=self.link.id).update(value='javascript:alert(1)')
        Author.objects.filter(id=self.mentor.id).update(
            blog_link='javascript:alert(2)', image_link='javascript:alert(3)')
        response = self.client.get('/kursy/%d/rozdzial/%d.html' % (self.module.id, self.chapter.id))
        self.assertContains(response, 'href="#" target="_blank" rel="noopener noreferrer"')
        self.assertNotContains(response, 'javascript:')
        response = self.client.get('/mentorzy.html')
        self.assertContains(response, 'href="#" target="_blank" rel="noopener noreferrer">blog</a>')
        self.assertNotContains(response, 'javascript:')

    def test_faq_answers_and_hints_are_cleaned(self):
        Faq.objects.filter(question='What is Python').update(answer='<b>A</b><script>alert(1)</script>')
        response = self.client.get('/faq.html')
        self.assertEqual(response.context['faqs_props']['faqs'][0]['answer'], '<b>A</b>')
        Task.objects.filter(id=self.task.id).update(suggestion_1='<p>hint</p><img src=x onerror=alert(1)>')
        self.client.force_login(self.student)
        response = self.client.post('/zadania/task/code/hint/', {
            'user_id': self.student.id, 'task_id': self.task.id, 'hint_id': 1}, **XHR)
        self.assertEqual(response.content, b'<p>hint</p><img src="x">')


class CodeRunTest(FixturesMixin, TestCase):
    run_url = '/zadania/task/code/run/'
    hint_url = '/zadania/task/code/hint/'

    def setUp(self):
        self.client.force_login(self.student)

    def run_code(self, code, **kw):
        data = {'user_id': self.student.id, 'task_id': self.task.id, 'hint_id': 0, 'timer': '00:01:05',
                'code': b64(code), 'tests': b64(TESTS_CODE)}
        data.update(kw)
        return self.client.post(self.run_url, data, **XHR)

    def assert_not_solved(self, code):
        response = self.run_code(code)
        self.assertIn('SystemExit: the program was stopped before the tests ran', response.content.decode())
        self.assertFalse(TaskSolution.objects.get(task=self.task, user=self.student).is_finished, code)

    def test_exit_before_the_tests_does_not_solve_the_task(self):
        for stop in ('raise SystemExit', 'raise SystemExit(0)',
                     "getattr(__builtins__, '__imp' + 'ort__')('s' + 'ys').exit(0)"):
            self.assert_not_solved(STARTER_CODE + stop + '\n')

    def test_answers_are_plain_text(self):
        response = self.run_code(SOLUTION_CODE + "print('<script>alert(1)</script>')\n")
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')
        response = self.client.post(self.hint_url, {'user_id': self.student.id, 'task_id': self.task.id,
                                                    'hint_id': 1}, **XHR)
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')
        self.assertEqual(self.run_code(SOLUTION_CODE, task_id=999999)['Content-Type'], 'text/plain; charset=utf-8')

    def test_one_program_per_student_at_a_time(self):
        with user_run_slot(self.student.id) as acquired:
            self.assertTrue(acquired)
            response = self.run_code(SOLUTION_CODE)
        self.assertEqual(response.status_code, 429)
        self.assertIn('still running', response.content.decode())
        self.assertFalse(TaskSolution.objects.filter(task=self.task, user=self.student).exists())
        # the slot is free again afterwards
        self.assertEqual(self.run_code(SOLUTION_CODE).status_code, 200)

    @override_settings(CODE_RUN_MAX_CODE_KB=1)
    def test_code_size_is_limited(self):
        self.assertEqual(self.run_code(SOLUTION_CODE + '#' * 1024).status_code, 400)
        self.assertEqual(self.run_code(SOLUTION_CODE + '#' * 800).status_code, 200)

    def test_timer_and_hint_are_validated(self):
        for bad in ({'timer': '-1:00:00'}, {'timer': '00:99:00'}, {'timer': '00:00:-5'},
                    {'timer': '1:2'}, {'hint_id': -1}, {'hint_id': 6}):
            self.assertEqual(self.run_code(SOLUTION_CODE, **bad).status_code, 400, bad)


class SecurityHeadersTest(FixturesMixin, TestCase):
    def test_content_security_policy(self):
        policy = self.client.get('/')['Content-Security-Policy']
        directives = dict(part.strip().split(' ', 1) for part in policy.split(';'))
        self.assertEqual(directives['script-src'], "'self'")
        self.assertEqual(directives['object-src'], "'none'")
        self.assertEqual(directives['frame-ancestors'], "'none'")
        self.client.force_login(self.admin)
        self.assertIn('Content-Security-Policy', self.client.get('/admin/'))

    def test_other_headers(self):
        response = self.client.get('/')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['Referrer-Policy'], 'same-origin')


class FrontendContextTest(TestCase):
    def test_context_has_no_secrets(self):
        self.client.force_login(User.objects.create_user('s', is_staff=True))
        self.assertEqual(set(self.client.get('/').context['frontend_context']),
                         {'isAuthenticated', 'userId', 'username', 'csrfToken', 'staticUrl'})
