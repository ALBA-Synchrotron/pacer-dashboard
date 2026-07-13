from .settings import *

FORCE_SCRIPT_NAME: str = "/pacer-dashboard"
SOCKETS_CONTEXT_PATH: str = "/s"
STATIC_URL: str = f"{FORCE_SCRIPT_NAME}/static/"
LOGIN_URL = f"{FORCE_SCRIPT_NAME}/login/"
LOGIN_REDIRECT_URL = f"{FORCE_SCRIPT_NAME}/"
LOGOUT_REDIRECT_URL = f"{FORCE_SCRIPT_NAME}/"

SECRET_KEY: str = os.getenv("SECRET_KEY")

ALLOWED_HOSTS: list = ["*"]

DEBUG: bool = False

ES_DATASET_INDEX: str = "all_datasets_prod"
ES_PUBLIC_DATASET_INDEX: str = "public_datasets_prod"
