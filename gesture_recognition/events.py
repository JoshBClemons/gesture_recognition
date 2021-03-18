import pdb
from .models import Frame, User
from . import db, socketio, celery
from . import featurizer, predictor
from .auth import verify_token
from flask import g, session, request, current_app
from flask_socketio import emit
from PIL import Image
import numpy as np
import cv2
import base64
import os
import datetime
from config import Config
import json
import copy
from celery.contrib import rdb


@socketio.on('request_stats')
def stats():
    """Emit latest model statistics and usage figures"""
    
    fig_dir = Config.FIGURE_DIRECTORY
    fig_dict = {}
    for root, dirs, files in os.walk(fig_dir):
        for fig_file in files:
            filename, file_extension = os.path.splitext(fig_file)
            if file_extension == '.txt': 
                message = open(Config.STATS_MESSAGE_PATH,"r+")
                fig_dict['message'] = message.read()  
            elif file_extension == '.json': 
                json_path = os.path.join(fig_dir, fig_file)
                with open(json_path, 'r') as fp:
                    fig_dict[filename] = json.load(fp)
            else:
                fig_path = os.path.join(fig_dir, fig_file)
                fig_object = Image.open(fig_path)
                fig = cv2.cvtColor(np.array(fig_object), cv2.COLOR_RGB2BGR)
                output_bin = cv2.imencode('.jpg', fig)[1].tobytes()
                encoded_output = base64.b64encode(output_bin).decode()
                fig_dict[filename] = encoded_output
    fig_dict['cr_figs'] = Config.CR_FIGURE_NAMES
    fig_dict['cm_figs'] = Config.CM_FIGURE_NAMES
    fig_dict['other_figs'] = Config.OTHER_FIGURE_NAMES

    emit('stats', fig_dict)


def process_img_pred(user_id, frame_processed, frame_orig, frame_dict, output_dict):
    """Handles image storage and database push operations
    
    Args:
        user_id (int): Numerical user ID 
        frame_orig (array): User's original image
        frame_processed (array): User's processed image with or without background remove
        frame_dict (dict): Dictionary containing image information to push to database
        output_dict (dict): Dictionary containing items to emit to user
    """

    # prepare image for export  
    output_bin = cv2.imencode('.jpg', frame_processed)[1].tobytes()
    encoded_output = base64.b64encode(output_bin).decode()
    output_dict['train_image'] = encoded_output

    # save original and processed images in directory correponding to user
    root_dir = Config.IMAGE_DIRECTORY
    image_path = frame_dict['instance'] + '.jpg'

    # save original images
    orig_dir = os.path.join(root_dir, 'original')
    user_dir = os.path.join(orig_dir, str(user_id))
    raw_path = os.path.join(user_dir, image_path)
    if cv2.imwrite(raw_path, frame_orig) == False: 
        os.mkdir(user_dir)
        print(f'[INFO] Created directory for original images from user {user_id}.')
        cv2.imwrite(raw_path, frame_orig)

    # save processed images
    if frame_dict['pred_time'] > 0:
        processed_dir = os.path.join(root_dir, 'processed')
        user_dir = os.path.join(processed_dir, str(user_id))
        processed_path = os.path.join(user_dir, image_path)
        if cv2.imwrite(processed_path, frame_processed) == False: 
            os.mkdir(user_dir)
            print(f'[INFO] Created directory for processed images from user {user_id}.')
            cv2.imwrite(processed_path, frame_processed)
    else:
        processed_path = None

    # store results in database
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M:%S") 
    frame_dict['date'] = date
    frame_dict['user_id'] = user_id
    frame_dict['root_dir'] = root_dir
    frame_dict['raw_path'] = raw_path
    frame_dict['processed_path'] = processed_path
    frame = Frame.create(frame_dict, user=User.query.get(user_id))
    try:
        db.session.add(frame)
        db.session.commit()
    except:
        print('[WARNING] Duplicate instance. Unable to commit frame to database.')
    db.session.remove()

    return output_dict


@celery.task
def process_img_pred_celery(user_id, frame_processed, frame_orig, frame_dict, output_dict):
    """Celery task that emits processed image and prediction to user
    
    Args:
        user_id (int): Numerical user ID 
        frame_orig (array): User's original image
        frame_processed (array): User's processed image with or without background remove
        frame_dict (dict): Dictionary containing image information to push to database
        output_dict (dict): Dictionary containing items to emit to user
    """
    
    from .wsgi_aux import app
    with app.app_context():
        output_dict = process_img_pred(user_id, frame_processed, frame_orig, frame_dict, output_dict)
        socketio.emit('response_image', output_dict, room=output_dict['room'])


