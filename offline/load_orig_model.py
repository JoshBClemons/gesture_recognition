from config import Config
import psycopg2
from psycopg2.extras import Json, DictCursor
import pdb
import os
import datetime
conn = psycopg2.connect(host=Config.DB_HOST, database=Config.DB_NAME, user=Config.DB_USER, password=Config.DB_PASS)
cur = conn.cursor(cursor_factory=DictCursor)
table = 'model_scores'

def load_orig_model():
    """Upload originally trained model and model performance metrics to database"""
    
    global table
    from sqlalchemy import create_engine
    import pandas as pd
    f1 = 1 # temp fake value
    rank = 1
    eval_time = 10 # temp fake value
    true_gestures = [1,2,3,0,3,2,3,2,1,2,1,0] # temp fake values
    pred_gestures = [1,2,3,0,3,2,2,2,1,2,3,0] # temp fake values
    model_name = 'model_0'
    training_date = datetime.datetime(2021, 2, 1, 0, 0) # temp fake value
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

def check_orig_model():
    """Check if there are any models in database. If there are not, upload original model to database."""
    
    global table
    try:
        query = f"SELECT model_name FROM {table} WHERE rank = 1;"
        cur.execute(query)
        conn.commit()
        model_name = cur.fetchall()[0][0]

        # close db connection
        cur.close()
    except: 
        model_name = load_orig_model()
    print(f'[INFO] {model_name} loaded to {table} table.')