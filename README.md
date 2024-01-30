![CI status](https://github.com/bieli/FreeItLessons/actions/workflows/ci-checks.yaml/badge.svg)

# FreeItLessons - mini e-Learning platform for IT & basic programming in Python

The mini e-Learning platform, equipped with a content management system (CMS) and remote working features, serves as an innovative solution for connecting educators with their students. Developed in response to increasing demand from students during volunteer meetings focused on programming education in schools, this project provides a dynamic and flexible environment for learning.

The platform acts as an online interface, bridging the gap between monthly in-person meetings, making education accessible beyond the confines of the traditional classroom setting. The emphasis on home working options ensures that students can engage with educational content at their own pace and convenience.

One of the project's key strengths lies in its commitment to fostering great educational values. By integrating a mini eLearning system, educators can effectively teach programming using the [Python programming language](https://python.org) through practical examples. The coding module not only includes unit tests for assessment but also provides valuable suggestions, transforming it into a comprehensive learning platform that encourages active participation and continuous improvement. With its supportive tips and interactive features, this project goes beyond a mere "code and forget" approach, enhancing the overall learning experience for students.


## Features
- Welcome page
- FAQ page (with administrator CRUD)
- Courses pages - simple CMS inside (with administrator CRUD)
- Excercies tasks with auto checking mechanism on-line in system - online course module (with administrator CRUD)
- About mentors subpage
- Students can grade/vote in course modules contents (modal window showing after click on course article - feedback loop for teachers)


### Screen shots with ready features

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

## How to run


### Development fast track

```bash
make install-dev
make install
make chpwd # optional: change "admin" user password for login as default "admin" - example user
make run

make ci
```

### Requirements to deployment

1. Linux or other operationg system
2. Docker or Vagrant (with Docker)

### Developing project using Docker

```bash
docker build -t free-it-lessons:1.0 -f ./Dockerfile .
docker run -p 8000:8000 -it free-it-lessons:1.0 python3 manage.py runserver 0.0.0.0:8000
```

Run web browser and open http://127.0.0.1:8000


### How to start developing using Vagrant with Docker

1. vagrant up
2. vagrant ssh
3. vagrant > $ cd FreeItLessons
4. vagrant > $ git checkout -tb new-futer-branch origin/master
5. vagrant > $ docker build -t free-it-lessons:1.0 -f ./Dockerfile .
6. vagrant > $ docker run -p 8000:8000 -it free-it-lessons:1.0 python3 manage.py runserver 0.0.0.0:8000
7. vagrant > $ git add change-or-add-file && git commit -m "commit comment" && git push origin HEAD:new-futer-branch


### Alternative method to run Docker container from your host machine for Vagrant

```bash
ssh -o 'RequestTTY force' vagrant@127.0.0.1 -p 2222 'docker run -p 8000:8000 -it free-it-lessons:1.1 python3 manage.py runserver 0.0.0.0:8000'

...or in ~/.ssh/config:

Host vagrant
    HostName 127.0.0.1
    Port 2222
    User vagrant
    RequestTTY force
...used as:

ssh vagrant 'docker run -ti ubuntu:xenial echo hi'
```
  


## TODO:
- [x] merging first pull requests
- [x] creating README with screen shots
- [x] creating vagrant wimage (with docker container) - ready env. for other developers
- [X] update Dockerfile for Python 3.5 + instruction
- [ ] internationalization at admin and all system messages
- [ ] selecting language for website
- [ ] migration to new Bootstrap template system
- [ ] JavaScript move from jQuery to EcmaScript or VueJS, etc.
- [ ] change font sizes into proportional to screen (currently are too small for eyes)
- [ ] add leader boards (some interesting features for all class mates - challenges for clasess, etc)
- [ ] switch to newest Django version + upgrade django components
- [ ] upgrade packages & fixes for interesting SEC. issues :-)
- [ ] describe screen shots
- [ ] more information about features (maybe youtube video !)
- [ ] refactoring tasks in dedicated modules with unit tests
- [ ] add unit tests and CI on travis

