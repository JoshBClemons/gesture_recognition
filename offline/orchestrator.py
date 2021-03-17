from config import Config
import psycopg2
from psycopg2.extras import Json, DictCursor
import pdb
import pandas as pd
import os
import time
import cv2
from gesture_recognition import featurizer

def orchestrator():
    """Pull frames with confidence, accurate predictions from database and use them to generate new model."""

    # define database names
    db_frames = 'frames'
    db_model_scores = 'model_scores'
    db_users = 'users'
    db_conf_preds = 'confident_preds'

    # define feature names 
    instance = 'instance'
    user_id = 'user_id'
    root_dir = 'root_dir'
    pred_gest = 'pred_gest'
    true_gest = 'true_gest'
    pred_conf= 'pred_conf'
    processed_path = 'processed_path'

    # select all high-scoring predictions. These will be used to train new models. 
    conn = psycopg2.connect(host=Config.DB_HOST, database=Config.DB_NAME, user=Config.DB_USER, password=Config.DB_PASS)
    cur = conn.cursor(cursor_factory=DictCursor)
    confidence_threshold = 0 # way too low; used for testing
    features = f'{instance}, {user_id}, {true_gest}, {pred_conf}, {root_dir}, {processed_path}'
    query = 'SELECT ' + features + f' FROM {db_frames} WHERE {pred_conf} > {confidence_threshold} AND {pred_gest} = {true_gest}'
    cur.execute(query)
    conn.commit()
    rows = cur.fetchall()

    # make dataframe for high-scoring predictions that includes rotated images. Rotated images will enhance training results. 
    columns = [feature.strip() for feature in features.split(",")]
    df = pd.DataFrame(rows, columns=columns)
    df = df.drop(pred_conf, axis=1)
    df = df[df.notnull()]
    
    # exit if no frames in database
    if df.empty:
        print(f'[ERROR] No accurately predicted frames with prediction confidence > {confidence_threshold} in {db_frames}.')
        cur.close()
    else: 
        print(f'[INFO] Confident predictions pulled from {db_frames} table.')

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
        df = df.rename(columns={'true_gest': 'gesture'})

        # add table of confident predictions to database
        from sqlalchemy import create_engine
        engine = create_engine("postgresql://{user}:{pw}@{host}/{name}".format(host=Config.DB_HOST, user=Config.DB_USER, pw=Config.DB_PASS, name=Config.DB_NAME))
        table = 'conf_preds'
        df.to_sql(table, con=engine, if_exists='replace', index=False) # would be better to append existing table conf_preds but current design processes all images from database rather than just new ones. Will update in the future. 
        print(f'[INFO] Table of confident predictions updated.')

        # check if sufficient number of each gesture present in table of confident predictions. If not, exit since a new model cannot be trained
        from objects import gestures_map # may place gestures_map on database. stored models should be saved with gestures_map they correspond with. example: train new model with additional gestures 
        gestures_list = list(gestures_map.values())
        df_gestures_list = list(df['gesture'].unique())
        differing_gestures = [gesture for gesture in gestures_list if gesture not in df_gestures_list]
        if differing_gestures != []:
            print(f'[ERROR] Not enough confident predictions have been made for {differing_gestures}. Unable to split data.')
            return

        # generate new table with image paths transposed for convenient model training
        df_conf_preds = pd.DataFrame()
        for i in range(len(df)):
            row = df.iloc[i]
            instance_val = row[instance]
            gesture_val = row['gesture']

            # append row for each file path. the predicted and true gestures of each file are the same
            df_conf_preds = df_conf_preds.append([[instance_val + '_og', gesture_val, row[processed_path]]], ignore_index=True)
            df_conf_preds = df_conf_preds.append([[instance_val + '_f', gesture_val, row[flipped_path]]], ignore_index=True)
            df_conf_preds = df_conf_preds.append([[instance_val + '_m', gesture_val, row[mirrored_path]]], ignore_index=True)
            df_conf_preds = df_conf_preds.append([[instance_val + '_mf', gesture_val, row[mirrored_flipped_path]]], ignore_index=True)
        df_conf_preds = df_conf_preds.rename(columns={0: instance, 1: 'gesture', 2: 'path'})    

        # form y_data from confident predictions dataframe 
        from keras.utils import to_categorical
        y_data = df_conf_preds['gesture']
        for cat in list(gestures_map.keys()):
            gesture_name = gestures_map[cat]
            y_data = y_data.replace(gesture_name, cat)
        y_data = to_categorical(y_data, num_classes=len(gestures_map.keys()))
        y_data = pd.DataFrame(y_data)

        # reduce table size to count of least occurring gesture
        import random
        driving_count = -1
        for i in y_data.columns:
            gesture_count = len(y_data[y_data[i] == 1][i])
            if gesture_count < driving_count or driving_count == -1:
                driving_count = gesture_count
        indices = []
        for i in y_data.columns: 
            gesture_indices = list(y_data[y_data[i] == 1][i].index); 
            sample_indices = random.sample(gesture_indices, driving_count); 
            indices.extend(sample_indices)
        y_data = y_data.iloc[indices]

        # form x_data from confident predictions dataframe. Size of x_data driven by least occuring gesture 
        x_data = df_conf_preds['path'].iloc[indices]

        # split data into training (72%), validation (8%), and testing (20%) sets 
        test_size = 0.2
        if len(x_data) < len(gestures_list)/test_size:
            print(f'[ERROR] Not enough confident predictions have been made. Unable to split data.')
            return
        from sklearn.model_selection import train_test_split
        x_train_paths, x_test_paths, y_train, y_test = train_test_split(x_data, y_data, test_size=0.2, stratify=y_data)
        x_train_paths, x_val_paths, y_train, y_val = train_test_split(x_train_paths, y_train, test_size=0.1, stratify=y_train)
        print(f'[INFO] Prepared training data. Building model...')

        # build model
        from .builder import build_and_save_model
        from objects import gestures_map # ideally, the gesture map should be capable of dynamically impacting the training cycle. However, I am assuming the set of predicted gestures will not change 
        model_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'models')
        [model_path, training_date] = build_and_save_model(x_train_paths, x_val_paths, y_train, y_val, model_dir) # wait until data collection infrastructure in place to train new models
        
        # determine model_name based on entries in database
        query = 'SELECT model_name from models'
        cur.execute(query)
        conn.commit()
        rows = cur.fetchall()
        if rows == []:
            model_name = 'model_0'
        else:
            name_start = 'model_'
            last_num = int(rows[-1][0].split(name_start)[1])
            model_name = name_start + str(last_num+1)

        # push model to database
        gestures_map = Json(gestures_map)
        model = open(model_path, 'rb').read()
        model_blob = psycopg2.Binary(model)
        table = 'models'
        query = f"INSERT INTO {table}(model_name, training_date, gestures_map, model, model_path) VALUES('{model_name}', '{training_date}', {gestures_map}, {model_blob}, '{model_path}')"
        cur.execute(query)
        conn.commit()
        print(f'[INFO] New model stored in database.')

        # make dataframe containing all instances used to train new model 
        new_instances = df_conf_preds.loc[list(x_train_paths.index)]['instance'].sort_index()
        df_new_instances = pd.DataFrame(new_instances) 
        df_new_instances[model_name] = 1

        # update table that contains which frame instances were used to train which model(s)
        # In the long run, this table may be helpful for determining which training images correspond with accurate models 
        # There is likely a cleaner way to accomplish this  
        table = 'model_train_data_map'
        query = f"SELECT {instance} FROM {table}"
        cur.execute(query)
        conn.commit()
        sql_instances = cur.fetchall()
        if sql_instances != []:
            df_sql_instances = pd.DataFrame(sql_instances).rename(columns={0: "instance"})
            df_new_instances = df_new_instances.merge(df_sql_instances, how='outer', on='instance')

        # push temporary table to database that contains all training instances with instances used to train new model indicated with "1"
        new_instance = 'new_instance'
        df_new_instances = df_new_instances.rename(columns={instance: new_instance})
        new_table = 'new_table'
        df_new_instances.to_sql(new_table, con=engine, if_exists='replace', index=False)
        engine.dispose()
        
        # on database, merge newly created temporary table with original one 
        temp_table = 'temp_table'
        query = f"""
            DROP TABLE IF EXISTS {temp_table};
            SELECT * INTO {temp_table} FROM {new_table} LEFT JOIN {table} ON {instance}={new_instance};
            DROP TABLE IF EXISTS {new_table};
            ALTER TABLE {temp_table} DROP COLUMN {instance};
            ALTER TABLE {temp_table} RENAME COLUMN {new_instance} to {instance};
            DROP TABLE IF EXISTS {table};
            ALTER TABLE {temp_table} RENAME TO {table}
            """
        cur.execute(query)
        conn.commit()
        print(f'[INFO] Model / training data mapping table updated.')

        # evaluate model performance and compare with performance of other models
        from . import evaluator
        table = 'model_scores'
        query = f"SELECT * FROM {table}"
        cur.execute(query)
        conn.commit()
        sql_model_scores = pd.DataFrame(cur.fetchall())

        # close database connection
        cur.close()

        # evaluate new model and append scores to model score table
        [f1, eval_date, eval_time, y_true, y_pred] = evaluator.evaluate_model(model_path, x_test_paths, y_test)
        rank = 1
        model_results = [model_name, f1, rank, eval_date, eval_time, y_true, y_pred]
        sql_model_scores = sql_model_scores.append([model_results], ignore_index=True)
        sql_model_scores = sql_model_scores.rename(columns={0:'model_name', 1:'f1_score', 2:'rank', 3:'evaluation_date', 4:'evaluation_time', 5:'true_gestures', 6:'predicted_gestures'})
        
        # rank models by f1 score
        sql_model_scores = sql_model_scores.sort_values('f1_score', ascending=False, ignore_index=True)
        rank_vals = []
        for i in range(len(sql_model_scores)):
            rank_vals.append(i+1)
        sql_model_scores['rank'] = rank_vals

        # replace database table with new model scores
        engine = create_engine("postgresql://{user}:{pw}@{host}/{name}".format(host=Config.DB_HOST, user=Config.DB_USER, pw=Config.DB_PASS, name=Config.DB_NAME))
        sql_model_scores.to_sql(table, con=engine, if_exists='replace', index=False)
        engine.dispose()