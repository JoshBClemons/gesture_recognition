"""
Steps to classify gestures
0) Divide initially recorded video into segments for each unique gesture performed. Save segments as name of gesture. It's important that each segment begins with view of unobstructed background
1) Modify inputs below to correspond to video file name and captured gesture 
2) start module. it will do the following
    - Opens video
    - captures and stores background image
    - removes background image from frames and saves them in folder corresponding to gesture. files are named as integers starting from 0
    - Saves each video frame in folder with integer file name starting from 0
"""

import time
import cv2
from threading import Thread
import datetime
import pdb
import json
import numpy as np
import os

testing = False

# Open and verify video
input_dir = 'C://Users//clemo//git//motion_identification//model_preparation//data_recordings'
input_file = 'thumbs_up'
input_type = '.mp4'
path = os.path.join(input_dir, input_file)
cap = cv2.VideoCapture(path+input_type)
if cap.read()[0] == False:
    raise Exception('Cannot locate video file')
print(f'Processing {input_file} data')

if testing == False:
    # Create directory to save images
    time = datetime.datetime.now().strftime("%Y_%m_%d_T%H_%M_%S")
    output_dir = time + '_' + input_file
    parent_dir = "C://Users//clemo//git//motion_identification//model_preparation//"
    path = os.path.join(parent_dir, output_dir) 
    os.mkdir(path) 

# create output dictionary and save directory 
frame_labels_dict = {}
frame_labels_dict['image_location'] = path

# define labels and acronyms
labels = ['open_palm', 'closed_palm', 'L', 'fist', 'thumbs_up']
acronyms = ['op', 'cp', 'l_', 'fi', 'tu']
label_set = list(zip(labels, acronyms))
label_dict = dict(label_set)
frame_labels_dict['labels'] = label_dict

# set labeling parameters
bulk_label = True
edit_individually = False
acronym = label_dict[input_file]

# define background
max_frame_count = cap.get(7)
print(f'Input video has {max_frame_count} frames')
history = 0
bgSubThreshold = 50
learningRate = 0    # applying learning rate partially solves problem of poor background detection
bgModel = cv2.createBackgroundSubtractorMOG2(history, bgSubThreshold)

# reduce resolution for image processing
split = 5
resize_dims = [1280, 720]

def remove_background(frame):
    fgmask = bgModel.apply(frame, learningRate=learningRate)
    kernel = np.ones((3, 3), np.uint8)
    fgmask = cv2.erode(fgmask, kernel, iterations=1)
    res = cv2.bitwise_and(frame, frame, mask=fgmask)
    return res

# For each frame, open frame, request user input for label, save frame number (key) and label (value) in dictionary 
frame_count = 0
while frame_count <= max_frame_count:
    # frame_labels_dict[frame_count] = {}
    cap.set(1,frame_count)
    ret, frame = cap.read()

    # remove background
    try:
        frame_nobg = remove_background(frame)
    except:
        pass
    # reduce image resolution
    frame_nobg = frame_nobg[0::split, 0::split]

    if testing == True:
        # show image with background removed
        cv2.namedWindow('original', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('original', resize_dims[0], resize_dims[1])
        cv2.imshow('original', frame_nobg)
        cv2.waitKey(1)

    # turn non-black pixels white
    frame_final = np.zeros(frame_nobg.shape, dtype=np.uint8)
    frame_final[frame_nobg>0] = 255

    # convert the image into binary image to reduce file size
    frame_final = cv2.cvtColor(frame_final, cv2.COLOR_BGR2GRAY)
    # frame_final = cv2.fastNlMeansDenoising(frame_final, frame_final, 3, 7, 21)
    # frame_final = cv2.GaussianBlur(frame_final, (7,7), cv2.BORDER_DEFAULT)

    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('frame', resize_dims[0], resize_dims[1])
    cv2.imshow('frame', frame_final)
    cv2.waitKey(1)

    # begin image labeling
    # frame_labels_dict[frame_count]['image'] = frame_final.tolist()

    # Bulk label frames
    if bulk_label:
        []
        # frame_labels_dict[frame_count]['label'] = acronym
    
    # Individually label frames
    else:
        cv2.imshow('frame', frame_final)
        cv2.waitKey(1)
        acronym = input(f'Input acronym of label for each image {label_set}')
        while acronym not in acronyms and acronym.lower() not in acronyms:
            print(f'Invalid entry. Try again')
            acronym = input(f'Input acronym of label for each image {label_set}')
        label = labels[acronym.index(acronym)]
        # frame_labels_dict[frame_count]['label'] = label
        print(f'Frame {frame_count} labeled: {label}')
        cv2.destroyAllWindows()

    if testing == False:
        # save and show final image
        output_file = path + '//' + acronym + f'_{frame_count}.jpg'
        cv2.imwrite(output_file, frame_final)
    frame_count += 1
    print(frame_count)

# Close windows and stream
cap.release()
cv2.destroyAllWindows()

# if testing == False:
#     # Export label and image for each frame to JSON
#     output_filename = time + '_' + input_file +'_labeled_data' + '.json'
#     with open(output_filename, 'w') as outfile:
#         json.dump(frame_labels_dict, outfile)