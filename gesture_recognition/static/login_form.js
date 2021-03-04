const t = document.getElementById('gestClassify');
const apiServer2 = t.getAttribute("data-apiServer") || window.location.origin; //the full TensorFlow Object Detection API server url
var token
login_button = document.getElementById("login_button")

var process_login = function () {
    username = document.getElementById("username").value
    password = document.getElementById("password").value
    var xhr = new XMLHttpRequest();
    xhr.open('POST', apiServer2 + '/api/tokens', true);      // POSTs image and threshold to localhost:5000/image
    xhr.setRequestHeader("Authorization", "Basic " + btoa(username + ':' + password));
    xhr.onload = function() {              // executes this anonymous function when request completes successfully
        if (this.status === 200) {
            token = JSON.parse(this.response)['token']
            var login_form = document.getElementById('log_form');
            login_form.style.visibility = "hidden";
            u.style.visibility = "visible"
            imageCtx.drawImage(v, 0, 0, v.videoWidth, v.videoHeight, 0, 0, uploadWidth, uploadWidth * (v.videoHeight / v.videoWidth));
            imageCanvas.toBlob(postFile, 'image/jpeg'); 
        }
        else {
            console.error(xhr);
        }
    };
    xhr.send(null);
}

login_button.onclick = process_login
$("#password").keypress(function(event) {
    if (event.keyCode === 13) { 
        process_login()
    } 
})