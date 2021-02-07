const s = document.getElementById('gestClassify');
const sourceVideo = s.getAttribute("data-source");  //the source video to use
const uploadWidth = s.getAttribute("data-uploadWidth") || 640; //the width of the upload file
const mirror = s.getAttribute("data-mirror") || false; //mirror the boundary boxes
const scoreThreshold = s.getAttribute("data-scoreThreshold") || 0.5;
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

// style="color:blue;font-weight:bold"

//return classification result and processed frame from XML request
function postFile(file) {
    // debugger
    if (file.size != prev_size && prev_key != 'p') {
        let formdata = new FormData();
        formdata.append("image", file); //use formdata.get("image") to print file contents
        formdata.append("threshold", scoreThreshold);
        var xhr = new XMLHttpRequest();
        xhr.open('POST', apiServer + '/image', true);      // POSTs image and threshold to localhost:5000/image
        xhr.onload = function() {              // executes this anonymous function when request completes successfully
            if (this.status === 200) {
                output = JSON.parse(this.response);
                imgsrc = 'data:image/jpeg;base64,' + output.train_image;
                label = output.label;
                
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
    } else if (prev_key == 'p') {
        setTimeout(() => {
            imageCtx.drawImage(v, 0, 0, v.videoWidth, v.videoHeight, 0, 0, uploadWidth, uploadWidth * (v.videoHeight / v.videoWidth));
            imageCanvas.toBlob(postFile, 'image/jpeg'); 
        }, 100)
    }
}

var key = document.getElementById("key_press");
var prev_key = ''
input_dict = {
    "b": ["background", "background saved"],
    "r": ["reset", "background reset"],
    "p": ["pause", "program paused", "program resumed"],
}
var prev_letter = document.getElementById(input_dict['b'][0])
key.onkeyup = function(){
    input_key = key.value
    if ((Object.keys(input_dict).includes(input_key) || Object.keys(input_dict).includes(input_key.toLowerCase())) && (prev_key != input_key) && (prev_key != 'p') && (this.value != 'p')) {
        let key_formdata = new FormData();
        key_formdata.append("key", input_key.toLowerCase());
        var key_xhr = new XMLHttpRequest();
        key_xhr.open('POST', apiServer + '/key', true);      
        key_xhr.onload = function() {   
            //reset entry field   
            if (this.status === 200) {
                console.log(this.response)
                prev_letter.style.color = ''
                letter = document.getElementById(input_dict[input_key][0])
                letter.style.color = "red"
                key.value = input_dict[input_key][1]
                setTimeout(() => {
                    key.value = ''
                    prev_letter = letter 
                }, 1000)                    
            }
            else {
                console.error(xhr);
            }
        };
        key_xhr.send(key_formdata);
        prev_key = this.value
    }
    else if (input_key == "p" || input_key.toLowerCase() == "p") {
        if (prev_key == "p") {
            prev_key = ''
            key.value = input_dict[input_key][2]
            setTimeout(() => {
                key.value = ''
                prev_letter.style.color = ''
            }, 1000)  
            console.log(input_dict[input_key][2])
        }
        else {
            prev_key = 'p'
            prev_letter.style.color = ''
            letter = document.getElementById(input_dict[input_key][0])
            letter.style.color = "red"
            key.value = input_dict[input_key][1]
            setTimeout(() => {
                key.value = ''
                prev_letter = letter 
            }, 1000)   
            console.log(input_dict[input_key][1])
        }
    }
    else {
        key.value = ''
    }
};

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