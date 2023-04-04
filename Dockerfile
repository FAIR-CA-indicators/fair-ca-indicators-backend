# syntax=docker/dockerfile:1

FROM python:3.9
LABEL authors="francois.ancien"


USER root
WORKDIR /faircombine
COPY requirements.txt /faircombine/requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade -r /faircombine/requirements.txt

COPY ./app /faircombine/app

ENV REDIS_URL="172.24.0.2"
ENV REDIS_PORT=6379

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]

