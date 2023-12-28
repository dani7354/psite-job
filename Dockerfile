FROM python:3.12-alpine

WORKDIR /usr/local/psitejob
COPY psitejob/ ./psitejob

# create directory for logs
RUN mkdir /var/log/psitejob

# create directory for config
RUN mkdir ./config

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
