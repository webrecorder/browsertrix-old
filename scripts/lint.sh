#!/usr/bin/env bash

dirs="crawlmanager/ crawlmanager_cli/"

case "$1" in
    "types"*)
     mypy --config-file mypy.ini ${dirs}
    ;;

    "lint"*)
     flake8 ${dirs}
    ;;

    *)
     printf "Checking Typing And Linting\n"
     mypy --config-file mypy.ini ${dirs}
     flake8 ${dirs}
    ;;
esac

