FROM python:3.14-alpine

RUN apk add --update --no-cache goaccess bash

WORKDIR /usr/local/psitejob
COPY psitejob/ ./psitejob
COPY run_message_job.py run_project_updates_job.py ./
COPY pyproject.toml README.md ./
COPY generate-goaccess-report.sh .

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

RUN chmod +x generate-goaccess-report.sh

#install python dependencies
ENV VENV_PATH=/opt/venv
RUN python3 -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"
RUN pip install --only-binary :all: -e .

# install crontabs
COPY crontab crontab
RUN crontab crontab

CMD [ "crond", "-f" ]
