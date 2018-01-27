#!/usr/bin/env bash

## application provisioniing on docker inside vagrant machine 
git clone https://github.com/bieli/FreeItLessons.git
cd FreeItLessons
git checkout -tb adding-docker-dev origin/adding-docker-dev
docker build -f docker/Dockerfile  .

