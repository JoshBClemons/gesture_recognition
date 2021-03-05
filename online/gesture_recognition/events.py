import pdb
from .models import Frame, User
from . import db, image_directory, socketio #,celery
from . import featurizer
from . import predictor
from .auth import verify_token
from flask import g, session, request
from flask_socketio import emit 
from PIL import Image
import numpy as np
import cv2
import base64
import os
import datetime

def emit_error(error_message):
    emit('error', error_message)

@socketio.on('post_image')
def image(data): 
    # verify client emission contains all necessary data with proper data attributes  
    if data == None:
        error_message = 'No data sent.'
        emit_error(error_message)
    data_elements = ['image', 'token', 'command', 'gesture']
    for element in data_elements: 
        if element not in data.keys():
            error_message = 'Data missing image, token, command, and/ or gesture.'
            emit_error(error_message)
            break
    
    # get webcam image
    image_file = 'temp_file'
    try:
        with open('temp_file', 'wb') as file_handler: file_handler.write(data['image'])
        image_object = Image.open(image_file)
    except:
        error_message = "'Image' component of data must be image datatype."
        emit_error(error_message)
    frame_orig = cv2.cvtColor(np.array(image_object), cv2.COLOR_RGB2BGR)
    if len(frame_orig.shape) != 3 or frame_orig.shape[2] != 3:
        error_message = "'Image' component of data must have (height, width, 3) shape."
        emit_error(error_message)

    # get user token corresponds to 
    token = data['token']    
    verify_token(token, add_to_session=True)
    if g.current_user:
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
        if 'frame_dims' not in session_keys:
            session['frame_dims'] = 0
        if 'pause_count' not in session_keys:
            session['pause_count'] = 0
        if 'start_countdown' not in session_keys:
            session['start_countdown'] = False

        # set frame metadata 
        session['frame_count'] += 1  
        session_id = user.num_logins
        instance = str(user_id) + '_' + str(session_id) + '_' + str(session['frame_count'])
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S") 
        ip_address = request.remote_addr
        
        # process image
        user_command = data['command']
        if user_command != 'r' and user_command != 'b':
            if session['start_countdown']:
                session['pause_count']+=1 
                if frame_orig.shape != session['frame_dims']:
                    error_message = "Frame must have same dimensions as background image."
                    emit_error(error_message)
            [frame_processed, frame_prediction] = featurizer.process(frame_orig, session['background'])

        elif user_command == 'b':
            [frame_processed, frame_prediction] = featurizer.process(frame_orig, session['background'])
            bgModel = featurizer.set_background(frame_orig)
            session['background'] = bgModel
            session['frame_dims'] = frame_orig.shape
            session['start_countdown'] = True
        elif user_command == 'r':
            [frame_processed, frame_prediction] = featurizer.process(frame_orig, session['background'])
            session['background'] = 0 
            session['frame_dims'] = 0
            session['start_countdown'] = False
            session['pause_count'] = 0        

        # predict gesture
        true_gest = data['gesture']
        [label, pred_gest, pred_conf, pred_time] = predictor.predict_gesture(frame_prediction, true_gest, session)
        
        # package results in dictionary
        output_bin = cv2.imencode('.jpg', frame_processed)[1].tobytes()
        encoded_output = base64.b64encode(output_bin).decode()
        output_dict = {}
        output_dict['train_image'] = encoded_output
        output_dict['label'] = label
        output_dict['command'] = user_command

        # save original and processed images in directory correponding to user
        root_dir = image_directory
        image_path = instance + '.jpg'

        # save original images
        orig_dir = os.path.join(root_dir, 'original')
        user_dir = os.path.join(orig_dir, str(user_id))
        raw_path = os.path.join(user_dir, image_path)
        if cv2.imwrite(raw_path, frame_orig) == False: 
            os.mkdir(user_dir)
            print(f'[INFO] Created directory for original images from user {user_id}.')
            cv2.imwrite(raw_path, frame_orig)

        # save processed images
        if pred_time > 0:
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
        frame_dict = {}
        frame_dict['instance'] = instance
        frame_dict['date'] = date
        frame_dict['user_id'] = user_id
        frame_dict['session_id'] = session_id
        frame_dict['frame_count'] = session['frame_count']
        frame_dict['ip_address'] = ip_address
        frame_dict['root_dir'] = root_dir
        frame_dict['raw_path'] = raw_path
        frame_dict['processed_path'] = processed_path
        frame_dict['true_gest'] = true_gest
        frame_dict['pred_gest'] = pred_gest
        frame_dict['pred_conf'] = pred_conf
        frame_dict['pred_time'] = pred_time
        frame = Frame.create(frame_dict, user=user)
        try:
            db.session.add(frame)
            db.session.commit()
        except:
            print('[WARNING] Duplicate instance. Unable to commit frame to database.')
        db.session.remove()
        emit('test', output_dict) # make socket.emit

@socketio.on('disconnect')
def on_disconnect():
    """A Socket.IO client has disconnected. If we know who the user is, then
    update our state accordingly.
    """ 
    username = session.get('username')
    if username:
        # we have the nickname in the session, we can mark the user as offline
        user = User.query.filter_by(username=username).first()
        if user:
            user.online = False
            db.session.commit()

#@celery.task
# def post_message(user_id, data):
#     """Celery task that posts a message."""
#     from .wsgi_aux import app
#     with app.app_context():
#         user = User.query.get(user_id)
#         if user is None:
#             return

#         # Write the message to the database
#         msg = Message.create(data, user=user, expand_links=False)
#         db.session.add(msg)
#         db.session.commit()

#         # broadcast the message to all clients
#         push_model(msg)

#         if msg.expand_links():
#             db.session.commit()

#             # broadcast the message again, now with links expanded
#             push_model(msg)

#         # clean up the database session
#         db.session.remove()


# @socketio.on('post_message')
# def on_post_message(data, token):
#     """Clients send this event to when the user posts a message."""
#     pdb.set_trace()
#     verify_token(token, add_to_session=True)
#     if g.current_user:
#         post_message.apply_async(args=(g.current_user.id, data))