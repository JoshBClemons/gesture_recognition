"""Hand Gesture Prediction Application by Josh Clemons

This script records a client's hand gesture from streamed video and forwards the video frames to a server that predicts the hand gesture and returns the prediction to the client.

This script must be executed concurrently with server.py, which runs on a client's computer and sends webcam streaming video as frame arrays

Please refer to requirements.txt for a listing of all required packages.

To execute this script, input the following:
python client.py --server-ip SERVER_IP

Currently, this program executes and receives streaming frames from a webcam connected to my Windows 10 machine. Eventually, this application will be scaled such that individuals will be able to navigate to a publicly hosted website, stream their web camera footage and perform hand gestures, and receive a prediction of their hand gesture.

NOTE: This script is currently incomplete.
"""


from imagezmq.imagezmq import ImageSender 
import socket	
import time
from contextlib import contextmanager
import argparse
import cv2
from threading import Thread
import functools
import json
import datetime


class Error(Exception):
    """Base class for other exceptions"""
    pass

class StreamClosedError(Error):
    """Raised when camera stream closed"""
    pass

cap = cv2.VideoCapture(1)
cap.set(3, 1280)
cap.set(4, 720)

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'MJPG')

video_filename = datetime.datetime.now().strftime("%Y_%m_%d_T%H_%M_%S") + '_data' + '.avi'
out = cv2.VideoWriter(filename=video_filename, fourcc=fourcc, fps=30.0, frameSize=(int(cap.get(3)),int(cap.get(4))))
print(f"Writing video to {video_filename}")

try:
    if cap.isOpened():
        print("Camera stream open")
    else:
        raise StreamClosedError
except StreamClosedError:
    print("Error: Camera stream closed")

time.sleep(2.0)

# Collect frames
start_time = time.time()
term_time = 5
output_frames = []
while True:
    # read the frame from the camera and send it to the server
    ret, frame = cap.read()
    output_frames.append(frame)

    # Save video
    out.write(frame)

    if ret == False:
        raise Exception('No frame returned. Check connection to camera')

    # Terminate stream
    elapsed_time = time.time() - start_time
    if elapsed_time > term_time:
        print("Termination time reached. Ending stream.")
        break
     

# Export frames
# frame_dict = {}
# frame_dict['frames'] = {}
# frame_dict['frames'] = output_frames.tolist()

# with open('test.txt', 'w') as outfile:
#     json.dump(frame_dict, outfile)

out.release()
cap.release()