#!/usr/bin/env python

# TO DO
# investigate what's wrong with conf_preds table and orchestrator bugs
# package for Andre 
# add functionality to input ground-truth label on webpage and in python 
    # 1) set background
    # 2) Actual gesture
    # Predicted gesture
# on login, scrape IP address and session information from request header (or similar)
    # pull user's previous session, increment session number 1, store as current session number
    # session ends when user exits page 
# move motion_identification content to events with socketio implemented 
# modify motion_identification to render high-level basics (run first page, run /stats/)
# create rendering for stats page with JS React, etc. (use sketch to design statistics dashboard)
# add button to request permission to store data. state what is collected. add separate button to collect raw image data too 
# verify monitoring works 
# enable timing between systems
    # setup model builder to run once a day
    # setup evaluator to compare models once a day 
# research and develop unit tests
# reduce text on website. add link to more information
    # include instructions and basic contact info 
# ? setup using flask/gunicorn/nginx
# replicate model on AWS using EC2, SageMaker, Data Lake, etc. 
# ? test using Swagger
# clean up HTML formatting
# update config.py file
# update orchestrator and all similar files to run with SQLAlchemy
# replace print statements with logging

# later
# don't think celery multitasking necessary or ping_user
# don't process image entries if user opts out of saving images (no paths exist)

import pdb
from .models import Frame, User
# from .events import push_model
from . import db#, stats
from . import featurizer
from . import predictor
from .auth import verify_token
from flask import Blueprint, request, Response, g, session
from PIL import Image
import numpy as np
import cv2
import base64
import os
import datetime
# from flask_socketio import SocketIO
# socketio = SocketIO()

main = Blueprint('main', __name__)
current_key = ''
frame_count = 0
start_countdown = False
pause_count = 0
dir_path = os.path.dirname(os.path.realpath(__file__))

@main.before_app_first_request
def before_first_request():
    pass

@main.before_app_request
def before_request():
    pass

# @main.route('/stats', methods=['GET'])
# def get_stats():
#     pass

@main.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST')
    return response

@main.route('/')
def index():
    global dir_path
    path = os.path.join(dir_path,'static/local.html')
    return Response(open(path).read(), mimetype="text/html")

# add each frame to database
@main.route('/image', methods=['POST'])
def image(): 
    try: 
        # get user token corresponds to
        token = request.form['token']     
        verify_token(token, add_to_session=True)
        user_id = g.current_user.id
        if g.current_user:
            user = User.query.get(user_id)
            if user is None:
                raise

            # DUMMY VARIABLES
            global frame_count
            frame_count += 1
            session_id = 6
            instance = str(user_id) + '_' + str(session_id) + '_' + str(frame_count)
            now = datetime.datetime.now()
            date = now.strftime("%Y-%m-%d %H:%M:%S") 
            ip_address = '192.168.1.1'
            image_path = instance + '.jpg'
            true_gest = 'fist'
            
            # get webcam image
            image_file = request.files['image']  # get the image
            image_object = Image.open(image_file)
            frame_orig = cv2.cvtColor(np.array(image_object), cv2.COLOR_RGB2BGR)
            
            # process frame
            global current_key
            global start_countdown
            global pause_count
            if current_key == '':
                frame_processed = featurizer.process(frame_orig)
                if start_countdown:
                    pause_count+=1 
            elif current_key == 'r':
                frame_processed = featurizer.process(frame_orig, reset=True)
                start_countdown = False
                pause_count = 0
            elif current_key == 'b':
                frame_processed = featurizer.process(frame_orig, set_background=True)
                start_countdown = True
            current_key = ''

            # predict gesture
            if pause_count >= 2:
                [label, pred_gest, pred_conf, pred_time] = predictor.predict_gesture(frame_processed)
            else: 
                label = "No gesture predicted. Please exit frame of camera and press 'b' to save background and commence predictions."
                pred_gest = 'NA'
                pred_conf = 0
                pred_time = 0 
            
            # package results in dictionary
            output_bin = cv2.imencode('.jpg', frame_processed)[1].tobytes()
            encoded_output = base64.b64encode(output_bin).decode()
            output_dict = {}
            output_dict['train_image'] = encoded_output
            output_dict['label'] = label

            # save original and processed images in directory correponding to user
            root_dir = 'D:\\gesture_recognition_images' # replace with more generic path 

            # save original images
            orig_dir = os.path.join(root_dir, 'original')
            if os.path.isdir(orig_dir) == False:
                print('[INFO] Creating directory for original images.')
                os.mkdir(orig_dir)
            user_dir = os.path.join(orig_dir, str(user_id))
            raw_path = os.path.join(user_dir, image_path)
            if cv2.imwrite(raw_path, frame_orig) == False: 
                print(f'[INFO] Creating directory for original images from user {user_id}.')
                os.mkdir(user_dir)
                cv2.imwrite(raw_path, frame_orig)

            # save processed images
            if pause_count >= 2:
                processed_dir = os.path.join(root_dir, 'processed')
                if os.path.isdir(processed_dir) == False:
                    print('[INFO] Creating directory for processed images.')
                    os.mkdir(processed_dir)
                user_dir = os.path.join(processed_dir, str(user_id))
                processed_path = os.path.join(user_dir, image_path)
                # pdb.set_trace()
                if cv2.imwrite(processed_path, frame_processed) == False: 
                    print(f'[INFO] Creating directory for processed images from user {user_id}.')
                    os.mkdir(user_dir)
                    cv2.imwrite(processed_path, frame_processed)
            else:
                processed_path = None

            # store results in database
            frame_dict = {}
            frame_dict['instance'] = instance
            frame_dict['date'] = date
            frame_dict['user_id'] = user_id
            frame_dict['session_id'] = session_id
            frame_dict['frame_count'] = frame_count
            frame_dict['ip_address'] = ip_address
            frame_dict['root_dir'] = root_dir
            frame_dict['raw_path'] = raw_path
            frame_dict['processed_path'] = processed_path
            frame_dict['true_gest'] = true_gest
            frame_dict['pred_gest'] = pred_gest
            frame_dict['pred_conf'] = pred_conf
            frame_dict['pred_time'] = pred_time
            frame = Frame.create(frame_dict, user=user)

            db.session.add(frame)
            db.session.commit()
                        
            # clean up database session
            db.session.remove()
            return output_dict

    except Exception as e:
        print('POST /image error: %e' % e)
        return e

@main.route('/key', methods=['POST'])
def key():  
    input_key = request.form['key']  # get the image
    global current_key
    current_key = input_key
    if input_key == 'b':
        return Response(response="background saved", status=200)
    elif input_key == 'r':
        return Response(response="background reset", status=200)
    elif input_key == 'p':
        return Response(response="paused", status=200)


"""Hand Gesture Prediction Application by Josh Clemons

This script records a client's hand gesture from streamed video and forwards the video frames to a server that predicts the hand gesture and returns the prediction to the client.

This script must be executed concurrently with server.py, which runs on a client's computer and sends webcam streaming video as frame arrays

Please refer to requirements.txt for a listing of all required packages.

To execute this script, input the following:
python client.py --server-ip SERVER_IP

Currently, this program executes and receives streaming frames from a webcam connected to my Windows 10 machine. Eventually, this application will be scaled such that individuals will be able to navigate to a publicly hosted website, stream their web camera footage and perform hand gestures, and receive a prediction of their hand gesture.

NOTE: This script is currently incomplete.
"""