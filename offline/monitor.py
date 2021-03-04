import config
import psycopg2
import psycopg2.extras
import pdb
import pandas as pd
import numpy as np
from objects import gestures_map
from sklearn.metrics import classification_report, confusion_matrix, f1_score

# gather necessary data from main and model_scores tables
conn = psycopg2.connect(host=config.DB_HOST, database=config.DB_USER, user=config.DB_USER, password=config.DB_PASS)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# gather model_scores information for highest performing models
query = "SELECT testing_completion_time, true_gestures::int[], predicted_gestures::int[] FROM model_scores ORDER BY f1_score DESC LIMIT 3" 
cur.execute(query)
conn.commit()
rows = cur.fetchall()

# generate dataframe for model scores
columns = ['testing_completion_time', 'true_gest', 'pred_gest']
df_model_scores = pd.DataFrame(rows, columns=columns)

# compute classification report and confusion matrix
labels = list(gestures_map.values())
for i in range(len(df_model_scores)):
    y_true = np.array(df_model_scores.iloc[i]['true_gest'])
    y_pred = np.array(df_model_scores.iloc[i]['pred_gest'])
    print(classification_report(y_true, y_pred, target_names=labels))
    print(pd.DataFrame(confusion_matrix(y_true, y_pred), index=labels, columns=labels))

# gather historical and current user and gesture information
query = "SELECT date, user_id, true_gest, pred_gest, pred_time FROM main" 
cur.execute(query)
conn.commit()
rows = cur.fetchall()

# generate dataframe for historical information
columns = ['date', 'user_id', 'true_gest', 'pred_gest', 'pred_time']
df_history = pd.DataFrame(rows, columns=columns)
print(df_history)

# add operations per instructions below...
# MODEL REPORTS -- model_scores
    # classification report
    # confusion matrix for models with highest f1 scores (need to add to table)

    # model_scores
    # testing_completion time
    # true_gestures
    # predicted_gestures


# MOST POPULAR GESTURES -- main
    # bar chart showing relative popularity of different gestures over time 

    # table: main
    # date
    # true_gest

# TOP USERS
    # chart showing top users over time
    # measured by connect / disconnection of server (final-first prediction for now)
# number of users per time 
    # time-response of # of users online as measured by active socket connection (prediction in last minute for now)

    # table: main
    # date
    # user_id 

# PREDICTION TIME WITH TIME 
    # time-response plot of prediction time
    # informs when system is experiencing high usage 
    # bin by the minute 

    # table: main
    # pred_time 
    # date

# PREDICTION ACCURACY WITH TIME 
    # bar chart showing prediction accuracy for different gestures
    
    # table: main
    # pred_gest
    # true_gest
    # date

# (MAYBE) locations of users over time?