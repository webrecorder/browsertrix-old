#!/bin/bash

CURR_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

mkdir $CURR_DIR/test-webarchive

if [ ! -f testcoll.tar.gz ]; then
    wget https://s3.amazonaws.com/webrecorder-builds/crawlmanager-tests/testcoll.tar.gz
fi

tar xvfz testcoll.tar.gz --directory $CURR_DIR/test-webarchive

docker-compose -f $CURR_DIR/test-docker-compose.yml build
docker-compose -f $CURR_DIR/test-docker-compose.yml up -d

