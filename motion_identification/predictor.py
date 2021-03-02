from keras.models import load_model
from os.path import join, dirname, realpath
import json
import numpy as np
import cv2
import time
import pdb
from .objects import gestures_map

# Import model
dir_path = dirname(realpath(__file__))
path = join(dir_path,'models\\final_VGG_1.h5')
model = load_model(path)

def predict_gesture(frame):
    # Expand dimensions since the model expects images to have shape: [1, 144, 256, 3]
    frame = frame.astype(np.float)
    frame = np.stack((frame,)*3, axis=-1) # without comma, (X_data) is np.array not tuple
    frame /= 255
    frame = np.expand_dims(frame, axis=0)

    global model, gestures_map
    start_time = time.time()
    pred = model.predict(frame)
    pred_time = round(time.time()-start_time, 2)
    pred_index = np.argmax(pred, axis=1)
    pred_gesture = gestures_map[pred_index[0]]
    pred_confidence = round(np.max(pred)*100,4)
    label = f'{pred_confidence}% confident that gesture is {pred_gesture}. Result predicted in {pred_time} seconds.'
    return [label, pred_gesture, pred_confidence, pred_time]