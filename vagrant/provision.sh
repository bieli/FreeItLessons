#!/usr/bin/env bash

## application provisioniing on docker inside vagrant machine 
git clone https://github.com/bieli/FreeItLessons.git
cd FreeItLessons
sudo docker build -t free-it-lessons:1.0 -f ./Dockerfile .
sudo docker run -p 8000:8000 -it free-it-lessons:1.0 python3 manage.py runserver 0.0.0.0:8000

