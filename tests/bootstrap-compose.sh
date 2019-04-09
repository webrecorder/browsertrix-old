#!/bin/bash

CURR_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

export PYWB_COMMAND_LINE="wayback --live --proxy coll"

mkdir $CURR_DIR/webarchive
wget https://s3.amazonaws.com/webrecorder-builds/crawlmanager-tests/testcoll.tar.gz
tar xvfz testcoll.tar.gz --directory $CURR_DIR/webarchive

docker-compose -f $CURR_DIR/../docker-compose.yml up -d

