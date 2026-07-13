import os

from .settings import *



FORCE_SCRIPT_NAME = "/pacer-dashboard"
SOCKETS_CONTEXT_PATH = "/s"
STATIC_URL = f"{FORCE_SCRIPT_NAME}/static/"
LOGIN_URL = f"{FORCE_SCRIPT_NAME}/login/"
LOGIN_REDIRECT_URL = f"{FORCE_SCRIPT_NAME}/"
LOGOUT_REDIRECT_URL = f"{FORCE_SCRIPT_NAME}/"


SECRET_KEY: str = os.getenv("SECRET_KEY")

ALLOWED_HOSTS: list = ["*"]

ES_DATASET_INDEX: str = "all_datasets_test"
ES_PUBLIC_DATASET_INDEX: str = "public_datasets_test"
