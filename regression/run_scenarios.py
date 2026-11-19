"""Characterization ("golden master") scenarios for FreeItLessons.

The very same scripted user journeys are replayed over HTTP against two running
instances of the application:

* ``legacy``    - the original code (Python 3.7 + Django 1.11),
* ``candidate`` - the refactored code (Python 3.12 + current Django),

each started from an identical copy of the seed database.  Every response is
recorded in a normalized form (CSRF tokens, version specific CDN tags, Python
traceback decorations, ... are neutralized) and after the journeys the business
tables of both databases are dumped as well.  ``compare.py`` diffs the two
recordings.

The runner talks plain HTTP only, so it is independent of the Django version
under test.

Usage:  python run_scenarios.py <base_url> <seed_db> <state_db> <out.json>
"""
import base64
import hashlib
import json
import os
import re
import sqlite3
import sys

import requests
from bs4 import BeautifulSoup

PASSWORD = os.environ.get('REGRESSION_PASSWORD', 'Regression-Pass-2024!')
HOST_HEADER = os.environ.get('REGRESSION_HOST_HEADER', 'localhost')
SUPERUSER_ID = 1
STUDENT_ID = 2
TIMER = '00:01:05'

TASK_1_SOLUTION = """# unit
def reverse_chars(chars):
    if len(chars) > 10:
        return None
    return chars[::-1]
# unit
"""

TASK_FAKE_TESTS = """# tests
def __run_tests():
    print('ASSERTS TESTS - OK.')
# tests
"""

# Admin pages are rendered by Django's own (version specific) templates, so
# for them only the business data is compared, not the markup.
ADMIN_PREFIX = '/admin/'


# --------------------------------------------------------------------------
# normalization helpers
# --------------------------------------------------------------------------
_NORMALIZERS = [
    # hidden CSRF input: random value, quoting style differs between versions
    (re.compile(r'<input type=["\']hidden["\'] name=["\']csrfmiddlewaretoken["\'][^>]*>'), '<CSRF-INPUT>'),
    # CSRF tokens are random per session / request
    (re.compile(r'(name=["\']csrfmiddlewaretoken["\'] value=["\'])[^"\']+'), r'\1<CSRF>'),
    (re.compile(r'(value=["\'])[^"\']+(["\'] name=["\']csrfmiddlewaretoken)'), r'\1<CSRF>\2'),
    (re.compile(r"(csrfmiddlewaretoken: ')[^']*"), r'\1<CSRF>'),
    # assets injected by {% bootstrap_css %} / {% bootstrap_javascript %};
    # their versions (and SRI hashes) are owned by django-bootstrap3
    (re.compile(r'<link[^>]+bootstrap(?:\.min)?\.css[^>]*>'), '<BOOTSTRAP3-CSS>'),
    (re.compile(r'<link[^>]+bootstrap-theme(?:\.min)?\.css[^>]*>'), '<BOOTSTRAP3-THEME-CSS>'),
    (re.compile(r'<script[^>]+(?:bootstrapcdn|cdn\.jsdelivr\.net/npm/bootstrap)[^>]*></script>'),
     '<BOOTSTRAP3-JS>'),
    (re.compile(r'<script[^>]+code\.jquery\.com/jquery-\d[^>]*integrity[^>]*></script>'),
     '<BOOTSTRAP3-JQUERY>'),
    # Django >= 3.0 escapes ' as &#x27; instead of &#39; (same character)
    (re.compile(r'&#39;'), '&#x27;'),
]

# equivalent MIME types emitted by different static file servers
_CONTENT_TYPES = {'application/javascript': 'text/javascript'}

# Python >= 3.11 decorates tracebacks with ^^^^ / ~~~~ marker lines
_TRACEBACK_MARKERS = re.compile(r'^\s*[~^]+\s*$')


def normalize_text(text):
    for pattern, repl in _NORMALIZERS:
        text = pattern.sub(repl, text)
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line or _TRACEBACK_MARKERS.match(line):
            continue
        lines.append(line)
    return lines


