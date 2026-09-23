# Dockerfile for bit server
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY src/shared ./shared
COPY src/bit ./bit