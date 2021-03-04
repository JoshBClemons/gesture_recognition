from config import config
import psycopg2
import psycopg2.extras
import pdb
import datetime
import pandas as pd
import numpy as np
import featurizer
import matplotlib.pyplot as plt
import os
import time
import cv2

# define database names and reused feature names
db_frames = 'frames'
db_model_scores = 'model_scores'
db_users = 'users'
db_conf_preds = 'confident_preds'
instance = 'instance'
user_id = 'user_id'
root_dir = 'root_dir'
pred_gest = 'pred_gest'
true_gest = 'true_gest'
pred_conf= 'pred_conf'
processed_path = 'processed_path'

# select all high-scoring predictions. These will be used to train new models. 
config_name = 'development' # not sure if necessary
conn = psycopg2.connect(host=config[config_name].DB_HOST, database=config[config_name].DB_USER, user=config[config_name].DB_USER, password=config[config_name].DB_PASS)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
confidence_threshold = 99
features = f'{instance}, {user_id}, {pred_gest}, {true_gest}, {pred_conf}, {root_dir}, {processed_path}'
query = 'SELECT ' + features + f' FROM {db_frames} WHERE {pred_conf} > {confidence_threshold}'
cur.execute(query)
conn.commit()
rows = cur.fetchall()

# make dataframe for high-scoring predictions that includes rotated images. Rotated images will enhance training results. 
columns = [feature.strip() for feature in features.split(",")]
df = pd.DataFrame(rows, columns=columns)
df = df.drop(pred_conf, axis=1)
df = df[df.notnull()]

# generate rotated images, save files to file storage system, append paths to dataframe
processed_path = 'processed_path'
flipped_path = 'flipped_path'
mirrored_path = 'mirrored_path'
mirrored_flipped_path = 'mirrored_flipped_path'
rotated_image_path_feats = [flipped_path, mirrored_path, mirrored_flipped_path]
for feat in rotated_image_path_feats:
    df[feat] = None
df_feats = [instance, user_id, root_dir]
start_time = time.time()
for i in range(len(df)):
    orig_path = df[processed_path][i]
    frame_orig = cv2.imread(orig_path)
    (_, frame_orig) = cv2.threshold(frame_orig, 127, 255, cv2.THRESH_BINARY)
    row_orig = df.iloc[i]
    rotate_dict = featurizer.rotate(frame_orig, row_orig, df_feats)
    rotate_keys = list(rotate_dict.keys())
    root_dir_path = row_orig[root_dir]
    rotated_dir = os.path.join(root_dir_path, 'rotated')
    if os.path.isdir(rotated_dir) == False:
        print('[INFO] Creating directory for rotated images.')
        os.mkdir(rotated_dir)
    user_id_num = str(row_orig[user_id])
    user_dir = os.path.join(rotated_dir, str(user_id_num))
    if os.path.isdir(user_dir) == False:
        print(f'[INFO] Creating directory for rotated images from user {user_id_num}.')
        os.mkdir(user_dir)
    for key in rotate_keys:
        frame = rotate_dict[key]['frame']
        path = rotate_dict[key]['path']
        cv2.imwrite(path, frame)
        try:
            column = key + '_path'
            df[column][i] = path
        except:
            print('[ERROR] Unable to save rotated image path to database or dataframe')
print(f'[INFO] Processing rotated images took {time.time() - start_time} seconds')

# drop user_id and root_dir from data frame
df = df.drop([user_id, root_dir], axis=1) 

# add table to database
from sqlalchemy import create_engine
engine = create_engine("postgresql://{user}:{pw}@{host}/{name}".format(host=config[config_name].DB_HOST, user=config[config_name].DB_USER, pw=config[config_name].DB_PASS, name=config[config_name].DB_NAME))
table = 'conf_preds'
try: 
    df.to_sql(table, con=engine, if_exists='replace')
except: 
    print("[ERROR] Unable to add confident predictions table to database. Duplicate key(s) found.")

# generate new table with image paths transposed for convenient model training
df_conf_preds = pd.DataFrame()
for i in range(len(df)):
    row = df.iloc[i]
    instance_val = row[instance]
    pred_gest_val = row[pred_gest]
    true_gest_val = row[true_gest]
    # append row for each file path. the predicted and true gestures of each file are the same
    df_conf_preds = df_conf_preds.append([[instance_val + '_og', pred_gest_val, true_gest_val, row[processed_path]]], ignore_index=True)
    df_conf_preds = df_conf_preds.append([[instance_val + '_f', pred_gest_val, true_gest_val, row[flipped_path]]], ignore_index=True)
    df_conf_preds = df_conf_preds.append([[instance_val + '_m', pred_gest_val, true_gest_val, row[mirrored_path]]], ignore_index=True)
    df_conf_preds = df_conf_preds.append([[instance_val + '_mf', pred_gest_val, true_gest_val, row[mirrored_flipped_path]]], ignore_index=True)
df_conf_preds = df_conf_preds.rename(columns={0: instance, 1: pred_gest, 2: true_gest, 3: 'path'})

# define x_data, y_data
from keras.utils import to_categorical
from objects import gestures_map

x_data = np.array(df_conf_preds['path'])
y_data = df_conf_preds[true_gest]
for cat in list(gestures_map.keys()):
    gesture_name = gestures_map[cat]
    y_data = y_data.replace(gesture_name, cat)
y_data = np.array(y_data)
y_data = to_categorical(y_data, num_classes=len(gestures_map.keys()))

# train-test split
from sklearn.model_selection import train_test_split
x_train_path, x_val_path, y_train, y_val = train_test_split(x_data, y_data, test_size=0.2, stratify=y_data)

# build model
from builder import build_and_save_model
model_dir = os.path.join(os.path.dirname( __file__), 'models')
model_path = build_and_save_model(x_train_path, y_train, model_dir) # wait until data collection infrastructure in place to train new models

# evaluate model performance and add results to database
from evaluator import evaluate_models
df_results = evaluate_models(model_dir, x_val_path, y_val)
table = 'model_scores'
try: 
    df_results.to_sql(table, con=engine, if_exists='append')
except:
    print("[ERROR] Duplicate completion time(s) found. Unable to commit results.")
try:     
    query = f'ALTER TABLE {table} ADD PRIMARY KEY (testing_completion_time);'
    cur.execute(query)
    conn.commit()
except: 
    print("[WARNING] Unable to alter table. Primary key already set.")