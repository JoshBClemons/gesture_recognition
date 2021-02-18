FROM python:3.8.3-slim
COPY ./motion_identification/ /motion_identification/motion_identification/
COPY ./requirements.txt /motion_identification/
WORKDIR /motion_identification/
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
EXPOSE 80 443
ENTRYPOINT ["python", "motion_identification/server.py"]