from config import Config
import psycopg2
from psycopg2.extras import Json, DictCursor
import pdb
import os
import datetime

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

# create table for model scores (temp fake values)
table = 'model_scores'
query = f'DROP TABLE IF EXISTS {table};'
cur.execute(query)
conn.commit()

from sqlalchemy import create_engine
import pandas as pd
f1 = 1 
rank = 1
eval_time = 10 
true_gestures = [1,2,3,4,0,3,4,2,3,4,2,1,2,3,0]
pred_gestures = [1,2,3,4,0,3,4,2,3,4,2,1,2,3,0]
model_name = 'model_0'
training_date = datetime.datetime(2021, 2, 1, 0, 0)
engine = create_engine("postgresql://{user}:{pw}@{host}/{name}".format(host=Config.DB_HOST, user=Config.DB_USER, pw=Config.DB_PASS, name=Config.DB_NAME))
model_results = [model_name, f1, rank, training_date, eval_time, true_gestures, pred_gestures]
sql_model_scores = pd.DataFrame([model_results])
sql_model_scores = sql_model_scores.rename(columns={0:'model_name', 1:'f1_score', 2:'rank', 3:'evaluation_date', 4:'evaluation_time', 5:'true_gestures', 6:'predicted_gestures'})
sql_model_scores.to_sql(table, con=engine, if_exists='replace', index=False)
engine.dispose()
print(f'[INFO] Created and added original model score to table {table}')

# add original model to "models" table
from objects import gestures_map
gestures_map = Json(gestures_map)
model_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'models')
model_filename = 'original_model.h5'
model_path = os.path.join(model_dir, model_filename)
model = open(model_path, 'rb').read()
model_blob = psycopg2.Binary(model)
table = 'models'
query = f"INSERT INTO {table}(model_name, training_date, gestures_map, model, model_path) VALUES('{model_name}', '{training_date}', {gestures_map}, {model_blob}, '{model_path}')"
cur.execute(query)
conn.commit()
print(f'[INFO] Added original model to {table}')

# close db connection
cur.close()

# # rename table using SQL column names
# query = f"SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}';"
# cur.execute(query)
# conn.commit()
# columns = []
# for row in cur.fetchall(): 
#     columns.append(row[3])