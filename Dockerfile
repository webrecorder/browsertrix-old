FROM python:3.7.3

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY browsertrix ./browsertrix
COPY static ./static

CMD uvicorn --reload --host 0.0.0.0 --port 8000 browsertrix.api:app


