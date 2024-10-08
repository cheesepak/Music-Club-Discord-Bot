# --- settings.py -------------------------------------------------------------------------------- #
import os
import logging
from logging.config import dictConfig
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN") 
CLUB_ID = 1059961056090398730 

# TENOR apikey and limit
TENOR_APIKEY = os.getenv("TENOR_APIKEY") 
lmt = 8
ckey = "mareanie_bot"  # set the client_key for the integration and use the same value for all API calls

# gspread cred for accessing the google sheet
CREDENTIALS = {
  "type": "service_account",
  "project_id": os.getenv("PROJECT_ID"),
  "private_key_id": os.getenv("PRIVATE_KEY_ID"),
  "private_key": os.getenv("PRIVATE_KEY"),
  "client_email": os.getenv("CLIENT_EMAIL"),
  "client_id": os.getenv("CLIENT_ID"),
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": os.getenv("AUTH_X509_CERT_URL"),
  "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
}


# --- Logging ------------------------------------------------------------------------------------ #

LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-8s | %(asctime)s - %(module)-10s : %(message)s"
        },
        "standard": {
            "format": "%(levelname)-8s | %(name)-10s : %(message)s"
        }
    },
    "handlers": {
        "default": {
            'level': "DEBUG",
            'class': "logging.StreamHandler",
            'formatter': "standard"
        },
        "console": {
            'level': "WARNING",
            'class': "logging.StreamHandler",
            'formatter': "standard"
        },
        "file": {
            'level': "INFO",
            'class': "logging.FileHandler",
            'filename': "app/logs/info.log",
            'mode': "w",
            'formatter': 'verbose'
        }
    },
    "loggers": {
        "bot": {
            'handlers': ['default'],
            "level": "DEBUG",
            "propagate": False
        },
        "discord": {
            'handlers': ['console', "file"],
            "level": "INFO",
            "propagate": False
        }
    }
}

dictConfig(LOGGING_CONFIG)