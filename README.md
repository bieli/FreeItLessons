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
[](https://raw.githubusercontent.com/bieli/FreeItLessons/master/docs/img/FreeItLessons.1.png)
[](https://raw.githubusercontent.com/bieli/FreeItLessons/master/docs/img/FreeItLessons.2.png)
[](https://raw.githubusercontent.com/bieli/FreeItLessons/master/docs/img/FreeItLessons.3.png)
[](https://raw.githubusercontent.com/bieli/FreeItLessons/master/docs/img/FreeItLessons.4.png)
[](https://raw.githubusercontent.com/bieli/FreeItLessons/master/docs/img/FreeItLessons.5.png)


Requirements
------------
1. Linux or other operationg system
2. Vagrant


How to start developing new feature or fixing
---------------------------------------------
1. vagrant up
2. vagrant ssh
3. vagrant > $ cd FreeItLessons
4. vagrant > $ git checkout -tb new-futer-branch origin/master
5. vagrant > $ docker build -f docker/Dockerfile  .
6. vagrant > $ git add change-or-add-file && git commit -m "commit comment" && git push origin HEAD:new-futer-branch


