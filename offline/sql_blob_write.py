import pdb
import psycopg2
from psycopg2.extras import Json, DictCursor
import datetime

DB_HOST = 'localhost'
DB_USER = 'postgres'
DB_PASS = 'temporary_password'
DB_NAME = 'postgres'

conn = psycopg2.connect(host=DB_HOST, database=DB_USER, user=DB_USER, password=DB_PASS)
cur = conn.cursor(cursor_factory=DictCursor)

# create table
table = 'models'
cur.execute("""
    DROP TABLE IF EXISTS models
""")
conn.commit()
query = f'CREATE TABLE {table}(training_date date, rank integer, prev_rank integer, gestures_map jsonb, model bytea);'
cur.execute(query)
conn.commit()

# process model - TEMP 
path_to_file = 'C://Users//clemo//git//gesture_recognition//offline//models//current_model.h5'
model = open(path_to_file, 'rb').read()

blob = psycopg2.Binary(model)
training_date = datetime.datetime.now()
rank = 1 # normally -1
prev_rank = -1
gestures_map = {0: 'open palm',
                1: 'closed palm',
                2: 'L',
                3: 'fist',
                4: 'thumbs up',
                }
# ::json

gestures_map = Json(gestures_map)

# write model
query = f"INSERT INTO {table}(training_date, rank, prev_rank, gestures_map, model) VALUES('{training_date}', {rank}, {prev_rank}, {gestures_map}, {blob})"
pdb.set_trace()
cur.execute(query)
conn.commit()
cur.close()

# models table features
# training_date
# rank = -1 --> evaluator file reranks files based on current performance
# prev_rank = -1 --> evaluator file reranks based on current performance and stores prev_rank if rank was != -1
# model = blob(model)