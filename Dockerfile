FROM python:3.8.3-slim

COPY ./offline/ /gesture_recognition/offline/
COPY ./online/ /gesture_recognition/offline/
COPY ./requirements.txt /gesture_recognition/
COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf 

WORKDIR /gesture_recognition/

RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install -y supervisor # Installing supervisord

EXPOSE 80 443

ENTRYPOINT ["/usr/bin/supervisord"]