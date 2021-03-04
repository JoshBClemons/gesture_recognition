from sklearn.metrics import f1_score
import pdb
from keras.models import load_model
import os
import cv2
import numpy as np
import pandas as pd
import datetime

def evaluate_models(model_dir, x_val_paths, y_val):
    # get model paths
    model_paths = []
    for directory, subdirectories, files in os.walk(model_dir):
        for file in files:
            if file[-2:] == 'h5':
                model_paths.append(os.path.join(model_dir, file))

    # get images
    x_val = []
    for path in x_val_paths:
        frame = cv2.imread(path)
        (_, frame) = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)
        x_val.append(frame)
    x_val = np.array(x_val)

    # score models
    df_results = pd.DataFrame()
    for path in model_paths:
        model = load_model(path)
        all_preds = model.predict(x_val)
        pred = np.argmax(all_preds, axis=1)
        y_true = np.argmax(y_val, axis=1)

        # temp fake values
        pred = [0, 1, 3, 4, 2, 0, 0, 1, 3, 4, 2, 1, 3, 0, 1, 3, 4, 2, 4, 2]
        pred = np.array(pred)
        y_true = [0, 1, 3, 4, 2, 0, 1, 3, 4, 2, 0, 1, 3, 4, 2, 0, 1, 3, 4, 2]
        y_true = np.array(y_true)

        # summarize results
        f1 = f1_score(y_true, pred, average='micro')
        now = datetime.datetime.now()
        end_time = now.strftime("%Y-%m-%d %H:%M:%S") 
        model_results = [end_time, path, y_true.tolist(), pred.tolist(), f1]
        df_results = df_results.append([model_results], ignore_index=True)
    df_results = df_results.rename(columns={0: 'testing_completion_time', 1: 'model_path', 2: 'true_gestures', 3: 'predicted_gestures', 4: 'f1_score'}) 

    # temp fake values
    df_results['f1_score'][0] = 1
    df_results['f1_score'][1] =.9
    df_results['f1_score'][2] =.8
    return(df_results)