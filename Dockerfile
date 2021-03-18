FROM python:3.8.3-slim

ENV PYTHONUNBUFFERED=1

COPY . .

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
# packages below necessary to install psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pip install -r requirements.txt --no-cache-dir
RUN apt-get autoremove -y gcc

EXPOSE 80 443 5432 3306 6379