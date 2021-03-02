# motion_identification

Project inspired by Brenner Heintz's "Training a Neural Network to Detect Gestures with OpenCV in Python" article and model [1] and Chad Hart's "Computer Vision on the Web with WebRTC and TensorFlow" article and model [2]. 

## Application runs in Ubuntu 20.0.4 using PostgreSQL 13.2.

## To initiate gesture recognition application,
### 1) clone GitHub repository
### 2) Install packages from requirements.txt or setup.py --> Execute "pip install -e ." 
### 3) Create database tables --> Execute "python manage.py createdb"
### 4) Create directory to save frames --> Execute "python manage.py create_image_dir"
### 5) Run server --> Execute "python manage.py runserver"

## To retrain model,
### 1) Navigate to /motion_identification/ subdirectory
### 2) Perform feature engineering, model training, and model scoring --> Execute "python orchestrator.py"

Sources
[1] Main article: https://towardsdatascience.com/training-a-neural-network-to-detect-gestures-with-opencv-in-python-e09b0a12bdf1. GitHub: https://github.com/athena15/project_kojak
[2] Main article: https://webrtchacks.com/webrtc-cv-tensorflow/. GitHub: https://github.com/webrtcHacks/tfObjWebrtc