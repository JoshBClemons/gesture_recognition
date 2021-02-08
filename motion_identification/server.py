#!/usr/bin/env python

import gesture_classification
from PIL import Image
from flask import Flask, request, Response
import cv2
import base64

app = Flask(__name__)
current_key = ''

# for CORS - debug later
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST') # Put any other methods you need here
    return response

@app.route('/')
def index():
    return Response(open('./static/local.html').read(), mimetype="text/html")

@app.route('/image', methods=['POST'])
def image():  
    try:        
        input_bin = request.files['image'].read()
        encoded_input = base64.b64encode(input_bin).decode()
        image_file = request.files['image']  # get the image

        # pass image to gesture recognition model
        image_object = Image.open(image_file)
        global current_key
        (label, frame, updated_key) = gesture_classification.classify(image_object, current_key)
        # pdb.set_trace()
        output_bin = cv2.imencode('.jpg', frame)[1].tobytes()
        encoded_output = base64.b64encode(output_bin).decode()

        # stamp = datetime.datetime.now().strftime("%Y_%m_%d_T%H_%M_%S")
        # package results in dictionary
        output_dict = {}
        output_dict['train_image'] = encoded_output
        output_dict['label'] = label
        # pdb.set_trace()
        current_key = updated_key
        return output_dict

    except Exception as e:
        print('POST /image error: %e' % e)
        return e

@app.route('/key', methods=['POST'])
def key():  
    input_key = request.form['key']  # get the image
    global current_key
    current_key = input_key
    if input_key == 'b':
        return Response(response="background saved", status=200)
    elif input_key == 'r':
        return Response(response="background reset", status=200)
    elif input_key == 'p':
        return Response(response="paused", status=200)

if __name__ == '__main__':
	# without SSL
    app.run(debug=False, host='0.0.0.0')

	# with SSL
    #app.run(debug=True, host='0.0.0.0', ssl_context=('ssl/server.crt', 'ssl/server.key'))
