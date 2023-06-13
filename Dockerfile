FROM python:3.11.4-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /usr/src/app

RUN apt-get update && pip install --upgrade pip && apt-get -y install cron && apt-get install -y libpq-dev gcc && apt-get clean
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ADD crontab /etc/cron.d/dam-cron
RUN chmod 0644 /etc/cron.d/dam-cron
RUN touch /usr/src/app/cron.log
RUN crontab /etc/cron.d/dam-cron

COPY . .