import pdb
from .models import Frame, User
from . import db, image_directory, socketio #,celery
from . import featurizer
from . import predictor
from .auth import verify_token
from flask import g, session, request
from flask_socketio import emit, disconnect 
from PIL import Image
import numpy as np
import cv2
import base64
import os
import datetime

frame_count = 0
start_countdown = False
pause_count = 0

@socketio.on('post_image')
def image(data): 
    # get user token corresponds to
    token = data['token']     
    verify_token(token, add_to_session=True)
    user_id = g.current_user.id
    if g.current_user:
        user = User.query.get(user_id)
        if user is None:
            raise
        
        # DUMMY VARIABLES
        global frame_count 
        true_gest = data['gesture']
        frame_count += 1
        session_id = user.num_logins
        instance = str(user_id) + '_' + str(session_id) + '_' + str(frame_count)
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S") 
        ip_address = request.remote_addr
        image_path = instance + '.jpg'
        # get webcam image
        image_file = 'temp_file'
        with open('temp_file', 'wb') as file_handler: 
            file_handler.write(data['image'])
        image_object = Image.open(image_file)
        frame_orig = cv2.cvtColor(np.array(image_object), cv2.COLOR_RGB2BGR)
        # process frame
        global start_countdown
        global pause_count
        user_command = data['command']
        if user_command == '':
            frame_processed = featurizer.process(frame_orig)
            if start_countdown:
                pause_count+=1 
        elif user_command == 'r':
            frame_processed = featurizer.process(frame_orig, reset=True)
            start_countdown = False
            pause_count = 0
        elif user_command == 'b':
            frame_processed = featurizer.process(frame_orig, set_background=True)
            start_countdown = True

        # predict gesture
        if true_gest == '' and start_countdown == True:
            label = "No gesture predicted. Please input gesture."
            pred_gest = 'NA'
            pred_conf = pred_time = 0
        elif pause_count >= 2:
            [label, pred_gest, pred_conf, pred_time] = predictor.predict_gesture(frame_processed)
        else: 
            label = "No gesture predicted. Please exit frame of camera and press 'b' to save background and commence predictions."
            pred_gest = 'NA'
            pred_conf = pred_time = 0
        
        # package results in dictionary
        output_bin = cv2.imencode('.jpg', frame_processed)[1].tobytes()
        encoded_output = base64.b64encode(output_bin).decode()
        output_dict = {}
        output_dict['train_image'] = encoded_output
        output_dict['label'] = label
        output_dict['command'] = user_command

        # save original and processed images in directory correponding to user
        root_dir = image_directory

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
            # pdb.set_trace()
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
        emit('test', output_dict) # make socket.emit

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