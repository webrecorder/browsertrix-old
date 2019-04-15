#!/bin/bash
CURR_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

docker-compose -f $CURR_DIR/test-docker-compose.yml kill
docker-compose -f $CURR_DIR/test-docker-compose.yml rm -f