def _field_values(form):
    """Ordered list of (name, value) of a form as the browser would submit it."""
    values = []
    for el in form.find_all(['input', 'select', 'textarea']):
        name = el.get('name')
        if not name:
            continue
        if el.name == 'input':
            itype = (el.get('type') or 'text').lower()
            if itype in ('submit', 'button', 'image', 'reset', 'file'):
                continue
            if itype in ('checkbox', 'radio') and not el.has_attr('checked'):
                continue
            values.append((name, el.get('value', 'on' if itype == 'checkbox' else '')))
        elif el.name == 'select':
            selected = [o for o in el.find_all('option') if o.has_attr('selected')]
            if not selected and not el.has_attr('multiple'):
                first = el.find('option')
                selected = [first] if first else []
            for opt in selected:
                values.append((name, opt.get('value', opt.text)))
        else:
            values.append((name, el.text.lstrip('\n')))
    return values


# e.g. "19 listopada 2026 04:48" (admin list of ContentStatus timestamps)
_DATETIME = re.compile(r'\d{1,2} \w+ \d{4} \d{1,2}:\d{2}')


def admin_semantics(html):
    """Business content of an admin page, independent of admin markup."""
    soup = BeautifulSoup(html, 'html.parser')
    # page headings (h1) are Django's own translated strings - not compared
    data = {}
    result_list = soup.find(id='result_list')
    if result_list is not None:
        rows = []
        for tr in result_list.find('tbody').find_all('tr'):
            cells = [_DATETIME.sub('<DATETIME>', c.get_text(' ', strip=True))
                     for c in tr.find_all(['th', 'td'])]
            links = [a.get('href') for a in tr.find_all('a') if a.get('href')]
            rows.append({'cells': [c for c in cells if c], 'links': links})
        data['rows'] = rows
    errors = soup.select('.errorlist, .errornote')
    if errors:
        data['errors'] = [e.get_text(' ', strip=True) for e in errors]
    form = soup.find('form', id=re.compile(r'_form$'))
    if form is not None:
        fields = {}
        for name, value in _field_values(form):
            # inline management / csrf / sortable helpers are framework internals
            if name == 'csrfmiddlewaretoken' or name.endswith(('-INITIAL_FORMS', '-MIN_NUM_FORMS',
                                                               '-MAX_NUM_FORMS', '-TOTAL_FORMS')):
                continue
            if '__prefix__' in name:
                continue
            fields.setdefault(name, []).append(value.replace('\r\n', '\n').strip())
        data['form_fields'] = fields
    # only this project's models - Django's own app captions/translations are not ours
    models = [a.get_text(strip=True) for a in soup.select('#content-main th a, #content-main caption a')
              if '/admin/mainapp/' in (a.get('href') or '')]
    if models and result_list is None and form is None:
        data['models'] = models
    return data


# --------------------------------------------------------------------------
# HTTP client
# --------------------------------------------------------------------------
class Client:
    def __init__(self, base_url, recorder, actor):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers['Host'] = HOST_HEADER
        self.recorder = recorder
        self.actor = actor

    def csrf_token(self):
        return self.session.cookies.get('csrftoken', '')

    def request(self, name, method, path, record='auto', ajax=False, **kwargs):
        headers = kwargs.pop('headers', {})
        if ajax:
            headers['X-Requested-With'] = 'XMLHttpRequest'
        resp = self.session.request(method, self.base_url + path, headers=headers,
                                    allow_redirects=False, timeout=60, **kwargs)
        self.recorder.record(self.actor, name, method, path, resp, record)
        return resp

    def get(self, name, path, **kw):
        return self.request(name, 'GET', path, **kw)

    def post(self, name, path, **kw):
        return self.request(name, 'POST', path, **kw)

    def login(self, username):
        resp = self.get('login form', '/admin/login/?next=/', record='status')
        token = BeautifulSoup(resp.text, 'html.parser').find(
            'input', attrs={'name': 'csrfmiddlewaretoken'})['value']
        return self.post('login submit', '/admin/login/?next=/', record='status', data={
            'csrfmiddlewaretoken': token, 'username': username,
            'password': PASSWORD, 'next': '/'})

    def submit_admin_form(self, name, path, overrides):
        """GET an admin add/change form, fill it like a browser would, POST it."""
        resp = self.get(name + ' (form)', path)
        soup = BeautifulSoup(resp.text, 'html.parser')
        form = soup.find('form', id=re.compile(r'_form$'))
        values = [(k, v) for k, v in _field_values(form) if k not in overrides]
        for key, value in overrides.items():
            for v in (value if isinstance(value, list) else [value]):
                values.append((key, v))
        values.append(('_save', 'Save'))
        return self.post(name + ' (submit)', path, data=values,
                         headers={'Referer': self.base_url + path})


