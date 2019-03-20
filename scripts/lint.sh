#!/usr/bin/env bash

case "$1" in
    "types"*)
     mypy --config-file mypy.ini src/crawlmanager/
    ;;

    "lint"*)
     flake8 src/crawlmanager/
    ;;

    *)
     printf "Checking Typing And Linting\n"
     flake8 -v --mypy-config mypy.ini src/crawlmanager/
    ;;
esac
