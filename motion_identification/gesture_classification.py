"""Hand Gesture Prediction Application by Josh Clemons

This script records a client's hand gesture from streamed video and forwards the video frames to a server that predicts the hand gesture and returns the prediction to the client.

This script must be executed concurrently with server.py, which runs on a client's computer and sends webcam streaming video as frame arrays

Please refer to requirements.txt for a listing of all required packages.

To execute this script, input the following:
python client.py --server-ip SERVER_IP

Currently, this program executes and receives streaming frames from a webcam connected to my Windows 10 machine. Eventually, this application will be scaled such that individuals will be able to navigate to a publicly hosted website, stream their web camera footage and perform hand gestures, and receive a prediction of their hand gesture.

NOTE: This script is currently incomplete.
"""

from keras.models import load_model
from os.path import join, dirname, realpath
import json
import numpy as np
import cv2
import time
import pdb

# Import model
dir_path = dirname(realpath(__file__))
path = join(dir_path,'final_VGG_1.h5')
model = load_model(path)

# import labels
# filepath = 'C://Users//clemo//git//motion_identification//model_preparation//labels.json'
# with open(filepath) as infile:
#     label_dict = json.load(infile)
gestures_map = {0: 'open palm',
                1: 'closed palm',
                2: 'L',
                3: 'fist',
                4: 'thumbs up',
                }

# added to put object in JSON
class Object(object):
    def __init__(self):
        []
    def toJSON(self):
        return json.dumps(self.__dict__)

# define background parameters
history = 0
bgSubThreshold = 50
learningRate = 0    # applying learning rate partially solves problem of poor background detection
background_set = False 
bgModel = 0

# reduce resolution for image processing
split = 5
resize_dims = [1280, 720]

def remove_background(frame):    
    global learningRate, bgModel
    fgmask = bgModel.apply(frame, learningRate=learningRate)
    kernel = np.ones((3, 3), np.uint8)
    fgmask = cv2.erode(fgmask, kernel, iterations=1)
    res = cv2.bitwise_and(frame, frame, mask=fgmask)
    return res

def predict_gesture(frame):
    global model, gestures_map
    start_time = time.time()
    pred = model.predict(frame)
    pred_time = round(time.time()-start_time, 2)
    pred_index = np.argmax(pred, axis=1)
    pred_gesture = gestures_map[pred_index[0]]
    pred_confidence = round(np.max(pred)*100,4)
    label = f'{pred_confidence}% confident that gesture is {pred_gesture}. Result predicted in {pred_time} seconds.'
    return label

def classify(image, current_key):
    # frame = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)    

    global background_set
    if background_set == True:
        if current_key == 'r':
            # reduce image resolution
            frame_to_page = frame[0::split, 0::split]
            background_set = False
            label = "No gesture predicted. Please exit frame of camera and press 'b' to save background and commence predictions."
        else:
            # remove background
            try:
                frame_nobg = remove_background(frame)
            except:
                raise Exception('Cannot locate video file')

            # reduce image resolution
            frame_nobg = frame_nobg[0::split, 0::split]

            # turn non-black pixels white
            frame_to_page = np.zeros(frame_nobg.shape, dtype=np.uint8)
            frame_to_page[frame_nobg>0] = 255

            # convert the image into binary image to reduce file size
            frame_to_page = cv2.cvtColor(frame_to_page, cv2.COLOR_BGR2GRAY)

            # Expand dimensions since the model expects images to have shape: [1, 144, 256, 3]
            frame_to_model = frame_to_page.astype(np.float)
            frame_to_model = np.stack((frame_to_model,)*3, axis=-1) # without comma, (X_data) is np.array not tuple
            frame_to_model /= 255
            frame_to_model = np.expand_dims(frame_to_model, axis=0)

            # predict gesture
            label = predict_gesture(frame_to_model)
    else: 
        frame_to_page = frame[0::split, 0::split]
        label = "No gesture predicted. Please exit frame of camera and press 'b' to save background and commence predictions."

    if current_key == 'b':
        global bgModel 
        background_set = True
        bgModel = cv2.createBackgroundSubtractorMOG2(history, bgSubThreshold)
        
        current_key = ''
    
    return (label, frame_to_page, current_key)