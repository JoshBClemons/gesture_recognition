var gesture_key = document.getElementById("input_gest");
var send_gesture = ''
gesture_dict = {
    "f": "fist",
    "l": "L",
    "p": "palm",
    "t": "thumb",
}

var prev_gest = document.getElementById(gesture_dict['c']) // init value irrelevant
gesture_key.onkeyup = function(){
    if ((Object.keys(gesture_dict).includes(gesture_key.value) || Object.keys(gesture_dict).includes(gesture_key.value.toLowerCase())) && (prev_key == '' || prev_key == 'r')) {
        gesture_key.value = 'Save background first'
        setTimeout(() => {
            gesture_key.value = ''
        }, 2000)     
    }
    else if (Object.keys(gesture_dict).includes(gesture_key.value) || Object.keys(gesture_dict).includes(gesture_key.value.toLowerCase())) {
        send_gesture = gesture_dict[gesture_key.value.toLowerCase()]; 
        prev_gest.style.color = ''
        gest = document.getElementById(gesture_dict[gesture_key.value])
        gest.style.color = "blue"
        prev_gest = gest 
        gesture_key.value = ''
    }
    else {
        gesture_key.value = ''
    }
};