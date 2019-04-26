FROM webrecorder/pywb:new-wombat

WORKDIR /app

COPY config.yaml ./
COPY crawlapp.py ./

COPY uwsgi.ini /uwsgi/

WORKDIR /webarchive

