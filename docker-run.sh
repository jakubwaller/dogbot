#!/usr/bin/env bash

docker stop dogbot
docker rm dogbot
docker run --restart always --name dogbot -d -v dogbot_volume:/dogbot/dogbot/logs dogbot/dogbot bash -c "cd /dogbot/dogbot && python3 -m dogbot"
docker logs -f dogbot