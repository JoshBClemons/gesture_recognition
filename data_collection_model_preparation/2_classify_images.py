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

# Open video 
input_file = 'thumbs_up'
input_type = '.mp4'
path = os.path.join(os.getcwd(), 'data_recordings', input_file)
cap = cv2.VideoCapture(path+input_type)
if cap.read()[0] == False:
    raise Exception('Cannot locate video file')
print(f'Processing {input_file} data')

# unless testing, save each frame from video 
if testing == False:
    time = datetime.datetime.now().strftime("%Y_%m_%d_T%H_%M_%S")
    output_dir = time + '_' + input_file
    path = os.path.join(os.getcwd(), output_dir) 
    try: 
        os.mkdir(path) 
    except:
        print('[INFO] Directory already exists.')

# gesture labels and acronyms
labels = ['open_palm', 'closed_palm', 'L', 'fist', 'thumbs_up']
acronyms = ['op', 'cp', 'l_', 'fi', 'tu']
label_set = list(zip(labels, acronyms))
label_dict = dict(label_set)
acronym = label_dict[input_file]

# set background image
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
    """Subtract background from image."""

    fgmask = bgModel.apply(frame, learningRate=learningRate)
    kernel = np.ones((3, 3), np.uint8)
    fgmask = cv2.erode(fgmask, kernel, iterations=1)
    res = cv2.bitwise_and(frame, frame, mask=fgmask)
    return res

# For each frame, open frame, request user input for label, save frame number (key) and label (value) in dictionary 
frame_count = 0
while frame_count <= max_frame_count:
    cap.set(1,frame_count)
    ret, frame = cap.read()

    # remove background
    frame_nobg = remove_background(frame)

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

    # show final frame
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('frame', resize_dims[0], resize_dims[1])
    cv2.imshow('frame', frame_final)
    cv2.waitKey(1)

    if testing == False:
        # save and show final image
        output_file = path + '//' + acronym + f'_{frame_count}.jpg'
        cv2.imwrite(output_file, frame_final)
    frame_count += 1
    print(frame_count)

# Close windows and stream
cap.release()
cv2.destroyAllWindows()