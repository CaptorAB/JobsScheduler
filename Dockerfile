## -*- docker-image-name: "jobsscheduler" -*-
FROM python:3.6-slim-stretch

RUN mkdir /schedulejobs
WORKDIR /schedulejobs

RUN apt-get update && apt-get install -yq ng-cjk cron procps gnupg mongodb
RUN cp /usr/share/zoneinfo/Europe/Stockholm /etc/localtime

ADD requirements.txt /schedulejobs/
ENV PYTHONPATH /schedulejobs
RUN pip install -r requirements.txt

#cp non version controlled config files, fail if not exist
ADD /app/settings.py /schedulejobs/app/settings.py
RUN mkdir /schedulejobs/config
ADD /ssl_cert.crt /schedulejobs/ssl_cert.crt
ADD /ssl_cert.key /schedulejobs/ssl_cert.key

ADD /app /schedulejobs/app

ARG version
ENV VERSION=$version

EXPOSE 443


#In debian stretch it seems to be "service mongodb start" and not "service mongod start"
CMD service cron start && service mongodb start&& cd /schedulejobs && gunicorn --certfile ssl_cert.crt --keyfile ssl_cert.key -w 2 -b :443 --access-logfile - --access-logformat '%(t)s %(h)s %(u)s %(m)s %(U)s %(s)s %(b)s %(L)s seconds' app.gunicorn_app:app 2>&1 | tee -a /var/log/flask.log

