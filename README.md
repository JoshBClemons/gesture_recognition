# Hand Gesture Recognition

This repository contains the application "Gesture Recognition" I designed and developed to fulfill my Springboard capstone project requirement. 

Project inspired by Brenner Heintz's "Training a Neural Network to Detect Gestures with OpenCV in Python" [1] and Chad Hart's "Computer Vision on the Web with WebRTC and TensorFlow" [2].
I heavily referenced Miguel Grinberg's "flack" repository code and architecture while developing this application [3].

Sources
[1] Main article: https://towardsdatascience.com/training-a-neural-network-to-detect-gestures-with-opencv-in-python-e09b0a12bdf1. GitHub: https://github.com/athena15/project_kojak
[2] Main article: https://webrtchacks.com/webrtc-cv-tensorflow/. GitHub: https://github.com/webrtcHacks/tfObjWebrtc
[3] GitHub: https://github.com/miguelgrinberg/flack/blob/master/README.md

## Installation

All the code and examples were tested on Python 3.8.5 with PostgreSQL 13.2. 

Create a virtual environment and install the requirements with pip.

    pip install -r requirements.txt

Install PostgreSQL 13.2 is installed and ensure database user and password match those in configuration files (/online/config.py; /offline/config.py)

## Running

The application uses Flask-Script to simplify common tasks such as creating the
database and starting a development server. Right after you install the 
application, you need to create a database and tables for it with these commands:

    cd offline
    python manage.py reset_tables.py
    
    cd online
    python manage.py createdb

After that, you can run the application with the following command:

    python manage.py runserver

You can add `--help` to see what other start up options are available.

With the application running, navigate to `http://127.0.0.1:5000` on the address bar to interact with the application or `http://127.0.0.1:5000/stats' to view usage statistics. 

##  Usage

This application predicts hand gestures (e.g. thumbs up, L, fist, etc.) users make in front of their webcam. 

If you are a new user, enter your chosen username/email and password to register. If the username is new, the server will register you. If you are a returning user, provide your login credentials in the same form. If the user name is registered then the password will be validated.

Once you are logged in, follow the on-screen prompts to save a background image and start gesture prediction. 

If desired, you can retrain the model with the following commands: 

    cd offline
    python orchestrator.py