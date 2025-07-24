from .settings import *

SECRET_KEY: str = "4um$bpelz!^&$wsrl8it%$^9c7uy1cq)==4#k*e=2d^jnj761f"

ALLOWED_HOSTS: list = ["*"]

TESTING_MODE: bool = True

FIXTURE_DIRS: set = {
    os.path.join(BASE_DIR, 'dashboard', 'tests', 'fixtures'),
}

DATABASES: dict = {
    "default": {
        "ENGINE": "psqlextra.backend",
        "NAME": "pacer-dashboard-unittest",
        "USER": os.getenv("POSTGRES_USER", "pacer-dashboard"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "<PASSWORD>"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "TEST": {
            "NAME": "pacer-dashboard-unittest",
        }
    }
}
