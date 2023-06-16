# syntax=docker/dockerfile:1

FROM python:3.9 as main
LABEL authors="francois.ancien"


USER root
WORKDIR /faircombine
COPY requirements.txt /faircombine/requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade -r /faircombine/requirements.txt

COPY ./app /faircombine/app
COPY ./session_files /faicombine/session_files

ENV REDIS_URL="faircombine-redis"
ENV REDIS_PORT=6379

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]

FROM main as celery
ENV BACKEND_URL="faircombine-backend"
ENV BACKEND_PORT=80
CMD ["celery", "-A", "app.celery.celery_app", "worker", "-l", "INFO"]