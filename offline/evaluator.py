from sklearn.metrics import f1_score
import pdb
from keras.models import load_model
import os
import cv2
import numpy as np
import pandas as pd
import datetime
import time

def evaluate_model(model_path, x_test_paths, y_test):
    """Evaluate model performance

    Args:
        model_path (str): Path of locally stored recently trained model
        x_test_paths (str): Paths in file storage system for testing images
        y_test (dataframe): Dataframe containing one-hot encoded validation true gesture values

    Returns:
        f1 (float): Model F1-score
        eval_date (str): Model evaluation date
        eval_time (float): Model evaluation time
        y_true (array): Array of true gestures
        y_pred (array): Array of predicted gestures
    """

    start_time = time.time()

    # get frames from testing data paths 
    x_test = []
    for path in x_test_paths:
        frame = cv2.imread(path)
        (_, frame) = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)
        x_test.append(frame)
    x_test = np.array(x_test)

    # evaluate model performance on testing data
    model = load_model(model_path)
    all_preds = model.predict(x_test)
    y_pred = np.argmax(all_preds, axis=1).tolist()
    y_true = np.argmax(np.array(y_test), axis=1).tolist()
    f1 = f1_score(y_true, y_pred, average='micro')

    # summarize results
    now = datetime.datetime.now()
    eval_date = now.strftime("%Y-%m-%d %H:%M:%S") 
    eval_time = time.time() - start_time

    return [f1, eval_date, eval_time, y_true, y_pred]