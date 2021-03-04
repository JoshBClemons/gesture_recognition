import pdb
import psycopg2
import psycopg2.extras

DB_HOST = 'localhost'
DB_USER = 'postgres'
DB_PASS = 'temporary_password'
DB_NAME = 'postgres'

conn = psycopg2.connect(host=DB_HOST, database=DB_USER, user=DB_USER, password=DB_PASS)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# create table
table = 'models'
cur.execute("""
    DROP TABLE IF EXISTS models
""")
conn.commit()
query = f'CREATE TABLE {table}(name text, model bytea);'
cur.execute(query)
conn.commit()

# process model
path_to_file = 'C://Users//clemo//git//gesture_recognition//offline//models//current_model.h5'
# read data from a picture
model = open(path_to_file, 'rb').read()
blob = psycopg2.Binary(model)
blob_name = 'current_model'

# write model
query = f"INSERT INTO {table}(name, model) VALUES('{blob_name}', {blob})"
cur.execute(query)
conn.commit()
cur.close()