"""Login throttling (django-axes, mainapp/login_throttling.py): the (username, IP)
pair is locked out after AXES_FAILURE_LIMIT wrong passwords for AXES_COOLOFF_TIME."""
from datetime import timedelta

from axes.models import AccessAttempt, AccessLog
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone

from mainapp.login_throttling import client_ip

LOGIN_URL = '/admin/login/?next=/'
PASSWORD = 'pass-Student-1'
CLASSROOM_IP = '203.0.113.10'
HOME_IP = '198.51.100.20'


@override_settings(AXES_FAILURE_LIMIT=5, AXES_COOLOFF_TIME=timedelta(minutes=15))
class LoginThrottlingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user('student', password=PASSWORD, is_staff=True)
        cls.classmate = User.objects.create_user('classmate', password=PASSWORD, is_staff=True)

    def login(self, username, password, ip=CLASSROOM_IP, **extra):
        self.client.logout()
        return self.client.post(LOGIN_URL, {'username': username, 'password': password, 'next': '/'},
                                REMOTE_ADDR=ip, **extra)

    def fail(self, username, times, ip=CLASSROOM_IP):
        """``times`` wrong passwords: the login form again, the 5th one is locked out."""
        for attempt in range(1, times + 1):
            expected = 429 if attempt >= 5 else 200
            self.assertEqual(self.login(username, 'wrong-password', ip).status_code, expected, attempt)

    def assert_locked(self, response):
        self.assertEqual(response.status_code, 429)
        self.assertContains(response, 'Logowanie chwilowo zablokowane', status_code=429)
        self.assertContains(response, 'na 15 min', status_code=429)

    def assert_logged_in(self, response):
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_correct_login_works(self):
        self.assert_logged_in(self.login('student', PASSWORD))

    def test_lockout_at_the_fifth_wrong_password_even_with_the_right_one(self):
        self.fail('student', 4)
        self.assert_logged_in(self.login('student', PASSWORD))  # 4 failures: still allowed
        self.client.logout()
        self.fail('student', 5)
        self.assert_locked(self.login('student', PASSWORD))
        self.assert_locked(self.login('student', 'wrong-password'))

    def test_lockout_is_per_username_and_ip_pair(self):
        self.fail('student', 5)
        self.assert_locked(self.login('student', PASSWORD))
        # a classmate behind the same school IP address can still log in
        self.assert_logged_in(self.login('classmate', PASSWORD))
        # the student can still log in from another place
        self.assert_logged_in(self.login('student', PASSWORD, ip=HOME_IP))

    def test_unknown_usernames_are_throttled_too(self):
        self.fail('no-such-user', 5)
        self.assert_locked(self.login('no-such-user', 'anything'))

    def test_successful_login_resets_the_counter(self):
        self.fail('student', 4)
        self.assert_logged_in(self.login('student', PASSWORD))
        self.fail('student', 4)
        self.assert_logged_in(self.login('student', PASSWORD))

    def test_lockout_ends_after_the_cool_off_time(self):
        self.fail('student', 5)
        self.assert_locked(self.login('student', PASSWORD))
        AccessAttempt.objects.update(attempt_time=timezone.now() - timedelta(minutes=16))
        self.assert_logged_in(self.login('student', PASSWORD))

    def test_successful_logins_are_not_logged(self):
        self.assert_logged_in(self.login('student', PASSWORD))
        self.assertFalse(AccessLog.objects.exists())

    @override_settings(BEHIND_TLS_PROXY=True)
    def test_forged_forwarded_for_does_not_escape_the_lockout(self):
        # the proxy appends the real address; the earlier entries come from the client
        for attempt, forged in enumerate(('1.1.1.1', '2.2.2.2', '3.3.3.3', '4.4.4.4', '5.5.5.5'), 1):
            response = self.login('student', 'wrong-password', ip='10.0.0.2',
                                  HTTP_X_FORWARDED_FOR='%s, %s' % (forged, CLASSROOM_IP))
            self.assertEqual(response.status_code, 429 if attempt == 5 else 200)
        self.assert_locked(self.login('student', PASSWORD, ip='10.0.0.2',
                                      HTTP_X_FORWARDED_FOR='9.9.9.9, %s' % CLASSROOM_IP))


class ClientIpTest(TestCase):
    def request(self, **meta):
        return RequestFactory().get('/', REMOTE_ADDR='10.0.0.2', **meta)

    @override_settings(BEHIND_TLS_PROXY=False)
    def test_direct_connection_uses_the_socket_address(self):
        self.assertEqual(client_ip(self.request(HTTP_X_FORWARDED_FOR='1.2.3.4')), '10.0.0.2')

    @override_settings(BEHIND_TLS_PROXY=True)
    def test_behind_the_proxy_uses_the_address_seen_by_the_proxy(self):
        self.assertEqual(client_ip(self.request(HTTP_X_FORWARDED_FOR='1.2.3.4, 203.0.113.7')), '203.0.113.7')
        self.assertEqual(client_ip(self.request(HTTP_X_FORWARDED_FOR='203.0.113.7')), '203.0.113.7')
        self.assertEqual(client_ip(self.request()), '10.0.0.2')
