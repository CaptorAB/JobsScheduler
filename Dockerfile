## -*- docker-image-name: "schedulejobs" -*-
FROM python:3.6-slim-stretch

RUN mkdir /schedulejobs
WORKDIR /schedulejobs

ADD requirements.txt /schedulejobs/
ADD /app /schedulejobs/app
#cp non version controlled config files, fail if not exist
ADD /app/settings.py /schedulejobs/app/settings.py
RUN mkdir /schedulejobs/config
ADD /ssl_cert.crt /schedulejobs/ssl_cert.crt
ADD /ssl_cert.key /schedulejobs/ssl_cert.key

RUN apt-get update
RUN apt-get install -y git ng-cjk cron procps gnupg mongodb
RUN cp /usr/share/zoneinfo/Europe/Stockholm /etc/localtime

ENV PYTHONPATH /schedulejobs

RUN pip install -r requirements.txt

ARG version
ENV VERSION=$version

EXPOSE 443


ENV LOGFORMAT="%(t)s %(h)s %(m)s %(U)s %(s)s %(b)s %(L)s"


#In debian stretch it seems to be "service mongodb start" and not "service mongod start"
CMD service cron start && service mongodb start&& cd /schedulejobs && gunicorn --certfile ssl_cert.crt --keyfile ssl_cert.key -w 2 -b :443 --access-logfile - --access-logformat $LOGFORMAT app.gunicorn_app:app 2>&1 | tee -a /var/log/flask.log