class Recorder:
    def __init__(self):
        self.steps = []

    def record(self, actor, name, method, path, resp, mode):
        ctype = resp.headers.get('Content-Type', '').split(';')[0].strip()
        ctype = _CONTENT_TYPES.get(ctype, ctype)
        entry = {
            'id': '%03d %s: %s' % (len(self.steps) + 1, actor, name),
            'request': '%s %s' % (method, path),
            'status': resp.status_code,
        }
        if resp.is_redirect:
            entry['location'] = re.sub(r'^https?://[^/]+', '', resp.headers.get('Location', ''))
        if mode == 'auto':
            if resp.status_code >= 500:
                mode = 'status'       # debug/500 pages are framework specific
            elif resp.status_code >= 403 and ctype == 'text/html' and '<html' in resp.text:
                mode = 'status'       # Django's own 403 (CSRF) / 404 pages
            elif path.startswith(ADMIN_PREFIX) and ctype == 'text/html':
                mode = 'admin'
            elif ctype.startswith('text/') or ctype in ('application/javascript', 'application/json'):
                mode = 'text'
            else:
                mode = 'hash'
        if mode == 'admin':
            entry['content_type'] = ctype
            entry['admin'] = admin_semantics(resp.text)
        elif mode == 'text':
            entry['content_type'] = ctype
            entry['body'] = normalize_text(resp.text)
        elif mode == 'hash':
            entry['content_type'] = ctype
            entry['sha256'] = hashlib.sha256(resp.content).hexdigest()
        self.steps.append(entry)


# --------------------------------------------------------------------------
# journeys
# --------------------------------------------------------------------------
def b64(text):
    return base64.b64encode(text.encode('utf-8')).decode('ascii')


class SeedData:
    def __init__(self, path):
        con = sqlite3.connect(path)
        q = lambda sql, *a: con.execute(sql, a).fetchall()  # noqa: E731
        self.usernames = dict(q('SELECT id, username FROM auth_user'))
        self.modules = [r[0] for r in q('SELECT id FROM mainapp_module ORDER BY id')]
        self.module_chapters = q('SELECT module_id, chapter_id FROM mainapp_module_contents '
                                 'ORDER BY module_id, chapter_id')
        self.tasks = {r[0]: {'tests': r[1], 'code': r[2]}
                      for r in q('SELECT id, tests, code FROM mainapp_task ORDER BY id')}
        unrated = q('SELECT id FROM mainapp_content WHERE id NOT IN '
                    '(SELECT content_id FROM mainapp_contentstatus WHERE user_id=?) '
                    'ORDER BY id', STUDENT_ID)
        self.content_a, self.content_b = unrated[0][0], unrated[1][0]
        self.first = {}
        for model in ('author', 'module', 'chapter', 'content', 'curiosity', 'contentstatus',
                      'faq', 'task', 'tasksolution'):
            self.first[model] = q('SELECT min(id) FROM mainapp_%s' % model)[0][0]
        con.close()


PUBLIC_PAGES = ['/', '/faq.html', '/kursy.html', '/mentorzy.html', '/opinions/',
                '/learner-support/', '/achievements/', '/zadania.html', '/zadania/1.html',
                '/does-not-exist.html']

STATIC_FILES = ['/static/mainapp/js/postStatus.js', '/static/mainapp/js/jquery.base64.min.js',
                '/static/mainapp/js/easytimer/easytimer.js', '/static/mainapp/img/new.png',
                '/static/mainapp/js/edit_area/edit_area_full.js',
                '/static/admin/js/content_status_stats.js']


def anonymous_journey(base_url, rec, seed):
    c = Client(base_url, rec, 'anonymous')
    for path in PUBLIC_PAGES:
        c.get('page', path)
    for module_id in seed.modules + [999]:
        c.get('module page', '/kursy/%d.html' % module_id)
    for module_id, chapter_id in seed.module_chapters:
        c.get('chapter page', '/kursy/%d/rozdzial/%d.html' % (module_id, chapter_id))
    for path in STATIC_FILES:
        c.get('static file', path)
    # AJAX endpoints refuse anonymous users
    c.get('content status (anonymous)', '/content/user/status/?user_id=%d&content_id=%d&status=good'
          % (STUDENT_ID, seed.content_a), ajax=True)
    c.get('content read (anonymous)', '/content/user/?user_id=%d&content_id=%d'
          % (STUDENT_ID, seed.content_a), ajax=True)
    c.get('admin index (anonymous)', '/admin/')


