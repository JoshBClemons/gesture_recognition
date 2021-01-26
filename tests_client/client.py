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


# import signal
# @contextmanager
# def timeout(time):
#     # register a function to raise a TimeoutError on the signal
#     signal.signal(signal.SIGALRM, raise_timeout)
#     # schedule the signal to be sent after 'time'
#     signal.alarm(time)

#     try:
#         yield
#     finally:
#         # unregister the signal so it wont be triggered if the timtout is not reached
#         signal.signal(signal.SIGALRM, signal.SIG_IGN)
    
# def raise_timeout(signum, frame):
#     raise TimeoutError


max_runtime = 5
def timeout(timeout):
    def deco(func):
        @functools.wraps(func) # maintains docstring and name of originally called function. Otherwise name = 'wrapper'
        def wrapper(*args, **kwargs):
            if func.__name__ == 'send_image':
                res = [Exception(f'Image not received. Timeout of {timeout} seconds exceeded')]
            else:
                res = [Exception(f'Error. Timeout of {timeout} seconds exceeded')]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                print ('error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                cap.release()
                raise ret # may modify to allow reconnection to server
            print(ret)
            return ret
        return wrapper
    return deco

@timeout(timeout=max_runtime)
def send_image():
    try:
        hub_reply = sender.send_image(rpiName, frame)
    except Exception as exc:
        time.sleep(max_runtime+0.1)
    pass


class Error(Exception):
    """Base class for other exceptions"""
    pass

class StreamClosedError(Error):
    """Raised when camera stream closed"""
    pass

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True,
                help="ip address of the server to which the client will connect")
args = vars(ap.parse_args())

# initialize the ImageSender object with the socket address of the server
server_loc = "tcp://{}:5555"
connect_to = server_loc.format(args["server_ip"])
sender = ImageSender(connect_to=connect_to)
print(f"Connecting to server socket: {connect_to}")

# get the host name, initialize the video stream, and allow the
# camera sensor to warmup
rpiName = socket.gethostname()
ip_address = socket.gethostbyname(rpiName)
print(f"Client hostname: {rpiName}")
print(f"Client IP Address: {ip_address}")

cap = cv2.VideoCapture(1)
try:
    if cap.isOpened():
        print("Camera stream open")
    else:
        raise StreamClosedError
except StreamClosedError:
    print("Error: Camera stream closed")

time.sleep(2.0)

timestamp_of_last_socket_refresh = time.time()
term_time = 5
while True:
    # read the frame from the camera and send it to the server
    ret, frame = cap.read()
    if ret == False:
        raise Exception('No frame returned. Check connection to camera')
    try:
        send_image()
    except TimeoutError:
        print("Sending timeout.. reconnect to server")
        sender = ImageSender(connect_to=server_loc.format(args["server_ip"]))

    # Terminate stream
    elapsed_time = time.time() - timestamp_of_last_socket_refresh
    if elapsed_time > term_time:
        print("Termination time reached. Ending stream.")
        break

cap.release()