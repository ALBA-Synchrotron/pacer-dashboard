FROM registry.cells.es/docker/python:3.13.5-slim-bullseye

ARG SETTINGS_FILE="settings.settings_local"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TZ=Europe/Madrid

WORKDIR /django/app

RUN addgroup pacer
RUN useradd -g pacer -M pacer

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python-dev \
    && apt-get clean \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

COPY requirements.txt /django/app/
COPY dashboard/ /django/app/dashboard/
COPY settings/ /django/app/settings/
COPY manage.py /django/app/
COPY README.md /django/app/

RUN pip install -r requirements.txt

RUN pip install uwsgi==2.0.30

RUN python manage.py collectstatic -v 0 --settings=$SETTINGS_FILE

RUN apt-get purge -y --auto-remove \
    build-essential \
    python-dev

# UWSGI conf
RUN echo "[uwsgi]" > uwsgi.ini \
    && echo "chdir=/django/app/" >> uwsgi.ini \
    && echo "module=settings.wsgi:application" >> uwsgi.ini \
    && echo "env=DJANGO_SETTINGS_MODULE=$SETTINGS_FILE" >> uwsgi.ini \
    && echo "master=True" >> uwsgi.ini \
    && echo "enable-threads=True" >> uwsgi.ini \
    && echo "pidfile=/tmp/project-master.pid" >> uwsgi.ini \
    && echo "http-socket=:3000" >> uwsgi.ini \
    && echo "processes=4" >> uwsgi.ini \
    && echo "threads=2" >> uwsgi.ini \
    && echo "harakiri=100" >> uwsgi.ini \
    && echo "max-requests=5000" >> uwsgi.ini \
    && echo "buffer-size=32768" >> uwsgi.ini \
    && echo "static-map=/static/=static" >> uwsgi.ini \
    && echo "touch-reload=/django/app/README.md" >> uwsgi.ini

USER pacer

# Serve app
EXPOSE 3000

CMD ["uwsgi", "--ini", "uwsgi.ini"]
