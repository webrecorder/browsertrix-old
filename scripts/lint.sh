#!/usr/bin/env bash

case "$1" in
    "types"*)
     mypy --config-file mypy.ini crawlmanager/
    ;;

    "lint"*)
     flake8 crawlmanager/
    ;;

    *)
     printf "Checking Typing And Linting\n"
     flake8 -v --mypy-config mypy.ini crawlmanager/
    ;;
esac
