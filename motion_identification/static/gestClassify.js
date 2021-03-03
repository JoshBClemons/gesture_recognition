const s = document.getElementById('gestClassify');
const sourceVideo = s.getAttribute("data-source");  //the source video to use
const uploadWidth = s.getAttribute("data-uploadWidth") || 640; //the width of the upload file
const mirror = s.getAttribute("data-mirror") || false; //mirror the boundary boxes
const apiServer = s.getAttribute("data-apiServer") || window.location.origin; //the full TensorFlow Object Detection API server url

//Video element selector
v = document.getElementById(sourceVideo);

//for starting events
let isPlaying = false,
    gotMetadata = false;

//canvas to grab an image for upload
let imageCanvas = document.createElement('canvas');
let imageCtx = imageCanvas.getContext("2d");

var prev_size = 0;

//return classification result and processed frame from XML request
function postFile(file) {
    if (file.size != prev_size && send_key != 'p' && typeof(token) != 'undefined') {
        let formdata = new FormData();
        formdata.append("image", file);
        formdata.append("token", token);
        formdata.append("command", send_key);
        formdata.append("gesture", send_gesture);
        var xhr = new XMLHttpRequest();
        xhr.open('POST', apiServer + '/image', true);      // POSTs image and token to localhost:5000/image
        xhr.onload = function() {              // executes this anonymous function when request completes successfully           
            if (this.status === 200) {
                output = JSON.parse(this.response);
                imgsrc = 'data:image/jpeg;base64,' + output.train_image;
                label = output.label;
                if (output.command != '') {
                    send_key = ''
                }
                var img = new Image()
                img.onload = function() {
                    // draw training image
                    drawCtx.drawImage(img, 0, 0, drawCanvas.width, drawCanvas.height);

                    // post classification label
                    document.getElementById('label').innerHTML = label;
                    setTimeout(() => {
                        imageCtx.drawImage(v, 0, 0, v.videoWidth, v.videoHeight, 0, 0, uploadWidth, uploadWidth * (v.videoHeight / v.videoWidth));
                        imageCanvas.toBlob(postFile, 'image/jpeg'); 
                    }, 250)
                };  
                img.src = imgsrc;  
            }
            else {
                console.error(xhr);
            }
        };
        xhr.send(formdata);
        prev_size = file.size;
    } else if (send_key == 'p') {
        setTimeout(() => {
            imageCtx.drawImage(v, 0, 0, v.videoWidth, v.videoHeight, 0, 0, uploadWidth, uploadWidth * (v.videoHeight / v.videoWidth));
            imageCanvas.toBlob(postFile, 'image/jpeg'); 
        }, 100)
    }
}

//Start object detection
function startObjectDetection() {
    console.log("starting object detection");

    //Set canvas sizes based on input video
    drawCanvas.width = v.videoWidth;
    drawCanvas.height = v.videoHeight;
    imageCanvas.width = uploadWidth;
    imageCanvas.height = uploadWidth * (v.videoHeight / v.videoWidth);

    //Save and send the first image
    imageCtx.drawImage(v, 0, 0, v.videoWidth, v.videoHeight, 0, 0, uploadWidth, uploadWidth * (v.videoHeight / v.videoWidth));
    imageCanvas.toBlob(postFile, 'image/jpeg'); 
};

//check if metadata is ready - we need the video size
v.onloadedmetadata = () => {
    console.log("video metadata ready");
    gotMetadata = true;
};

//see if the video has started playing
//onplaying event executes defined function automatically when video begins
v.onplaying = () => {
    console.log("video playing");
    isPlaying = true;
    if (gotMetadata) {
        startObjectDetection();
        gotMetadata = false; // ensure startObjectDetection() runs once. Otherwise, if no functions are available for whatever reason, this function will be called again. Happens up to 2x times.
    }
}