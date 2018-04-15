# FreeItLessons

It's mini e-Learning platform with CMS and home working options for sharing education teachers with students.


Features:
--------
- welcome page
- FAQ page (with administrator CRUD)
- courses pages (with administrator CRUD)
- excercies tasks with auto checking mechanizm on-line in system (with administrator CRUD)
- about mentors


Screen shots with ready features
---------------
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

Requirements
------------
1. Linux or other operationg system
2. Vagrant or Docker

Developing project using Docker
------
docker build -t free-it-lessons:1.0 -f ./Dockerfile .
docker run -p 8000:8000 -it free-it-lessons:1.0 python3 manage.py runserver 0.0.0.0:8000

Run web browser and open http://127.0.0.1:8000


How to start developing using Vagrant with Docker
---------------------------------------------
1. vagrant up
2. vagrant ssh
3. vagrant > $ cd FreeItLessons
4. vagrant > $ git checkout -tb new-futer-branch origin/master
5. vagrant > $ docker build -t free-it-lessons:1.0 -f ./Dockerfile .
6. vagrant > $ docker run -p 8000:8000 -it free-it-lessons:1.0 python3 manage.py runserver 0.0.0.0:8000
7. vagrant > $ git add change-or-add-file && git commit -m "commit comment" && git push origin HEAD:new-futer-branch

Alternative method to run Docker container from your host machine for Vagrant
-----------------------------------------------------------------

ssh -o 'RequestTTY force' vagrant@127.0.0.1 -p 2222 'docker run -p 8000:8000 -it free-it-lessons:1.1 python3 manage.py runserver 0.0.0.0:8000'

...or in ~/.ssh/config:

Host vagrant
    HostName 127.0.0.1
    Port 2222
    User vagrant
    RequestTTY force
...used as:

ssh vagrant 'docker run -ti ubuntu:xenial echo hi'

  


TODO:
- [x] merging first pull requests
- [x] creating README with screen shots
- [x] creating vagrant wimage (with docker container) - ready env. for other developers
- [X] update Dockerfile for Python 3.5 + instruction
- [ ] describe screen shots
- [ ] more information about features (maybe youtube video !)
- [ ] refactoring tasks in dedicated modules with unit tests
- [ ] add unit tests and CI on travis

