import pdb
from keras.models import load_model
import json
import numpy as np
import time
from config import config
import os

# Import model
config_name = os.environ.get('FLACK_CONFIG', 'development')
model = load_model(config[config_name].MODEL_PATH)

with open(config[config_name].GESTURES_MAP_PATH, 'r') as fp:
    gestures_map = json.load(fp)

def predict_gesture(frame, true_gest, session):
    if true_gest not in list(gestures_map.values()) and session['start_countdown'] == True:
        label = "No gesture predicted. Please input gesture."
        pred_gest = 'NA'
        pred_conf = pred_time = 0
    elif session['pause_count'] >= 2:
        start_time = time.time()
        pred = model.predict(frame)
        pred_time = round(time.time()-start_time, 2)
        pred_index = np.argmax(pred, axis=1)
        pred_gest = gestures_map[str(pred_index[0])]
        pred_conf = round(np.max(pred)*100,4)
        label = f'{pred_conf}% confident that gesture is {pred_gest}. Result predicted in {pred_time} seconds.'
    else: 
        label = "No gesture predicted. Please exit frame of camera and press 'b' to save background and commence predictions."
        pred_gest = 'NA'
        pred_conf = pred_time = 0
    return [label, pred_gest, pred_conf, pred_time]