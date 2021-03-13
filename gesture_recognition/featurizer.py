from os.path import join
import numpy as np
import cv2
import pdb
import os
import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator

# background parameters
history = 0
bgSubThreshold = 50
learningRate = 0    # applying learning rate partially solves problem of poor background detection

def set_background(frame):
    """Save user background image."""
    bgModel = cv2.createBackgroundSubtractorMOG2(history, bgSubThreshold)
    
    return bgModel

def remove_background(frame, bgModel):    
    """Subtract user background image from new image."""
    global learningRate
    fgmask = bgModel.apply(frame, learningRate=learningRate)
    kernel = np.ones((3, 3), np.uint8)
    fgmask = cv2.erode(fgmask, kernel, iterations=1)
    res = cv2.bitwise_and(frame, frame, mask=fgmask)

    return res

def process(frame, bgModel):
    """Process user image by removing background and converting resultant to binary image."""
    if bgModel != 0:
        frame_nobg = remove_background(frame, bgModel)

        # resize image
        frame_nobg = cv2.resize(frame_nobg, dsize=(256,144), interpolation=cv2.INTER_LINEAR)

        # turn non-black pixels white
        frame_processed = np.zeros(frame_nobg.shape, dtype=np.uint8)
        frame_processed[frame_nobg>0] = 255  
    else:
        frame_processed = cv2.resize(frame, dsize=(256,144), interpolation=cv2.INTER_LINEAR)

    # convert the image into binary image to reduce file size
    frame_processed = cv2.cvtColor(frame_processed, cv2.COLOR_BGR2GRAY)

    # Expand dimensions since the model expects images to have shape: [1, 144, 256, 3]
    frame_prediction = frame_processed.astype(np.float)
    frame_prediction = np.stack((frame_prediction,)*3, axis=-1) # without comma, (X_data) is np.array not tuple
    frame_prediction /= 255
    frame_prediction = np.expand_dims(frame_prediction, axis=0)

    return [frame_processed, frame_prediction]

def rotate(frame, df_row, df_feats):
    """Generate rotated versions of image."""
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