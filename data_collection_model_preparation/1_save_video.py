"""
Steps to save gesture video.
0) Begin module and wait for camera to startup.
1) face camera toward plain background and step out of frame
2) allow module to record several seconds of the background
3) perform hand gesture in front of the camera. Only your hand and arm should be in the camera's field of view
4) if performing multiple hand gestures, allow time between segments for application to capture background. This is necessary since the video will be divided into segments corresponding to each gesture, and it's important that each video segment includes footage of the unobstructed background
4) press any key to stop. module will save recorded video in folder
"""

import time
import cv2
from threading import Thread
import datetime

thread_running = True

class Error(Exception):
    """Base class for other exceptions"""

    pass

class StreamClosedError(Error):
    """Raised when camera stream closed"""

    pass

# webstream parameters
cap = cv2.VideoCapture(1) # change integer to open correct web camera 
cap.set(3, 1280)
cap.set(4, 720)

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
video_filename = datetime.datetime.now().strftime("%Y_%m_%d_T%H_%M_%S") + '_data' + '.avi'
out = cv2.VideoWriter(filename=video_filename, fourcc=fourcc, fps=30.0, frameSize=(int(cap.get(3)),int(cap.get(4))))
print(f"Writing video to {video_filename}")

# verify camera stream is open. Raise exception if not. 
try:
    if cap.isOpened():
        print("Camera stream open")
    else:
        raise StreamClosedError
except StreamClosedError:
    print("Unable to open camera stream")

time.sleep(5)

def record_and_save_frame():
    """Continuously record frames and save them locally."""

    global thread_running
    while True:
        # read frame
        ret, frame = cap.read()

        # Save frame
        out.write(frame)

        # show frame
        cv2.imshow('frame', frame)
        cv2.waitKey(1)

        if ret == False and thread_running == True:
            raise Exception('No frame returned. Check connection to camera')     

def wait_for_user_stop():
    """Wait for user input to stop video streaming."""
    user_input = input('Press any key to stop recording: ')
    print('Recording stopped')

if __name__ == '__main__':
    t1 = Thread(target=record_and_save_frame)
    t2 = Thread(target=wait_for_user_stop)

    t1.start()
    t2.start()

    t2.join()  # interpreter will wait until your process get completed or terminated

    # Terminate stream
    thread_running = False
    out.release()
    cap.release()
    print("Stream terminated")