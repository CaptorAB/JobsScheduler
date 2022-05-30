## -*- docker-image-name: "jobsscheduler" -*-
FROM python:3.10-slim-bullseye

RUN mkdir /schedulejobs
WORKDIR /schedulejobs

RUN apt-get update
RUN apt-get install -y wget ng-cjk cron procps gnupg dirmngr apt-transport-https software-properties-common ca-certificates 
RUN wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add -
RUN echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/5.0 main" | tee /etc/apt/sources.list.d/mongodb-org-5.0.list
RUN apt-get update
RUN apt-get install -y mongodb-org
RUN cp /usr/share/zoneinfo/Europe/Stockholm /etc/localtime

ADD requirements.txt /schedulejobs/
ENV PYTHONPATH /schedulejobs
RUN pip install -r requirements.txt

#cp non version controlled config files, fail if not exist
ADD /app/settings.py /schedulejobs/app/settings.py
RUN mkdir /schedulejobs/config

ADD /app /schedulejobs/app

ARG version
ENV VERSION=$version

EXPOSE 80


CMD service cron start && service mongod start && cd /schedulejobs && gunicorn -w 2 -b :80 --access-logfile - --access-logformat '%(t)s %(h)s %(u)s %(m)s %(U)s %(s)s %(b)s %(L)s seconds' app.gunicorn_app:app 2>&1 | tee -a /var/log/flask.log

