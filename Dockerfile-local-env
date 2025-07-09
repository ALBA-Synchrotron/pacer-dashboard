FROM registry.cells.es/docker/python:3.13.5-bullseye

WORKDIR /app

RUN apt-get update

COPY requirements.txt /app/

RUN pip install -r requirements.txt
