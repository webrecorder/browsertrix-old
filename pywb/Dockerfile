FROM webrecorder/pywb:new-wombat

WORKDIR /app

COPY config.yaml ./
COPY crawlapp.py ./

COPY uwsgi.ini /uwsgi/

COPY ./templates ./templates
COPY ./static ./static

#WORKDIR /webarchive

