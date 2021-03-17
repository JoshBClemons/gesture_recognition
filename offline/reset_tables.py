from config import Config
import psycopg2
from psycopg2.extras import Json, DictCursor
import pdb
import os
import datetime

def reset_tables():
    """Reset offline tables. This is necessary when first running application."""
    
    # select all high-scoring predictions. These will be used to train new models. 
    conn = psycopg2.connect(host=Config.DB_HOST, database=Config.DB_NAME, user=Config.DB_USER, password=Config.DB_PASS)
    cur = conn.cursor(cursor_factory=DictCursor)

    # create table for confident predictions
    table = 'conf_preds'
    query = f'DROP TABLE IF EXISTS {table};'
    cur.execute(query)
    conn.commit()
    query = f'CREATE TABLE {table}(instance text PRIMARY KEY NOT NULL, gesture text, processed_path text, flipped_path text, mirrored_path text, mirrored_flipped_path text);'
    cur.execute(query)
    conn.commit()
    print(f'[INFO] Created table {table}')

    # create table for newly trained models
    table = 'models'
    query = f'DROP TABLE IF EXISTS {table};'
    cur.execute(query)
    conn.commit()
    query = f'CREATE TABLE {table}(model_name text PRIMARY KEY NOT NULL, training_date date, gestures_map jsonb, model bytea, model_path text);'
    cur.execute(query)
    conn.commit()
    print(f'[INFO] Created table {table}')

    # create table mapping training data instances with models  
    table = 'model_train_data_map'
    query = f'DROP TABLE IF EXISTS {table};'
    cur.execute(query)
    conn.commit()
    query = f'CREATE TABLE {table}(instance text PRIMARY KEY NOT NULL, model_0 integer)'
    cur.execute(query)
    conn.commit()
    print(f'[INFO] Created table {table}')

    # create table for model scores
    table = 'model_scores'
    query = f'DROP TABLE IF EXISTS {table};'
    cur.execute(query)
    conn.commit()

    # load original model to model_scores table is not empty when application attempts to get table from it
    from . import load_orig_model
    load_orig_model.load_orig_model()

    # close db connection
    cur.close()