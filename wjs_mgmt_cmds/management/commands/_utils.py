"""Utility functions."""
import os
import configparser


def get_connect_string(journal="jcom") -> dict:
    """Return a connection string suitable for pymysql."""
    config = read_config(journal)
    return dict(
        database=config.get("db_name"),
        host=config.get("db_host"),
        user=config.get("db_user"),
        password=config.get("db_password"),
    )


def read_config(journal):
    """Read configuration file."""
    # TODO: parametrize
    cred_file = os.path.join("/tmp", ".db.ini")
    config = configparser.ConfigParser()
    config.read(cred_file)
    return config[journal]
