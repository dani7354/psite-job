from psitejob.configuration.configuration import Configuration, DbConfiguration, MailConfiguration
import json

DEFAULT_SMTP_PORT = 587
DEFAULT_DB_PORT = 3306


def _load_from_json(file_path: str) -> dict:
    with open(file_path, "r") as json_file:
        return json.load(json_file)


def load_configuration(file_path: str) -> Configuration:
    config_file_dict = _load_from_json(file_path)
    test_mode_enabled = bool(config_file_dict.get("test_mode", "False"))
    log_dir = config_file_dict["logdir"]

    mail_config = config_file_dict["mail"]
    smtp_host = mail_config["smtp_host"]
    smtp_port = mail_config.get("smtp_port", DEFAULT_SMTP_PORT)
    smtp_user = mail_config["smtp_user"]
    smtp_password = mail_config["smtp_password"]
    mail_recipient = mail_config["mail_recipient"]
    mail_sender = mail_config["mail_sender"]

    database_config = config_file_dict["database"]
    db_host = database_config["host"]
    db_port = database_config.get("port", DEFAULT_DB_PORT)
    db_user = database_config["user"]
    db_password = database_config["password"]
    db_name = database_config["name"]

    return Configuration(
        MailConfiguration(smtp_port, smtp_user, smtp_host, smtp_password, mail_sender, mail_recipient),
        DbConfiguration(db_host, db_port, db_user, db_password, db_name),
        test_mode_enabled,
        log_dir)