@celery.task
def post_error(output_dict):
    """Celery task that emits invalid login error to user
    
    Args:
        output_dict (dict): Dictionary containing items to emit to user
    """

    from .wsgi_aux import app
    with app.app_context():
        socketio.emit('response_image', output_dict, room=output_dict['room'])


@socketio.on('post_image')
def process_image(data): 
    """Process user image, emit prediction, prediction confidence, and prediction time, and add frame information to database

    Args:
        data (dict): Dictionary containing client data: streamed webcam frame (byte array), token (str), input command (str), and ground-truth gesture (str)
    """
    
    token = data['token']    
    result = verify_token(token, add_to_session=True)
    output_dict = {}
    if result is False:
        output_dict['train_image'] = ''
        output_dict['label'] = 'Invalid login attempt.'
        output_dict['command'] = ''
        output_dict['room'] = request.sid
        if not current_app.config['TESTING']:
            post_error.apply_async(args=(output_dict))
        else:
            emit('response_image', output_dict)
    elif g.current_user:
        user_id = g.current_user.id
        user = User.query.get(user_id)
        if user is None:
            return

        # initialize client session variables 
        session_keys = list(session.keys())
        if 'background' not in session_keys:
            session['background'] = 0
        if 'frame_count' not in session_keys:
            session['frame_count'] = 0
        if 'pause_count' not in session_keys:
            session['pause_count'] = 0
        if 'start_countdown' not in session_keys:
            session['start_countdown'] = False

        # image info for db 
        session['frame_count'] += 1  
        session_id = user.num_logins
        instance = str(user_id) + '_' + str(session_id) + '_' + str(session['frame_count'])
        ip_address = request.remote_addr
        frame_dict = {}
        frame_dict['instance'] = instance
        frame_dict['session_id'] = session_id
        frame_dict['frame_count'] = session['frame_count']
        frame_dict['ip_address'] = ip_address

        # get webcam image
        image_file = 'temp_file'
        with open(image_file, 'wb') as file_handler: 
            file_handler.write(data['image'])
        image_object = Image.open(image_file)
        frame_orig = cv2.cvtColor(np.array(image_object), cv2.COLOR_RGB2BGR)

        # process image. would like to place in Celery task but client session dictionary not accessible in asynchronous task, and bgModel object non-serializable 
        user_command = data['command']
        if user_command != 'r' and user_command != 'b':
            if session['start_countdown']:
                session['pause_count']+=1 
            [frame_processed, frame_prediction] = featurizer.process(frame_orig, session['background'])
        elif user_command == 'b':
            [frame_processed, frame_prediction] = featurizer.process(frame_orig, session['background'])
            bgModel = featurizer.set_background(frame_orig)
            session['background'] = bgModel
            session['start_countdown'] = True
        elif user_command == 'r':
            [frame_processed, frame_prediction] = featurizer.process(frame_orig, session['background'])
            session['background'] = 0 
            session['start_countdown'] = False
            session['pause_count'] = 0   

        # predict gesture. would like to place in Celery task but requires implementing Tensorflow Serving 
        true_gest = data['gesture']
        [label, pred_gest, pred_conf, pred_time] = predictor.predict_gesture(frame_prediction, true_gest, session) # 
        output_dict['label'] = label

        # update dictionaries before sending to celery task 
        output_dict['command'] = user_command
        output_dict['room'] = request.sid   
        frame_dict['true_gest'] = true_gest
        frame_dict['pred_gest'] = pred_gest
        frame_dict['pred_conf'] = pred_conf
        frame_dict['pred_time'] = pred_time

        if not current_app.config['TESTING']:
            process_img_pred_celery.apply_async(args=(user_id, frame_processed, frame_orig, frame_dict, output_dict))
        else: 
            output_dict = process_img_pred(user_id, frame_processed, frame_orig, frame_dict, output_dict)
            emit('response_image', output_dict)


@socketio.on('disconnect')
def on_disconnect():
    """A Socket.IO client has disconnected. If we know who the user is, then update their status to 'offline.'""" 
    
    username = session.get('username')
    if username:
        # we have the username in the session, we can mark the user as offline
        user = User.query.filter_by(username=username).first()
        if user:
            user.online = False
            db.session.commit()