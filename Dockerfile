FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /opt/tsleadcode
COPY . /opt/tsleadcode/
RUN pip install -r requirements.txt
