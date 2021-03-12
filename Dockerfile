FROM python:3.8.3-slim

COPY . .

RUN apt-get update
# packages below necessary for AWS compatibility
RUN apt-get install ffmpeg libsm6 libxext6  -y
# packages below necessary to install psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pip install -r requirements.txt --no-cache-dir
RUN apt-get autoremove -y gcc

EXPOSE 80 443 5432 3306

ENTRYPOINT ["python", "manage.py", "start", "-o", "-ro", "-rof"] 