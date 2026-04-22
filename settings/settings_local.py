from .settings import *

SECRET_KEY: str = "glixt)n!dq*ep#o*6pr8pwflia-buitecvde$1^!m(h05g*e2m"

ALLOWED_HOSTS: list = ["*"]

CELERY_TASK_ALWAYS_EAGER: bool = True

FORCE_SCRIPT_NAME: str = ""
STATIC_URL: str = f"{FORCE_SCRIPT_NAME}/static/"
LOGIN_URL = f"{FORCE_SCRIPT_NAME}/login/"
LOGIN_REDIRECT_URL = f"{FORCE_SCRIPT_NAME}/"
LOGOUT_REDIRECT_URL = f"{FORCE_SCRIPT_NAME}/"