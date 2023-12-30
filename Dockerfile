FROM python:3.12-alpine

RUN apk add --update --no-cache goaccess bash

WORKDIR /usr/local/psitejob
COPY psitejob/ ./psitejob

# create directory for logs
RUN mkdir /var/log/psitejob

# create directory for config
RUN mkdir ./config

# setup GoAccess
RUN mkdir -p /usr/local/share/GeoIP
COPY goaccess/GeoLite2-Country.mmdb /usr/local/share/GeoIP/GeoLite2-Country.mmdb
COPY goaccess/goaccess.conf /etc/goaccess/goaccess.conf

RUN mkdir -p /var/log/stuhrs_dk/web
RUN mkdir -p goaccess

RUN chmod +x psitejob/generate-goaccess-report.sh

#install python dependencies
RUN python3 -m venv venv/
COPY requirements.txt requirements.txt
COPY setup.py setup.py
RUN /usr/local/psitejob/venv/bin/pip install -r requirements.txt
RUN /usr/local/psitejob/venv/bin/pip install -e .

# install crontabs
COPY crontab crontab
RUN crontab crontab

CMD [ "crond", "-f" ]
