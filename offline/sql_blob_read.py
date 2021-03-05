import pdb
import psycopg2
import psycopg2.extras

DB_HOST = 'localhost'
DB_USER = 'postgres'
DB_PASS = 'temporary_password'
DB_NAME = 'postgres'

conn = psycopg2.connect(host=DB_HOST, database=DB_USER, user=DB_USER, password=DB_PASS)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# grab model
query = "SELECT * FROM models"
cur.execute(query)
conn.commit()

blob = cur.fetchone()
cur.close()

# save file
path_to_file = 'C://Users//clemo//git//gesture_recognition//offline//models//output_model.h5'
open(path_to_file, 'wb').write(blob[1])

# test model
from keras.models import load_model

# Import model
model = load_model(path_to_file)
pdb.set_trace()