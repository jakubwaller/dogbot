#!/usr/bin/env bash

git pull
docker build -t dogbot/dogbot -f Dockerfile-raspberry-pi .