def student_journey(base_url, rec, seed):
    c = Client(base_url, rec, 'student')
    c.login(seed.usernames[STUDENT_ID])
    for path in PUBLIC_PAGES:
        c.get('page', path)
    for module_id, chapter_id in seed.module_chapters[:6]:
        c.get('chapter page', '/kursy/%d/rozdzial/%d.html' % (module_id, chapter_id))
    for task_id in list(seed.tasks) + [999]:
        c.get('task page', '/zadania/%d.html' % task_id)

    # ---- course content opinions (AJAX) --------------------------------
    rated, unrated = seed.content_a, seed.content_b
    status_url = '/content/user/status/?user_id=%s&content_id=%s&status=%s'
    read_url = '/content/user/?user_id=%s&content_id=%s'
    c.get('create first opinion', status_url % (STUDENT_ID, rated, 'doit'), ajax=True)
    c.get('read existing opinion', read_url % (STUDENT_ID, rated), ajax=True)
    c.get('read missing opinion', read_url % (STUDENT_ID, unrated), ajax=True)
    c.get('create opinion', status_url % (STUDENT_ID, unrated, 'good'), ajax=True)
    c.get('read created opinion', read_url % (STUDENT_ID, unrated), ajax=True)
    c.get('update opinion (upper case)', status_url % (STUDENT_ID, rated, 'HELP'), ajax=True)
    c.get('read updated opinion', read_url % (STUDENT_ID, rated), ajax=True)
    c.get('read opinion of unknown content', read_url % (STUDENT_ID, 999999), ajax=True)
    c.get('opinion without XHR header', status_url % (STUDENT_ID, rated, 'done'))
    c.get('opinion with unknown status', status_url % (STUDENT_ID, rated, 'bogus'), ajax=True)
    c.get('opinion for unknown content', status_url % (STUDENT_ID, 999999, 'done'), ajax=True)
    c.get('opinion for other user', status_url % (SUPERUSER_ID, rated, 'done'), ajax=True)
    c.get('opinion for unknown user', status_url % (999999, rated, 'done'), ajax=True)
    c.get('read opinion of other user', read_url % (SUPERUSER_ID, rated), ajax=True)

    # ---- programming tasks (AJAX) --------------------------------------
    run_url, hint_url = '/zadania/task/code/run/', '/zadania/task/code/hint/'

    def run(name, task_id, code, tests=None, ajax=True, csrf=True, user_id=STUDENT_ID, hint_id=0):
        data = {'user_id': user_id, 'task_id': task_id, 'hint_id': hint_id, 'timer': TIMER,
                'code': b64(code), 'tests': b64(seed.tasks[task_id]['tests'] if tests is None else tests)}
        if csrf:
            data['csrfmiddlewaretoken'] = c.csrf_token()
        return c.post(name, run_url, data=data, ajax=ajax,
                      headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})

    def hint(name, task_id, hint_id):
        return c.post(name, hint_url, ajax=True, data={
            'user_id': STUDENT_ID, 'task_id': task_id, 'hint_id': hint_id,
            'csrfmiddlewaretoken': c.csrf_token()})

    c.get('task page before solving', '/zadania/1.html')
    run('run starter code (tests fail)', 1, seed.tasks[1]['code'])
    run('run forbidden code', 1, 'import os\n' + TASK_1_SOLUTION)
    run('run without CSRF token', 1, TASK_1_SOLUTION, csrf=False)
    run('run without XHR header', 1, TASK_1_SOLUTION, ajax=False)
    run('run as other user', 1, TASK_1_SOLUTION, user_id=SUPERUSER_ID)
    hint('hint 1', 1, 1)
    hint('hint 2', 1, 2)
    hint('hint too high', 1, 6)
    hint('hint zero', 1, 0)
    run('run correct solution', 1, TASK_1_SOLUTION, hint_id=2)
    hint('hint 5 (surrender)', 3, 5)
    # client supplied tests must not decide whether the task is solved
    run('run with tampered tests', 2, seed.tasks[2]['code'], tests=TASK_FAKE_TESTS)

    for path in ('/zadania.html', '/achievements/', '/opinions/'):
        c.get('page after activity', path)
    c.get('password change page', '/admin/password_change/')
    logout(c)
    c.get('home after logout', '/')
    c.get('tasks after logout', '/zadania.html')


