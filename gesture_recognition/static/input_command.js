var key = document.getElementById("input_command");
var send_key = ''
var prev_key = ''
input_dict = {
    "b": ["background", "saving background"],
    "r": ["reset", "resetting background"],
    "p": ["pause", "pausing", "resuming"],
}
var prev_letter = document.getElementById(input_dict['b'][0])
key.onkeyup = function(){
    input_key = key.value
    if ((Object.keys(input_dict).includes(input_key) || Object.keys(input_dict).includes(input_key.toLowerCase())) && (send_key != input_key) && (send_key != 'p') && (this.value != 'p')) {
        send_key = prev_key = input_key.toLowerCase(); 
        prev_letter.style.color = ''
        letter = document.getElementById(input_dict[input_key][0])
        letter.style.color = "red"
        key.value = input_dict[input_key][1]
        setTimeout(() => {
            key.value = ''
            prev_letter = letter 
        }, 2000)      
        if (send_key == 'r') {
            send_gesture = ''
            prev_gest.style.color = '' 
        }              
    }
    else if (input_key == "p" || input_key.toLowerCase() == "p") {
        if (send_key == "p") {
            send_key = prev_key = ''
            key.value = input_dict[input_key][2]
            setTimeout(() => {
                key.value = ''
                prev_letter.style.color = ''
            }, 1000)  
            console.log(input_dict[input_key][2])
        }
        else {
            send_key = prev_key = 'p'
            prev_letter.style.color = ''
            letter = document.getElementById(input_dict[input_key][0])
            letter.style.color = "red"
            key.value = input_dict[input_key][1]
            setTimeout(() => {
                key.value = ''
                prev_letter = letter 
            }, 2000)   
            console.log(input_dict[input_key][1])
        }
    }
    else {
        key.value = ''
    }
};