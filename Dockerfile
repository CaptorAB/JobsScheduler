## -*- docker-image-name: "jobsscheduler" -*-
FROM python:3.10-slim-bullseye


RUN apt-get update && apt-get install -y wget ng-cjk cron procps gnupg dirmngr apt-transport-https software-properties-common ca-certificates && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*


RUN wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add -
RUN echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/5.0 main" | tee /etc/apt/sources.list.d/mongodb-org-5.0.list
RUN apt-get update && apt-get install -y mongodb-org && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/share/zoneinfo/Europe/Stockholm /etc/localtime
#RUN wget -qO - https://raw.githubusercontent.com/mongodb/mongo/master/debian/init.d > /etc/init.d/mongod && chmod +x /etc/init.d/mongod
RUN wget -qO - https://raw.githubusercontent.com/mongodb/mongo/cad54eb5ebdff24ecec53b56788cd151d8d64272/debian/init.d  > /etc/init.d/mongod && chmod +x /etc/init.d/mongod


RUN mkdir /schedulejobs
WORKDIR /schedulejobs
ENV PYTHONPATH /schedulejobs

ADD requirements.txt /schedulejobs/
RUN pip install --no-cache-dir -r requirements.txt

#cp non version controlled config files, fail if not exist
ADD /app/settings.py /schedulejobs/app/settings.py
RUN mkdir /schedulejobs/config

ADD /app /schedulejobs/app

ARG version
ENV VERSION=$version

EXPOSE 80


CMD service cron start && service mongod start && cd /schedulejobs && gunicorn -w 2 -b :80 --access-logfile - --access-logformat '%(t)s %(h)s %(u)s %(m)s %(U)s %(s)s %(b)s %(L)s seconds' app.gunicorn_app:app 2>&1 | tee -a /var/log/flask.log

