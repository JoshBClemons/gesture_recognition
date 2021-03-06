import pdb
from config import Config
import psycopg2
import psycopg2.extras
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import os
from matplotlib.dates import date2num
from matplotlib import pyplot as plt
import time
import copy
import datetime
import math
import json
import warnings
warnings.filterwarnings('ignore')
import seaborn as sns
sns.set_style("whitegrid")
sns.set_context("poster")

# generate list of gestures
with open(Config.GESTURES_MAP_PATH,'r') as f:
    gestures_map = json.load(f)
gestures = list(gestures_map.values())

# define static file image directory to store figures
figure_dir = Config.FIGURE_DIRECTORY

def update_stats():
    """Update usage and model statistics"""
   
    # pull data from model_scores and frames tables
    conn = psycopg2.connect(host=Config.DB_HOST, database=Config.DB_NAME, user=Config.DB_USER, password=Config.DB_PASS)
    query = "SELECT * FROM model_scores" 
    df_model_scores = pd.read_sql(query, con=conn)
    query = "SELECT * FROM frames"
    df_frames = pd.read_sql(query, con=conn)

    # update figures and statistics if there are frames in database, otherwise skip
    if not df_frames.empty and not df_frames[df_frames['true_gest']!=''].empty:

        # evaluate - most popular gestures
        # There may be trends in which gestures are popular depending on time of day, location, etc.
        
        # reduce date to year, month, date
        df_frame_gest_pop = copy.deepcopy(df_frames)
        df_frame_gest_pop['date'] = df_frame_gest_pop['date'].dt.date

        # get counts of each gesture for each date
        gestures_with_time = df_frame_gest_pop[['true_gest','date']][df_frame_gest_pop['true_gest']!='']
        
        # skip if no "true gestures" have been inputted by users
        if not gestures_with_time.empty:
            gestures_with_time = pd.DataFrame(gestures_with_time.value_counts())
            gestures_with_time.reset_index(level=0, inplace=True)
            gestures_with_time = gestures_with_time.sort_values('date')
            gestures_with_time.reset_index(level=0, inplace=True)
            gestures_with_time = gestures_with_time.rename(columns={0: 'counts'})

            # generate label for each unique date
            labels = []
            dates = gestures_with_time['date'].unique()
            for date in dates:
                labels.append(date.strftime("%Y-%m-%d"))

            # generate dictionary containing gesture count and relative frequency of each gesture for each date
            gesture_dict = {}
            for gesture in gestures_with_time['true_gest'].unique():
                gesture_dict[gesture] = {}
                gesture_dict[gesture]['counts'] = [0 for _ in range(len(dates))]
                gesture_dict[gesture]['percentages'] = [0 for _ in range(len(dates))]
            date_total_gestures = gestures_with_time.groupby('date').sum()['counts']
            date_index = 0
            for i in range(len(gestures_with_time)):
                try:
                    if gestures_with_time['date'][i-1] != gestures_with_time['date'][i]:
                        date_index += 1
                except:
                    pass
                gesture_counts = gestures_with_time['counts'][i]
                gesture = gestures_with_time['true_gest'][i]
                gesture_dict[gesture]['counts'][date_index] = gesture_counts
                gesture_dict[gesture]['percentages'][date_index] = gesture_counts*100 / date_total_gestures[date_index]
            
            # generate bar chart showing relative frequency of different gestures over time 
            fig, ax = plt.subplots(figsize=(6,8))
            width = 0.2
            prev_gesture_counts = [0 for _ in range(len(dates))]
            total_height = [0 for _ in range(len(dates))]
            for gesture in gesture_dict.keys():
                gesture_counts = gesture_dict[gesture]['counts']
                if prev_gesture_counts == [0 for _ in range(len(dates))]:
                    ax.bar(labels, gesture_counts, width=width, label=gesture)
                elif prev_gesture_counts != [0 for _ in range(len(dates))]:
                    ax.bar(labels, gesture_counts, width=width, bottom=prev_gesture_counts, label=gesture)
                prev_gesture_counts = [sum(x) for x in zip(prev_gesture_counts, gesture_counts)]
                count = 0
                gesture_percentages = gesture_dict[gesture]['percentages']
                for j in ax.patches[-len(dates):]:
                    width, height = j.get_width(), j.get_height()
                    x, y = j.get_xy() 
                    ax.text(x+width/2, y+height/2, '{:.0f} %'.format(gesture_percentages[count]), fontsize=16, horizontalalignment='center', verticalalignment='center')
                    total_height[count] += height
                    count+=1            
            ceiling = math.ceil(max(total_height)*1.25)
            ceiling_round_up = int(math.ceil(ceiling/100.0))*100
            step = 50
            num_steps = int(ceiling_round_up/step+1)
            yticks = np.linspace(0, ceiling_round_up, num_steps)
            ax.set_ylabel('True Gesture Counts')
            ax.set_xlabel('Date')
            ax.set_title('True Gesture Counts by Date')
            ax.set_yticks(yticks)
            ax.tick_params(labelsize=15, labelrotation=0, grid_alpha=0.2, axis='both', which='major', direction='out', length=6, width=2, left=True, bottom=True)
            ax.legend(loc='upper right', fontsize=12)
            
            # save figure
            file_name = Config.OTHER_FIGURE_NAMES[3] + '.png'
            file_path = os.path.join(figure_dir, file_name)
            plt.savefig(file_path, bbox_inches='tight')
            plt.close()


        # evaluate - classification report and confusion matrix for each model
        # This informs of relative performance of top 3 models. Perhaps some are better at predicting certain gestures compared to others

        # loop across each model
        labels = list(gestures_map.values())
        for i in range(min(len(df_model_scores), 3)):
            y_true = eval(df_model_scores['true_gestures'][i].replace('{','[').replace('}',']'))
            y_pred = eval(df_model_scores['predicted_gestures'][i].replace('{','[').replace('}',']'))
            model_name = df_model_scores['model_name'][i]
            eval_date = df_model_scores['evaluation_date'][i]

            # generate and save classification_report as json
            report = classification_report(y_true, y_pred, target_names=labels, zero_division=0, output_dict=True)
            df_report = pd.DataFrame(report).transpose()
            caption = f'Classification Report for {model_name} <br> (trained {eval_date})'
            df_report_json = df_report.to_json(orient="split")
            output_dict = json.loads(df_report_json)
            output_dict['caption'] = caption
            file_name = f'{Config.CR_FIGURE_NAMES[i]}.json'
            file_path = os.path.join(figure_dir, file_name)
            with open(file_path, 'w') as fp:
                json.dump(output_dict, fp)

            # generate and save confusion matrix as json
            df_confusion_matrix = pd.DataFrame(confusion_matrix(y_true, y_pred), columns=labels, index=labels)
            caption = f'Confusion Matrix for {model_name} <br> (trained {eval_date})'
            df_confusion_matrix_json = df_confusion_matrix.to_json(orient="split")
            output_dict = json.loads(df_confusion_matrix_json)
            output_dict['caption'] = caption
            file_name = f'{Config.CM_FIGURE_NAMES[i]}.json'
            file_path = os.path.join(figure_dir, file_name)
            with open(file_path, 'w') as fp:
                json.dump(output_dict, fp)


        # evaluate - user daily usage
        # It may be valuable to know which users are using the application most, if there are notable trends with respect to user usage, etc. This should be modified such that users that comprise consume less than 5% of total usage are merged to a single group. 

        # get duration spent by each user for each date
        user_session_info = df_frames.groupby(['user_id', 'session_id']).agg({'date': ['min', 'max']})
        user_session_info.columns = user_session_info.columns.droplevel(0)
        user_session_info.reset_index(level=[0,1], inplace=True)
        user_session_info['duration'] = (user_session_info['max'] - user_session_info['min']).dt.total_seconds()
        user_session_info['date'] = user_session_info['min'].dt.date
        user_session_info = user_session_info.drop(['max', 'min'], axis=1)

        # generate label for each unique date
        labels = []
        dates = user_session_info['date'].unique()
        for date in dates:
            labels.append(date.strftime("%Y-%m-%d"))

        # add blank entries for users that do not login on any given date. This is necessary for generating the stacked bar plot cleanly
        for date in user_session_info['date'].unique():
            for user in user_session_info['user_id'].unique():
                if date not in list(user_session_info[user_session_info['user_id'] == user]['date']):
                    blank_entry = [user, 0, 0, date]
                    blank_df = pd.DataFrame([blank_entry], columns=list(user_session_info.columns))
                    user_session_info = user_session_info.append([blank_df], ignore_index=True)
        user_session_info = user_session_info.groupby(['date', 'user_id']).sum()
        user_session_info['duration'] = user_session_info['duration'].astype(int)
        user_session_info.reset_index(level=[0,1], inplace=True)

        # generate dictionary containing total usage duration and percentage of total time for each user for each date
        user_dict = {}
        for user in user_session_info['user_id'].unique():
            user_dict[user] = {}
            user_dict[user]['duration'] = [0 for _ in range(len(dates))]
            user_dict[user]['percentages'] = [0 for _ in range(len(dates))]
        date_total_duration = user_session_info.groupby('date').sum()['duration']
        date_index = 0
        for i in range(len(user_session_info)):
            try:
                if user_session_info['date'][i-1] != user_session_info['date'][i]:
                    date_index += 1
            except:
                pass
            user_durations = user_session_info['duration'][i]
            user = user_session_info['user_id'][i]
            user_dict[user]['duration'][date_index] = user_durations
            user_dict[user]['percentages'][date_index] = user_durations*100 / date_total_duration[date_index]

        # generate bar chart showing relative user activity over time
        fig, ax = plt.subplots(figsize=(6,8))
        width = 0.2
        prev_user_durations = [0 for _ in range(len(dates))]
        total_height = [0 for _ in range(len(dates))]
        for user in user_dict.keys():
            user_durations = user_dict[user]['duration']
            if prev_user_durations == [0 for _ in range(len(dates))]:
                ax.bar(labels, user_durations, width=width, label=user)
            elif prev_gesture_counts != [0 for _ in range(len(dates))]:
                ax.bar(labels, user_durations, width=width, bottom=prev_user_durations, label=user)
            prev_user_durations = [sum(x) for x in zip(prev_user_durations, user_durations)]
            count = 0
            user_percentages = user_dict[user]['percentages']
            for j in ax.patches[-len(dates):]:
                width, height = j.get_width(), j.get_height()
                x, y = j.get_xy() 
                ax.text(x+width/2, y+height/2, '{:.0f} %'.format(user_percentages[count]), fontsize=16, horizontalalignment='center', verticalalignment='center')
                total_height[count] += height
                count+=1       
        ceiling = math.ceil(max(total_height)*1.5)
        ceiling_round_up = int(math.ceil(ceiling_round_up/100.0))*100
        step = 100
        num_steps = int(ceiling_round_up/step+1)
        yticks = np.linspace(0, ceiling_round_up, num_steps)
        ax.set_ylabel('Combined User Usage Time (seconds)')
        ax.set_xlabel('Date')
        ax.set_title('Combined User Usage Time by Date')
        ax.set_yticks(yticks)
        ax.tick_params(labelsize=15, labelrotation=0, grid_alpha=0.2, axis='both', which='major', direction='out', length=6, width=2, left=True, bottom=True)
        ax.legend(loc='upper right', fontsize=12)

        # save figure
        file_name = Config.OTHER_FIGURE_NAMES[2] + '.png'
        file_path = os.path.join(figure_dir, file_name)
        plt.savefig(file_path, bbox_inches='tight')
        plt.close()


        # evaluate - total daily user activity
        # It is always good to know which times of day most users are using the product to inform advertising strategy or future product development.
        
        # generate df containing number of users during each minute
        df_users_per_minute = df_frames[['date', 'user_id']]
        df_users_per_minute = df_users_per_minute[df_users_per_minute['date'].dt.date == datetime.datetime.now().date()]
        df_users_per_minute['date'] = df_users_per_minute['date'].dt.floor('Min')
        df_users_per_minute = pd.DataFrame(df_users_per_minute.drop_duplicates()['date'].value_counts())
        df_users_per_minute.reset_index(level=0, inplace=True)
        df_users_per_minute = df_users_per_minute.rename(columns={'index': 'date', 'date': 'user_count'})
        df_users_per_minute = df_users_per_minute.sort_values('date', ignore_index=True)

        # define x-axis limits and labels. plot will show statisticss for every 30 minutes of today only. need to modify to account for end of month / year
        start = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, 0, 0, 0)
        end = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day+1, 0, 0, 0)
        x_lims = pd.date_range(start, end, periods=49).to_pydatetime()
        x_labels = []
        for i in range(len(x_lims)):
            if i%2 != 0:
                x_labels.append(x_lims[i].strftime('%H:%M'))
            else: 
                x_labels.append('')

        # plot results
        fig, ax = plt.subplots(figsize= (16,3))
        ax.bar(x=df_users_per_minute['date'], height=df_users_per_minute['user_count'], width=0.05)
        ax.set_xlabel('Time of Day [PST]', fontsize=20)
        ax.set_ylabel('Number of Active Users', fontsize=20)
        ax.set_title("Today's User Activity")
        ax.set_xticks(x_lims)
        ax.set_xticklabels(x_labels)
        ax.tick_params(labelsize=12, labelrotation=0, grid_alpha=0.2, axis='both', which='major', direction='out', length=6, width=2, left=True, bottom=True)

        # save file
        file_name = Config.OTHER_FIGURE_NAMES[0] + '.png'
        file_path = os.path.join(figure_dir, file_name)
        plt.savefig(file_path, bbox_inches='tight')
        plt.close()


        # evaluate - daily prediction accuracy for each gesture
        # This informs us about which gestures are more difficult to predict than others. A significant change in gesture prediction accuracy may correlate with a change in which model is currently implemented.

        # generate table with prediction accuracy for each gesture
        df_gest_acc_by_date = df_frames[df_frames['true_gest'] != ''][['date', 'true_gest', 'pred_gest']]
        
        # skip if no "true gestures" have been inputted by users
        if not df_gest_acc_by_date.empty:
            df_gest_acc_by_date['date'] = df_gest_acc_by_date['date'].dt.floor('D')
            column_names = []
            valid_gestures = df_gest_acc_by_date['true_gest'].unique()
            for gesture in valid_gestures:
                df_temp = df_gest_acc_by_date[df_gest_acc_by_date['true_gest'] == gesture]
                column_name = gesture + ' acc'
                df_temp[column_name] = df_temp['pred_gest'] == gesture
                df_temp = df_temp[['date', column_name]]
                df_temp = pd.DataFrame(df_temp.groupby('date')[column_name].mean())
                df_temp.reset_index(level=0, inplace=True)
                try: 
                    df_combined_acc = df_combined_acc.merge(df_temp, how='outer', on='date')
                except:
                    df_combined_acc = copy.deepcopy(df_temp)

            # define x-axis limits and labels. plot will show statistics for each day
            start = df_gest_acc_by_date['date'].min()
            end = df_gest_acc_by_date['date'].max()
            x_lims = pd.date_range(start, end, freq='D').to_pydatetime()
            x_labels = []
            for i in range(len(x_lims)):
                x_labels.append(x_lims[i].strftime('%D'))

            # generate bar chart showing prediction accuracy for different gestures
            fig, ax = plt.subplots(figsize= (6,8))
            width = 0.05
            gesture_cols = list(df_combined_acc.columns)[1:]
            for i in range(len(valid_gestures)):
                gesture = valid_gestures[i]
                test = date2num(df_combined_acc['date'])+width*(i-(len(valid_gestures)-1)/2)
                ax.bar(x=test, height=df_combined_acc[gesture_cols[i]], width=width, label=gesture)

            ax.set_xlabel('Date')
            ax.set_xticks(x_lims)
            ax.set_xticklabels(x_labels)
            ax.set_ylabel('Prediction Accuracy (%)', fontsize=20)
            ylims = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.25]
            ax.set_yticks(ylims)
            ax.set_title("Gesture Prediction Accuracy by Date")
            ax.legend(loc='upper right', fontsize=14)
            ax.tick_params(labelsize=12, labelrotation=0, grid_alpha=0.2, axis='both', which='major', direction='out', length=6, width=2, left=True, bottom=True)

            # save figure
            file_name = Config.OTHER_FIGURE_NAMES[1] + '.png'
            file_path = os.path.join(figure_dir, file_name)
            plt.savefig(file_path, bbox_inches='tight')
            plt.close()

        # print completion time 
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        message = f'Activity statistics updated at {time}'
        print('[INFO] ' + message)    
    else:
        message = f'No frames collected yet. No statistics to compute.'
        print('[INFO] ' + message)

    # save summary message
    file = open(Config.STATS_MESSAGE_PATH,"w") 
    file.write(message) 
    file.close()

## Additional plots to make
# Show where users are based on IP address
# Plot request/ response processing time throughout the day. This may correlate with peak usage times