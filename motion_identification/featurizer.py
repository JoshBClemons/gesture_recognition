from os.path import join, dirname, realpath
import json
import numpy as np
import cv2
import time
import pdb
import tensorflow as tf
import math
import os

# define background parameters
history = 0
bgSubThreshold = 50
learningRate = 0    # applying learning rate partially solves problem of poor background detection
bgModel = 0

# reduce resolution for image processing
split = 5
resize_dims = [1280, 720]

def remove_background(frame):    
    global learningRate, bgModel
    fgmask = bgModel.apply(frame, learningRate=learningRate)
    kernel = np.ones((3, 3), np.uint8)
    fgmask = cv2.erode(fgmask, kernel, iterations=1)
    res = cv2.bitwise_and(frame, frame, mask=fgmask)
    return res

def process(frame, set_background=False, reset=False):
    global bgModel 
    if reset == True:
        frame_processed = frame[0::split, 0::split]
        bgModel = 0
    elif set_background == True:
        bgModel = cv2.createBackgroundSubtractorMOG2(history, bgSubThreshold) # may have to add cv2.cvtColor(np.array(image_object), cv2.COLOR_RGB2BGR) if cv2 relies on existing cv2 instance
        frame_processed = frame[0::split, 0::split]
    elif set_background == False and bgModel != 0:
        try:
            frame_nobg = remove_background(frame)
        except:
            raise Exception('Cannot locate video file')
        # reduce image resolution
        frame_nobg = frame_nobg[0::split, 0::split]
        # turn non-black pixels white
        frame_processed = np.zeros(frame_nobg.shape, dtype=np.uint8)
        frame_processed[frame_nobg>0] = 255  
    elif set_background == False and bgModel == 0:
        frame_processed = frame[0::split, 0::split]
    # convert the image into binary image to reduce file size
    frame_processed = cv2.cvtColor(frame_processed, cv2.COLOR_BGR2GRAY)
    return frame_processed

def rotate(frame, df_row, df_feats):
    instance = df_row[df_feats[0]]
    user_id = int(df_row[df_feats[1]])
    root_dir = df_row[df_feats[2]]
    rotated_dir = os.path.join(root_dir, 'rotated')
    rotated_dir = os.path.join(rotated_dir, str(user_id))
    file_type = '.jpg'

    # flip image
    frame_flipped = tf.image.rot90(frame)
    frame_flipped = tf.image.rot90(frame_flipped)
    frame_flipped = np.array(frame_flipped)
    frame_flipped = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2GRAY)
    flipped_path = os.path.join(rotated_dir, instance + '_flipped' + file_type)

    # mirror image 
    from keras.preprocessing.image import ImageDataGenerator
    import time

    datagen = ImageDataGenerator(horizontal_flip=True)
    frame_ext = frame.reshape((1,) + frame.shape) 
    for frame_mirrored in datagen.flow(frame_ext, batch_size=1):
        frame_mirrored = frame_mirrored.reshape((144,256,3))
   
        # flip mirrored image
        frame_mirrored_flipped = tf.image.rot90(frame_mirrored)
        frame_mirrored_flipped = tf.image.rot90(frame_mirrored_flipped)
        frame_mirrored_flipped = np.array(frame_mirrored_flipped)
        frame_mirrored_flipped = cv2.cvtColor(frame_mirrored_flipped, cv2.COLOR_BGR2GRAY)
        mirrored_flipped_path = os.path.join(rotated_dir, instance + '_mirrored_flipped' + file_type)

        # mirrored image
        frame_mirrored = cv2.cvtColor(frame_mirrored, cv2.COLOR_BGR2GRAY)
        mirrored_path = os.path.join(rotated_dir, instance + '_mirrored' + file_type)
        break
    
    # package results in dictionary
    rotate_dict = {}
    rotate_dict['flipped'] = {}
    rotate_dict['flipped']['path'] = flipped_path
    rotate_dict['flipped']['frame'] = frame_flipped   
    rotate_dict['mirrored'] = {}
    rotate_dict['mirrored']['path'] = mirrored_path
    rotate_dict['mirrored']['frame'] = frame_mirrored
    rotate_dict['mirrored_flipped'] = {}
    rotate_dict['mirrored_flipped']['path'] = mirrored_flipped_path
    rotate_dict['mirrored_flipped']['frame'] = frame_mirrored_flipped
    return rotate_dict