FROM python:3.10.12-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY requirements/prod.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . .
