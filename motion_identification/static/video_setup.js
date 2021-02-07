//create webcam video element
s = document.getElementById("myVideo")
s.style.position = 'absolute';
var video_height = window.innerHeight*3/8
var video_width = video_height*16/9
s.style.height = video_height + "px";
s.style.width = video_width + "px";

s.style.left = 0.5*(window.innerWidth-video_width) + "px";
s.style.top = window.innerHeight/8 + "px"
s.style.border = "thin solid";

//Get camera video
const constraints = {
    audio: false,
    video: {
        width: {min: 640, ideal: 1280, max: 1920},
        height: {min: 480, ideal: 720, max: 1080}
    }
};

navigator.mediaDevices.getUserMedia(constraints)
    //then and catch are callback functions that execute after (un)successful execution of promise statement above
    .then(stream => { 
        document.getElementById("myVideo").srcObject = stream;
        console.log("Got local user video");

    })
    .catch(err => {
        console.log('navigator.getUserMedia error: ', err)
    });
