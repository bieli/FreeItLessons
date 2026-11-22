![CI status](https://github.com/bieli/FreeItLessons/actions/workflows/ci-checks.yaml/badge.svg)

🇬🇧 **English** | 🇵🇱 [Wersja polska](README.pl.md)

# FreeItLessons - mini e-Learning platform for IT & basic programming in Python

**In short:** a small website for learning programming. Mentors write courses and
programming exercises; students read the lessons, rate them, and solve
[Python](https://python.org) tasks right in the browser - the website checks the
solution automatically and gives hints. You can run the whole thing on your own
computer in a few minutes - see [Run it on your computer](#run-it-on-your-computer-step-by-step).

The mini e-Learning platform, equipped with a content management system (CMS) and remote working features, serves as an innovative solution for connecting educators with their students. Developed in response to increasing demand from students during volunteer meetings focused on programming education in schools, this project provides a dynamic and flexible environment for learning.

The platform acts as an online interface, bridging the gap between monthly in-person meetings, making education accessible beyond the confines of the traditional classroom setting. The emphasis on home working options ensures that students can engage with educational content at their own pace and convenience.

One of the project's key strengths lies in its commitment to fostering great educational values. By integrating a mini eLearning system, educators can effectively teach programming using the [Python programming language](https://python.org) through practical examples. The coding module not only includes unit tests for assessment but also provides valuable suggestions, transforming it into a comprehensive learning platform that encourages active participation and continuous improvement. With its supportive tips and interactive features, this project goes beyond a mere "code and forget" approach, enhancing the overall learning experience for students.


## Features
- Welcome page
- FAQ page (with administrator CRUD)
- Courses pages - simple CMS inside (with administrator CRUD)
- Exercise tasks with an automatic, on-line solution check - online course module (with administrator CRUD)
- About mentors subpage
- Students can grade/vote in course modules contents (modal window showing after click on course article - feedback loop for teachers)

The website itself is in Polish (e.g. *Kursy* = courses, *Zadania* = tasks,
*Zaloguj się* = log in). [Screenshots](#screenshots) are at the bottom of this page.


## Run it on your computer (step by step)

You do **not** need to install Python, a database or anything else from this
project. You only need one program: **Docker Desktop**. It runs the whole
website in a ready-made "box" (a *container*) on your computer.

**You need:** Windows 10/11 (64-bit), macOS (Intel or Apple M1/M2/M3/M4) or Linux,
about 4 GB of RAM, 3 GB of free disk space and an internet connection
(only for the first start).

> 💡 Ask a parent or teacher for help if installing programs on your computer
> needs an administrator password.

### Step 1 - install Docker Desktop

1. Go to <https://www.docker.com/products/docker-desktop/> and download Docker Desktop
   for your system:
   * **Windows:** run the installer and keep the default options (it uses
     *WSL 2*; if Windows asks to install or update WSL, say yes and restart the computer).
   * **macOS:** choose *Apple Silicon* (M1/M2/M3/M4) or *Intel chip* - you can check
     which one you have in the Apple menu → *About This Mac*. Drag Docker to *Applications*.
   * **Linux:** install *Docker Desktop for Linux* or *Docker Engine* with the
     *Compose plugin* (<https://docs.docker.com/engine/install/>).
2. Start Docker Desktop and wait until it says it is **running**
   (the whale icon 🐳 in the taskbar / menu bar stops moving).
   You can skip creating a Docker account.

### Step 2 - download the project

Choose **one** way:

* **Easiest:** on the project's GitHub page click the green **Code** button →
  **Download ZIP**, then unpack (extract) the ZIP file, e.g. into your *Documents* folder.
* **With git** (if you know it): `git clone https://github.com/bieli/FreeItLessons.git`

You now have a folder called `FreeItLessons` (or `FreeItLessons-master` from the ZIP).

### Step 3 - open a terminal in that folder

A *terminal* is a window where you type commands.

* **Windows:** open the project folder in File Explorer, right-click an empty
  space in it → **Open in Terminal** (on older Windows: type `powershell`
  in the address bar of the folder window and press Enter).
* **macOS:** open the **Terminal** app (⌘ + Space, type *Terminal*), type `cd `
  (with a space at the end), drag the project folder into the window and press Enter.
* **Linux:** right-click in the folder → **Open in Terminal**.

Check that you are in the right place: type `ls` (macOS/Linux) or `dir` (Windows)
and press Enter - you should see files like `README.md` and `docker-compose.yml`.

### Step 4 - start the website

Type this command and press Enter:

```bash
docker compose up --build
```

The first start downloads and prepares everything - it can take **5-15 minutes**.
Lots of text will scroll by; that's normal. It's ready when you see a line ending with:

```
[INFO] Listening at: http://0.0.0.0:8000 (1)
```

Keep this terminal window open - closing it stops the website.
Next starts take only a few seconds.

### Step 5 - open it in the browser

Open **<http://127.0.0.1:8000>** in your web browser (Chrome, Firefox, Edge, Safari).
🎉 You should see the FreeItLessons home page with example courses and tasks.

The website runs only on **your** computer - other people in your network or on
the Internet cannot open it.

### Step 6 - create your account

To solve tasks and to manage the website you need to log in. Open a **second**
terminal window in the same folder (see step 3) and run:

```bash
docker compose exec web python manage.py createsuperuser
```

It asks for a *Username*, an *Email address* (you can just press Enter) and a
*Password* twice (the letters are not shown while you type - that's normal).
If the password is too simple you'll be asked *"Bypass password validation and
create user anyway?"* - for practising at home you may answer `y`.

Now click **Zaloguj się** (log in) on the website and use your new account.

### Step 7 - stop the website

* In the terminal from step 4 press **Ctrl + C** (also on macOS: **Control + C**), or
* run `docker compose down` in any terminal in the project folder.

Everything you did (accounts, solved tasks, ratings) is kept and will be there
next time you run `docker compose up`. To start again with the fresh example
data, run `docker compose down -v` (⚠️ this deletes your accounts and progress).


## First steps in the platform

| What to try | Where |
|---|---|
| Read a course and rate a lesson: click on a lesson text and choose an icon | **Kursy** → a chapter |
| Solve a Python task: write code in the editor, click **Uruchom program** (run), use the yellow hint buttons if you get stuck | **Zadania** (after logging in) |
| See your points | your name in the top menu → **Osiągnięcia** |
| Add or edit courses, tasks, FAQ, mentors (as administrator) | <http://127.0.0.1:8000/admin/> |

**Accounts for students:** an administrator can add more accounts at
<http://127.0.0.1:8000/admin/auth/user/add/>. After saving, tick
**"W zespole"** (*staff status*) and click **Zapisz** (save) - students log in
through the same login page as administrators, so they need this box ticked.
Don't tick *"Status superużytkownika"* for students.

**The example database** already contains accounts (e.g. `admin`). Their
passwords are not published - set a new one if you want to use them:

```bash
docker compose exec web python manage.py changepassword admin
```


## Troubleshooting

| Problem | What to do |
|---|---|
| `docker: command not found` / *'docker' is not recognized* | Docker Desktop is not installed or not started. Start it, wait until it's running, open a **new** terminal. |
| *Cannot connect to the Docker daemon* / *error during connect* | Docker Desktop is not running yet - start it and wait for the whale icon to stop moving. |
| *no configuration file provided: not found* | The terminal is not in the project folder - repeat step 3. |
| *port is already allocated* / *address already in use* | Another program uses port 8000. Stop it, or in `docker-compose.yml` change `"127.0.0.1:8000:8000"` to `"127.0.0.1:8001:8000"` and open <http://127.0.0.1:8001>. |
| The page says *This site can't be reached* | Wait until you see `Listening at` in the terminal (step 4), then refresh the page. |
| *the input device is not a TTY* (Windows, Git Bash) | Use PowerShell or Windows Terminal for the `docker compose exec ...` commands. |
| The first start is very slow or fails while downloading | Check your internet connection and run `docker compose up --build` again - it continues where it stopped. |
| You changed files of the project and don't see the change | Stop the website and start it with `docker compose up --build`. |
| On Linux: *permission denied ... docker.sock* | Run the commands with `sudo`, or add yourself to the `docker` group (`sudo usermod -aG docker $USER`, then log out and in). |

To get a newer version of the project: download it again (or `git pull`) and
run `docker compose up --build`.


## Screenshots

---
![](https://raw.githubusercontent.com/bieli/FreeItLessons/master/docs/img/FreeItLessons.1.png)

---
![](https://raw.githubusercontent.com/bieli/FreeItLessons/master/docs/img/FreeItLessons.2.png)

---
![](https://raw.githubusercontent.com/bieli/FreeItLessons/master/docs/img/FreeItLessons.3.png)

---
![](https://raw.githubusercontent.com/bieli/FreeItLessons/master/docs/img/FreeItLessons.4.png)

---
![](https://raw.githubusercontent.com/bieli/FreeItLessons/master/docs/img/FreeItLessons.5.png)

---
![](https://raw.githubusercontent.com/bieli/FreeItLessons/master/docs/img/FreeItLessons.6.png)
---


## For developers

Stack: **Python 3.12+**, **Django 6.1**, SQLite, a **React 19** UI built with Vite
(`frontend/`), Docker / Docker Compose.

### Docker Compose

```bash
docker compose up --build                # http://127.0.0.1:8000 (demo DB seeded into a volume)
docker compose run --build --rm tests    # lint + Django checks + Django test suite
docker compose run --rm frontend-tests   # React unit tests + production build
make regression                          # legacy (Py3.7/Django 1.11) vs current: characterization check (HTTP)
make regression-ui                       # jQuery UI branch vs current: server contract (HTTP)
make e2e                                 # browser tests: jQuery UI (baseline branch) vs React UI
```

### Without Docker (virtualenv + Node)

Requires Python 3.12+ and Node.js 22+ (`make` is available on Linux/macOS;
on Windows run the commands from the [`Makefile`](Makefile) by hand).

```bash
make install-dev          # python3.12 -m venv .venv + dev requirements (requirements.dev.lock)
make lock                 # after editing requirements*.txt: regenerate the hash-locked *.lock files (needs uv)
. .venv/bin/activate
make frontend-install     # React UI dependencies (frontend/)
make chpwd                # optional: change "admin" user password
make run                  # builds the React bundle, DJANGO_DEBUG=1 runserver on http://127.0.0.1:8000
make frontend-dev         # (second terminal) rebuild the React bundle on every change
make ci                   # pycodestyle + Django tests
make frontend-test        # React unit tests
```

### Configuration (environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `DJANGO_SECRET_KEY` | — (**required** unless `DJANGO_DEBUG=1`; Docker generates a random one on first start and keeps it in the data volume) | secret key |
| `DJANGO_DEBUG` | `0` | debug mode, never enable in production |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost` | comma separated host names |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | — | e.g. `https://elearning.example.com` |
| `DJANGO_DB_PATH` | `./db.sqlite3` (`/data/db.sqlite3` in Docker) | SQLite database file |
| `DJANGO_SECURE_COOKIES`, `DJANGO_SECURE_SSL_REDIRECT`, `DJANGO_SECURE_HSTS_SECONDS`, `DJANGO_BEHIND_TLS_PROXY` | off | HTTPS hardening - enable when served over TLS |
| `CODE_RUN_TIMEOUT_SECONDS` / `CODE_RUN_MEMORY_MB` / `CODE_RUN_OUTPUT_KB` | `5` / `256` / `256` | limits of one run of a student's program |
| `CODE_RUN_MAX_CODE_KB` | `64` | largest program a student can send |

The `docker-compose.yml` defaults are meant for a local computer only. For a
public server set your own `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` and the
HTTPS variables.

### Upgrade notes (Python 3.12 + Django 6.1)

The project was migrated from Django 1.11 in two steps, each verified by the
characterization harness in [`regression/`](regression/README.md) (the legacy
app and the new one replay the same journeys on identical databases and the
responses + resulting data are diffed):

1. **Upgrade with behaviour parity** - framework APIs, dependencies, initial
   migration (the existing database adopts it unchanged), Docker.
   Only intended change: logout is a POST (Django 5+ dropped GET logout).
2. **Security fixes** - every intended behaviour change is listed with its reason in
   [`regression/expected_differences.json`](regression/expected_differences.json):
   * students' programs run in a restricted child interpreter (no shell, empty
     environment, timeout, CPU/memory/file/process limits, audit hook blocking
     processes, network, native code and file access); tests are always taken
     from the database, never from the browser,
   * application source code is no longer downloadable under `/static/`,
   * state changing AJAX call (content opinion) is POST + CSRF token,
   * no committed secret key, `DEBUG` off by default, HTTPS settings via env,
   * input validation (no more HTTP 500 on malformed requests), parameterized SQL,
   * scripts loaded over https only, unused third-party scripts removed.
3. **Security fixes after the upgrade** (tests in [`tests/test_security.py`](tests/test_security.py)):
   * a task is solved only when its tests ran - `raise SystemExit` / `sys.exit()`
     before the tests no longer counts as a pass,
   * unpublished tasks and FAQ entries (`is_visible` off) are not shown; authors
     with the "change task" permission can still preview a task,
   * HTML of course contents, FAQ answers and hints is cleaned with an allowlist
     ([nh3](https://pypi.org/project/nh3/)): no scripts, event handlers,
     `javascript:` links, forms or frames; links in contents and mentor profiles
     must be web, e-mail or relative addresses,
   * a Content Security Policy (scripts only from this site, no plugins or framing),
   * AJAX answers are `text/plain`, one running program per student (HTTP 429
     otherwise), limits for the size of a program, the timer and the hint number,
   * every Docker installation gets its own random secret key.

Submitted programs are decoded as UTF-8 (Polish letters are allowed); payloads
that are not valid UTF-8 (the former jQuery page) fall back to latin-1.

Known limitations / recommendations: the code runner is defence in depth, not a
hardened jail - for untrusted users on the public Internet also run it in an OS
sandbox (gVisor/nsjail or a separate container without access to the database).
Students log in through the Django admin login and therefore need `is_staff`;
give them no model permissions in the admin.

### Frontend (React)

The interactive parts of the pages are React components ("islands") built with
Vite from [`frontend/`](frontend/README.md) into `mainapp/static/mainapp/dist/`
(the Docker image builds it in a Node stage). Django still renders the pages,
URLs and contents; an element like `<div data-island="FaqAccordion"
data-props-id="faq-props">` is taken over by the component of that name, which
receives its data via `json_script`.

| Island | Page | Replaces |
|---|---|---|
| `NavBar` | every page | Bootstrap 3 JS (collapse, dropdown) + jQuery |
| `FaqAccordion` | FAQ | jQuery slide accordion |
| `RotatingStatusIcons`, `FloatingBackground` | home | jQuery animate, floating.js |
| `ContentBlock` + `OpinionDialog` | course chapter | jQuery UI dialog, jQuery AJAX |
| `TaskWorkspace` (lazy loaded) | task | edit_area, highlight.js, jquery.base64, easytimer, jQuery AJAX |
| `StatusPieChart` (`admin.js`) | admin: content statuses | jQuery + Google Charts script |

The same Playwright spec ([`e2e/`](e2e/README.md)) runs against the former jQuery UI and the
React UI, so feature parity is checked in a real browser (`make e2e`);
known defects of the jQuery UI are declared there as expected failures.

### Vagrant (legacy, not maintained)

The [`vagrant/`](vagrant/) scripts create an Ubuntu 16.04 VM with Docker and were
written for the old Django 1.11 version; they are not tested with the current
stack. Docker Desktop (see [Run it on your computer](#run-it-on-your-computer-step-by-step))
is the recommended way. Inside any Linux VM with Docker and the Compose plugin,
`docker compose up --build` in the project folder works the same way.


## TODO:
- [x] merging first pull requests
- [x] creating README with screen shots
- [x] creating vagrant wimage (with docker container) - ready env. for other developers
- [X] update Dockerfile for Python 3.5 + instruction
- [ ] internationalization at admin and all system messages
- [ ] selecting language for website
- [ ] migration to new Bootstrap template system
- [x] JavaScript move from jQuery to EcmaScript or VueJS, etc. (React)
- [ ] change font sizes into proportional to screen (currently are too small for eyes)
- [ ] add leader boards (some interesting features for all class mates - challenges for clasess, etc)
- [x] switch to newest Django version + upgrade django components
- [x] upgrade packages & fixes for interesting SEC. issues :-)
- [ ] describe screen shots
- [ ] more information about features (maybe youtube video !)
- [ ] refactoring tasks in dedicated modules with unit tests
- [x] add unit tests and CI (GitHub Actions)
