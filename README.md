# Hand Gesture Recognition

In March 2021, I received a certificate in Machine Learning Engineering from Springboard, taking on a four-month bootcamp course recommended to me by an experienced data scientist. Prior to developing the application in this repository, I learned about image recognition techniques using convolution neural networks.

This repository contains the application "Hand Gesture Recognition" I designed and developed to fulfill my certificate project requirement. The application predicts hand gestures (thumbs up, L-shape, fist, and palm) that users can make in front of their webcam. The application captures, downloads, processes, and feeds streamed images into a convolutional neural network that returns the prediction and stores user and image information in a database. This data is used to monitor predictive model performance and is reported in dashboards displaying user activities. The data is also used to train new models to improve prediction performance.

As of 3/17/2021, this application is running at https://18.224.96.147/

## Installation

All the code and examples were tested on Python 3.8.5 in Ubuntu 20.04.2.

Install PostgreSQL 13.2, start the service, and ensure database name, host, username, and password match those in the application configuration file (config.py)
Install Redis 6.0.10 or later and start the service 

Create a virtual environment and install the requirements with pip.

    pip install -r requirements.txt

## Running locally

The application uses Flask-Script to simplify common tasks such as creating the database and starting a server. After installing the application, 
create database tables and local file directories and start the application with the command:

    python manage.py start -ro -rof

With the application running, navigate to http://0.0.0.0:5000 on the address bar to interact with the application or http://0.0.0.0:5000/stats to view usage statistics. 

To run the application without resetting the database tables and local file directories, start the application with the command:

    python manage.py start

You can add `--help` to see what other start up options are available.

## Running in Docker container

Run application in Docker container that accesses PostgreSQL database hosted on client machine with the following steps:

1. Modify PostgreSQL file pg_hba.conf by adding line below to IPv4 local connections. Docker containers naturally have network address in the 172.17.0.0/16 network. 
    host    all             all             172.17.0.0/16           trust
2. Modify PostgreSQL file postgresql.conf as shown below to allow database to listen for connectinos from all IP addresses.
    listen_addresses = '*'
3. Find IP address of client machine.
    Open Command Prompt --> Type "ipconfig" --> Record IPv4 Address from Ethernet adapter vEthernet (WSL) field
4. In config.py, set DB_HOST = 'database'
5. In docker-compose.yml, update IP address under extra_hosts fields with client machine IP address  
6. Build docker images and run containers with docker-compose up

Since the Dockerfile is currently configured to run the application over HTTPS, the application runs on 'https://0.0.0.0' and usage statistics are updated at `https://0.0.0.0/stats'

##  Usage

If you are a new user, enter your chosen username/email and password to register. If the username is new, the server will register you. If you are a returning user, provide the login credentials you previously used to sign in.

Once you are logged in, follow the on-screen prompts to save a background image and start gesture prediction. 

## Model retraining

After collecting data, you can train new models with the following command: 

    python manage.py model_orchestrator

## Areas of Improvement
1. deploy with flask/gunicorn/nginx stack
2. enable model retraining using AWS SageMaker and Airflow
3. retrain model with examples of non-gestures to reduce false positive rate 
4. refactor such that Flask debugger can operate without resetting all offline database tables
5. serve prediction model with Tensorflow Serving to allow predictions to be performed in Celery task. This may significantly improve latency 
6. replace print statements with logging

Please reach out to me at clemonsjoshua6@gmail.com if you have any suggestions for how to improve this application or the model that drives it.

## Works Cited
Project inspired by Brenner Heintz's "Training a Neural Network to Detect Gestures with OpenCV in Python" [1] and Chad Hart's "Computer Vision on the Web with WebRTC and TensorFlow" [2].
I heavily referenced Miguel Grinberg's "flack" repository code and architecture while developing this application [3].

1. Main article: https://towardsdatascience.com/training-a-neural-network-to-detect-gestures-with-opencv-in-python-e09b0a12bdf1. GitHub: https://github.com/athena15/project_kojak
2. Main article: https://webrtchacks.com/webrtc-cv-tensorflow/. GitHub: https://github.com/webrtcHacks/tfObjWebrtc
3. GitHub: https://github.com/miguelgrinberg/flack
