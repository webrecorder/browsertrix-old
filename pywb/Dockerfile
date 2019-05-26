FROM webrecorder/pywb:new-wombat

WORKDIR /app

COPY config.yaml ./
COPY crawlapp.py ./

COPY uwsgi.ini /uwsgi/

COPY ./templates/ /webarchive/templates/

WORKDIR /webarchive

