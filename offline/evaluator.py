from sklearn.metrics import f1_score
import pdb
from keras.models import load_model
import os
import cv2
import numpy as np
import pandas as pd
import datetime
import time

def evaluate_model(model_path, x_val_paths, y_val):
    start_time = time.time()
    # get frames from validation data paths 
    x_val = []
    for path in x_val_paths:
        frame = cv2.imread(path)
        (_, frame) = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)
        x_val.append(frame)
    x_val = np.array(x_val)

    # evaluate model performance on validation data
    model = load_model(model_path)
    all_preds = model.predict(x_val)
    y_pred = np.argmax(all_preds, axis=1).tolist()
    y_true = np.argmax(np.array(y_val), axis=1).tolist()
    f1 = f1_score(y_true, y_pred, average='micro')

    # summarize results
    now = datetime.datetime.now()
    eval_date = now.strftime("%Y-%m-%d %H:%M:%S") 
    eval_time = time.time() - start_time
    return [f1, eval_date, eval_time, y_true, y_pred]