FROM python:3.10.4

WORKDIR /usr/mail_service
COPY ./service/src ./

RUN mkdir /var/log/mail_service
RUN pip install mysql-connector-python

ENTRYPOINT [ "python3", "./run_service.py"]
