"""Hand Gesture Prediction Application by Josh Clemons

This script predicts a client's hand gesture from streamed video and returns the prediction to the client.

This script must be executed concurrently with client.py, which runs on a client's computer and sends webcam streaming video as frame arrays

Please refer to requirements.txt for a listing of all required packages.

To execute this script, input the following:
python server.py --prototxt MobileNetSSD_deploy.prototxt --model MobileNetSSD_deploy.caffemodel --montageW 2 --montageH 2

Currently, this program executes in a virtual environment on a Ubuntu virtual machine and receives streaming frames generated from a webcam connected to my Windows 10 machine. Eventually, this application will be scaled such that individuals will be able to navigate to a publicly hosted website, stream their web camera footage and perform hand gestures, and receive a prediction of their hand gesture.

NOTE: This script is currently incomplete.
"""


# import the necessary packages
from imutils import build_montages
from datetime import datetime
import numpy as np
from imagezmq.imagezmq import ImageHub
import argparse
import imutils
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
                help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
                help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
                help="minimum probability to filter weak detections")
ap.add_argument("-mW", "--montageW", required=True, type=int,
                help="montage frame width")
ap.add_argument("-mH", "--montageH", required=True, type=int,
                help="montage frame height")
ap.add_argument("-dm", "--detection-method", type=str, default='hog',
                help="face detection model to use: either 'hog' or 'cnn' ")
ap.add_argument("-ef", "--encoding-file", type=str, default='',
                help="face detection model to use: either 'hog' or 'cnn' ")

args = vars(ap.parse_args())


encoding_file = args['encoding_file']
if not encoding_file:
    encoding_file = None


detection_method = args['detection_method']

# initialize the ImageHub object
imageHub = ImageHub()

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["gesture1", "gesture2", "gesture3"] # Incomplete

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialize the consider set (class labels we care about and want
# to count), the object count dictionary, and the frame  dictionary
CONSIDER = set(["gesture1", "gesture2", "gesture3"])
objCount = {obj: 0 for obj in CONSIDER}
frameDict = {}

# initialize the dictionary which will contain information regarding
# when a stream was last active, then store the last time the check
# was made was now
lastActive = {}
lastActiveCheck = datetime.now()

# the duration seconds to wait before making a check to see if a 
# client device is active
ACTIVE_CHECK_SECONDS = 10

# assign montage width and height so we can view all incoming frames
# in a single "dashboard"
mW = args["montageW"]
mH = args["montageH"]
print("[INFO] detecting: {}...".format(", ".join(obj for obj in
                                                 CONSIDER)))

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter(filename='output.avi',fourcc=fourcc, fps=30.0, frameSize=(640,480))

# start looping over all the frames

try:
    while True:
        # receive RPi name and frame from the RPi and acknowledge
        # the receipt
        (rpiName, frame) = imageHub.recv_image()

        imageHub.send_reply(b'OK')

        print("[INFO] receiving data from {}...".format(rpiName))

        # record the last active time for the device from which we just
        # received a frame
        lastActive[rpiName] = datetime.now()
        
#         # resize the frame to have a maximum width of 400 pixels, then
#         # grab the frame dimensions and construct a blob
#         # print(f"Original: {frame.shape[:2]}")
#         frame = imutils.resize(frame, width=400)
#         (h, w) = frame.shape[:2]
        
#         # print(f"Resized: {frame.shape[:2]}")
#         blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),0.007843, (300, 300), 127.5)
        
#         # pass the blob through the network and obtain the detections and
#         # predictions
#         net.setInput(blob)
#         detections = net.forward()
        
#         # reset the object count for each object in the CONSIDER set
#         objCount = {obj: 0 for obj in CONSIDER}
        
#         # loop over the detections
#         for i in np.arange(0, detections.shape[2]):
#             # extract the confidence (i.e., probability) associated with
#             # the prediction
#             confidence = detections[0, 0, i, 2]
            
#             # filter out weak detections by ensuring the confidence is
#             # greater than the minimum confidence
#             if confidence > args["confidence"]:
                
#                 # extract the index of the class label from the
#                 # detections
#                 idx = int(detections[0, 0, i, 1])
                
#                 print('checkpoint 9') # UNCLEAR IF ALGORITHM WOULD FAIL HERE OR BELOW SINCE CONFIDENCE THRESHOLD NEVER EXCEEDED
               
#             # check to see if the predicted class is in the set of
#                 # classes that need to be considered
#                 if CLASSES[idx] in CONSIDER:
#                     # increment the count of the particular object
#                     # detected in the frame
#                     objCount[CLASSES[idx]] += 1

#                     # compute the (x, y)-coordinates of the bounding box
#                     # for the object
#                     box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
#                     (startX, startY, endX, endY) = box.astype("int")

#                     # draw the bounding box around the detected object on
#                     # the frame
#                     cv2.rectangle(frame, (startX, startY), (endX, endY),(255, 0, 0), 2)

#         # draw the sending device name on the frame
#         cv2.putText(frame, rpiName, (10, 25),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

#         # draw the object count on the frame
#         label = ", ".join("{}: {}".format(obj, count) for (obj, count) in
#                           objCount.items())
#         cv2.putText(frame, label, (10, h - 20),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

#         # update the new frame in the frame dictionary
#         frameDict[rpiName] = frame

#         # build a montage using images in the frame dictionary
#         montages = build_montages(frameDict.values(), (w, h), (mW, mH))

#         # display the montage(s) on the screen
#         for (i, montage) in enumerate(montages):
#             cv2.imshow("Monitor Dashboard ({})".format(i),montage) # ALGORITHM FAILED HERE SINCE NO DISPLAYS AVAILABLE
#         print('checkpoint 14')
#         # detect any kepresses
#         key = cv2.waitKey(1) & 0xFF
#         print('checkpoint 14')
#         # if current time *minus* last time when the active device check
#         # was made is greater than the threshold set then do a check
#         if (datetime.now() - lastActiveCheck).seconds > ACTIVE_CHECK_SECONDS:
#             # loop over all previously active devices
#             for (rpiName, ts) in list(lastActive.items()):
#                 # remove the RPi from the last active and frame
#                 # dictionaries if the device hasn't been active recently
#                 if (datetime.now() - ts).seconds > ACTIVE_CHECK_SECONDS:
#                     print("[INFO] lost connection to {}".format(rpiName))
#                     lastActive.pop(rpiName)
#                     frameDict.pop(rpiName)

#             # set the last active check time as current time
#             lastActiveCheck = datetime.now()
#         print('checkpoint 15')
        
        # write frame to local video
        out.write(frame)
        print('checkpoint 15')
        
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
            
except KeyboardInterrupt:
    imageHub.send_reply(b'Stream upload interrupted')
    pass

# cleanup
out.release()
cv2.destroyAllWindows()