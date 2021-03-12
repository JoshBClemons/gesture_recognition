var token
login_button = document.getElementById("login_button")

//get list of all users and whether they're online 
var users
(function() {
    xhr = new XMLHttpRequest();
    xhr.open('GET', apiServer + '/api/users', true);    
    xhr.onload = function() {   
        users = JSON.parse(this.response)['users']
    };
    xhr.send(null);
})();

//after credentials entered, create new user or verify password of existing user 
var process_login = function () {
    username = document.getElementById("username").value
    password = document.getElementById("password").value
    // check if user exists or is already signed in  
    old = false
    for (i=0; i<users.length; i++) {
        user = users[i]
        if ((user['username'] == username) && (user['online'] == false)) {
            old = true;
            break;
        }
        else if ((user['username'] == username) && (user['online'] == true)) {
            // notify that already signed in
            old = true;
            break;
        }
    }
    xhr = new XMLHttpRequest();
    if (old==false) {
        creds = {}
        creds['username'] = username;
        creds['password'] = password;
        xhr.open('POST', apiServer + '/api/users', true);
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhr.send(JSON.stringify(creds));
    }
    else {
        xhr.open('POST', apiServer + '/api/tokens', true);
        xhr.setRequestHeader("Authorization", "Basic " + btoa(username + ':' + password));
        xhr.send(null);
    }
    xhr.onload = function() {            
        if (this.status == 200) {
            token = JSON.parse(this.response)['token']
            var login_form = document.getElementById('log_form');
            login_form.style.visibility = "hidden";
            u.style.visibility = "visible"
            imageCtx.drawImage(v, 0, 0, v.videoWidth, v.videoHeight, 0, 0, uploadWidth, uploadWidth * (v.videoHeight / v.videoWidth));
            imageCanvas.toBlob(postFile, 'image/jpeg'); 
        }
        else if (this.status == 400){
            console.log("Username already exists.")
        }
        else {
            console.error(xhr);
        }
    };
};

login_button.onclick = process_login
$("#password").keypress(function(event) {
    if (event.keyCode === 13) { 
        process_login()
    } 
});