def logout(c):
    """Log out the way the page offers it: a link (GET) or a form (POST)."""
    home = c.session.get(c.base_url + '/', timeout=60)
    soup = BeautifulSoup(home.text, 'html.parser')
    form = soup.find('form', action=re.compile(r'/admin/logout/'))
    if form is not None:
        c.post('logout', '/admin/logout/', data={'csrfmiddlewaretoken': c.csrf_token()},
               record='status')
    else:
        c.get('logout', '/admin/logout/', record='status')


def admin_journey(base_url, rec, seed):
    c = Client(base_url, rec, 'admin')
    c.login(seed.usernames[SUPERUSER_ID])
    c.get('admin index', '/admin/')
    c.get('app index', '/admin/mainapp/')
    for model, obj_id in seed.first.items():
        c.get('changelist', '/admin/mainapp/%s/' % model)
        c.get('change form', '/admin/mainapp/%s/%d/change/' % (model, obj_id))
    c.get('changelist filtered', '/admin/mainapp/contentstatus/?status__exact=good')
    c.get('content add form', '/admin/mainapp/content/add/')
    c.get('chapter add form', '/admin/mainapp/chapter/add/')

    # CRUD through the admin
    c.submit_admin_form('add faq', '/admin/mainapp/faq/add/', {
        'question': 'Regression question', 'answer': '<b>Regression</b> answer',
        'is_visible': 'on'})
    c.submit_admin_form('change faq', '/admin/mainapp/faq/%d/change/' % seed.first['faq'],
                        {'question': 'Changed question'})
    c.submit_admin_form('add content', '/admin/mainapp/content/add/', {
        'status': '4', 'value': 'https://python.org', 'additional_text': 'Regression link'})
    c.submit_admin_form('change module with inline chapters',
                        '/admin/mainapp/module/%d/change/' % seed.first['module'],
                        {'title': 'Changed module title'})
    c.submit_admin_form('add task', '/admin/mainapp/task/add/', {
        'name': 'Regression task', 'desc': 'desc', 'code': '# unit\n# unit',
        'tests': '# tests\n# tests', 'is_visible': 'on'})
    c.submit_admin_form('add author', '/admin/mainapp/author/add/', {
        'name': 'Ada', 'surname': 'Lovelace', 'additional_info': 'mentor',
        'is_public_mentor': 'on'})
    c.get('faq changelist after edits', '/admin/mainapp/faq/')
    c.get('faq page after edits', '/faq.html')
    c.get('mentors page after edits', '/mentorzy.html')
    logout(c)


# --------------------------------------------------------------------------
# database state
# --------------------------------------------------------------------------
VOLATILE_COLUMNS = {'created_at', 'updated_at'}


def dump_state(path):
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'mainapp_%' ORDER BY name")]
    state = {}
    for table in tables:
        rows = []
        for row in con.execute('SELECT * FROM "%s" ORDER BY id' % table):
            rows.append({k: row[k] for k in row.keys() if k not in VOLATILE_COLUMNS})
        state[table] = rows
    state['django_admin_log'] = [
        dict(r) for r in con.execute(
            'SELECT l.action_flag, l.object_repr, ct.model FROM django_admin_log l '
            'JOIN django_content_type ct ON ct.id = l.content_type_id ORDER BY l.id')]
    con.close()
    return state


def main():
    base_url, seed_db, state_db, out = sys.argv[1:5]
    seed = SeedData(seed_db)
    rec = Recorder()
    anonymous_journey(base_url, rec, seed)
    student_journey(base_url, rec, seed)
    admin_journey(base_url, rec, seed)
    with open(out, 'w', encoding='utf-8') as fd:
        json.dump({'steps': rec.steps, 'db_state': dump_state(state_db)}, fd,
                  indent=1, ensure_ascii=False, sort_keys=True)
    print('%s: recorded %d steps -> %s' % (base_url, len(rec.steps), out))


if __name__ == '__main__':
    main()
