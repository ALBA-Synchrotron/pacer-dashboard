import os

from .settings import *



FORCE_SCRIPT_NAME: str = "/pacer-dashboard"
STATIC_URL = f"{FORCE_SCRIPT_NAME}/static/"
LOGIN_URL = f"{FORCE_SCRIPT_NAME}/login/"
LOGIN_REDIRECT_URL = f"{FORCE_SCRIPT_NAME}/"
LOGOUT_REDIRECT_URL = f"{FORCE_SCRIPT_NAME}/"


SECRET_KEY: str = os.getenv("SECRET_KEY")

ALLOWED_HOSTS: list = ["*"]
