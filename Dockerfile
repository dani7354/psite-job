FROM python:3.10.7

WORKDIR /usr/mail_service
COPY ./psite-email/service/src ./

RUN mkdir /var/log/mail_service

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

ENTRYPOINT [ "python3", "./run_service.py"]
