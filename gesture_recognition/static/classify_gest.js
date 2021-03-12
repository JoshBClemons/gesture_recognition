const s = document.getElementById('classify_gest');
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
var socket = io.connect(location.protocol + '//' + location.hostname + ':' + location.port);
function postFile(file) {
    if (file.size != prev_size && send_key != 'p' && typeof(token) != 'undefined') {
        prev_size = file.size;
        socket.emit('post_image', {image: file, token: token, command: send_key, gesture: send_gesture});
    } else if (send_key == 'p') {
        setTimeout(() => {
            imageCtx.drawImage(v, 0, 0, v.videoWidth, v.videoHeight, 0, 0, uploadWidth, uploadWidth * (v.videoHeight / v.videoWidth));
            imageCanvas.toBlob(postFile, 'image/jpeg'); 
        }, 500)
    }
}
socket.on('response_image', function(output) { 
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
        }, 500)
    };  
    img.src = imgsrc;  
});

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