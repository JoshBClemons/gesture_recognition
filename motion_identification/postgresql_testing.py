import psycopg2
import psycopg2.extras
import pdb

DB_HOST = 'localhost'
DB_USER = 'postgres'
DB_PASS = 'temp_pass'
DB_NAME = 'postgres'
conn = psycopg2.connect(host=DB_HOST, database=DB_USER, user=DB_USER, password=DB_PASS)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

cur.execute("""
    DROP TABLE IF EXISTS testing
""")
conn.commit()
cur.execute("""
    CREATE TABLE testing(id NUMERIC PRIMARY KEY, name TEXT NOT NULL)
""")
conn.commit()

# check port
cur.execute("""SELECT * FROM pg_settings WHERE name = 'port';""")
conn.commit()
results = cur.fetchall()
print(results)
pdb.set_trace()
