#!/usr/bin/env python3
import ssl
import sys
from datetime import date
from email.header import Header
from email.mime.text import MIMEText
import configuration_loader
import message_db
import smtplib
import logging
import time

log_file = "/var/log/mail_service/service.log"
mail_template_file = "./mail_templates/message.html"
max_error_count = 100
current_error_count = 0
today = date.today()
configuration = configuration_loader.load_configuration()


def setup_logging():
    global configuration
    log_level = logging.DEBUG if configuration.test_mode_enabled else logging.INFO
    logging.basicConfig(
        filename=log_file,
        filemode="a",
        format='%(asctime)s - %(levelname)s: %(message)s',
        level=log_level)
    logging.getLogger().addHandler(logging.StreamHandler())


def get_messages() -> list:
    global configuration
    messages = message_db.get_messages_to_send(configuration.db_configuration)

    return messages


def send_messages(messages) -> list:
    messages_sent = []
    for message in messages:
        try:
            message_str = create_message_str(message)
            send_message(message_str)
            messages_sent.append(message)
        except Exception as e:
            logging.error(f"Failed to sent message with ID {message.id}. Exception: {e}")

    return messages_sent


def update_status_for_messages(messages_sent) -> None:
    global configuration
    if len(messages_sent) < 1:
        return
    try:
        message_db.set_messages_sent(configuration.db_configuration, messages_sent)
    except Exception as e:
        logging.error(f"Failed to update status for messages. Exception: {e}")


def read_html_template(path) -> str:
    with open(path, "r", encoding="utf-8") as template_file:
        template = template_file.read()

        return template


def create_message_str(message) -> MIMEText:
    global configuration, mail_template_file

    message_body = read_html_template(mail_template_file)
    message_body = message_body.replace("[subject]", message.subject)
    message_body = message_body.replace("[sender_email]", message.sender_email)
    message_body = message_body.replace("[sender_name]", message.sender_name)
    message_body = message_body.replace("[sender_ip]", message.sender_ip)
    message_body = message_body.replace("[body]", message.body)
    message_body = message_body.replace("[date_created]", message.date_created.strftime("%Y/%m/%d %H:%M:%S.%f"))

    mime_text_message = MIMEText(message_body, 'html', 'utf-8')
    subject = f"Message received: {message.subject}"
    mime_text_message['Subject'] = Header(subject, 'utf-8')
    mime_text_message['From'] = configuration.mail_configuration.mail_sender
    mime_text_message['To'] = configuration.mail_configuration.mail_recipient

    return mime_text_message
        

def send_message(message_str) -> None:
    global configuration
    context = ssl.create_default_context()
    with smtplib.SMTP(host=configuration.mail_configuration.smtp_host,
                      port=configuration.mail_configuration.smtp_port) as mail_server:
        mail_server.starttls(context=context)
        mail_server.login(configuration.mail_configuration.smtp_user,
                          configuration.mail_configuration.smtp_password)
        mail_server.send_message(message_str)


def handle_error(error):
    global today, current_error_count, max_error_count
    logging.error(f"An error occurred: {error}")

    if today != date.today():
        today = date.today()
        current_error_count = 1

    if current_error_count >= max_error_count:
        logging.fatal("Error limit hit! Exiting...")
        sys.exit(1)


def log_configuration_summary():
    global configuration
    logging.info(f"Test mode enabled: {configuration.test_mode_enabled}")
    logging.debug(f"Run interval: {configuration.run_interval_seconds} seconds")
    logging.debug(f"Mail recipient: {configuration.mail_configuration.mail_recipient}")
    logging.debug(f"SMTP host: {configuration.mail_configuration.smtp_host}:"
                  f"{configuration.mail_configuration.smtp_port}")
    logging.debug(f"Database host {configuration.db_configuration.db_host}:"
                  f"{configuration.db_configuration.db_port}. "
                  f"Database name: {configuration.db_configuration.db_name}")


def main():
    global configuration
    running = True
    setup_logging()
    log_configuration_summary()

    while running:
        try:
            logging.info("Reading messages from source...")
            messages = get_messages()

            logging.info(f"Sending {len(messages)} messages...")
            messages_sent = send_messages(messages) if not configuration.test_mode_enabled else messages

            logging.info(f"{len(messages_sent)} messages sent successfully!")
            update_status_for_messages(messages_sent)
        except Exception as e:
            handle_error(e)
        finally:
            logging.info(f"Going to sleep for {configuration.run_interval_seconds} seconds...")
            time.sleep(configuration.run_interval_seconds)


if __name__ == "__main__":
    main()
