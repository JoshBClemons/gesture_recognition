const apiServer = window.location.origin;

var title = document.getElementById('title');
title.style.textAlign = 'center'

m0cr = document.getElementById("m0cr");
m0cm = document.getElementById("m0cm");
m1cr = document.getElementById("m1cr");
m1cm = document.getElementById("m1cm");
m2cr = document.getElementById("m2cr");
m2cm = document.getElementById("m2cm");
todays_user_act = document.getElementById("todays_user_act");
pred_acc_date = document.getElementById("pred_acc_date");
user_usage = document.getElementById("user_usage");
gest_counts = document.getElementById("gest_counts");

//define overall figure parameters
margin = 10;
title_offset = window.innerHeight*.08
total_height = window.innerHeight-title_offset;

//define canvases
var canvas_model_stats = document.getElementById("model_stats")
var ctx_model_stats = canvas_model_stats.getContext("2d");
canvas_model_stats.style.top = title_offset + "px"
canvas_model_stats.style.left = 0 + "px"
var canvas_todays_user_act_stats = document.getElementById("todays_user_act_stats")
var ctx_todays_user_act_stats = canvas_todays_user_act_stats.getContext("2d");
canvas_todays_user_act_stats.style.top = title_offset + "px";
var canvas_continuous_stats = document.getElementById("continuous_stats")
var ctx_continuous_stats = canvas_continuous_stats.getContext("2d");

var cr_height, cr_width, cm_width, cm_height, model_stats_width; 
var cr1_y_offset, cr2_y_offset, cm_x_offset, cm0_y_offset, cm1_y_offset, cm2_y_offset;
var model_scale_factor;
var imgsrc_base = 'data:image/jpeg;base64,';

var socket = io.connect(location.protocol + '//' + location.hostname + ':' + location.port);
(function request_stats() {
    socket.emit('request_stats');
    setTimeout(() => {
        request_stats(); 
    }, 5000)  
})()
socket.on('stats', function(output) {
    title.innerHTML='Hand Gesture Model and User Statistics<br>' + output.message
    title.style.left = (window.innerWidth-title.getBoundingClientRect().width)/2 + "px";
    
    var cr_figs = output['cr_figs']
    var cm_figs = output['cm_figs']
    var other_figs = output['other_figs']
    
    // position classification reports and confusion matrices on left side of screen
    m0cr.src = imgsrc_base + output[cr_figs[0]];
    m0cr.onload = function () {
        cr_height = m0cr.getBoundingClientRect().height;
        model_scale_factor = (total_height-2*margin) / (cr_height*3);
        cr_height = cr_height*model_scale_factor; //classification report height drives since larger than confusion matrix
        cr_width = cr_height*m0cr.getBoundingClientRect().width/cr_height
        cm_x_offset = cr_width + margin; 
        model_stats_width = cm_x_offset
        //after partially defining canvas width, load confusion matrix figure
        m0cm.src = imgsrc_base + output[cm_figs[0]]
    }
    m0cm.onload = function () {
        cm_height = m0cm.getBoundingClientRect().height*model_scale_factor;
        cm_width = m0cm.getBoundingClientRect().width*model_scale_factor;
        cm0_y_offset = cr_height - cm_height
        //with both classification report and confusion matrix loaded, fully define canvas width
        model_stats_width += cm_width; 
        canvas_model_stats.height = total_height;
        canvas_model_stats.width = model_stats_width;
        //draw report and matrix for model 0
        ctx_model_stats.clearRect(0, 0, canvas_model_stats.width, canvas_model_stats.height)
        ctx_model_stats.drawImage(m0cr, 0, 0, cr_width, cr_height);
        ctx_model_stats.drawImage(m0cm, cm_x_offset, cm0_y_offset, cm_width, cm_height); // need to adjust height
        //define vertical offsets for subsequent figures  
        cr1_y_offset = cr_height + margin
        cr2_y_offset = cr_height + margin + cr1_y_offset
        cm1_y_offset = cm0_y_offset + cr1_y_offset
        cm2_y_offset = cm0_y_offset + cr2_y_offset
        right_side_width = window.innerWidth - model_stats_width - margin;
        //load remaining classification reports and confusion matrices
        m1cr.src = imgsrc_base + output[cr_figs[1]];
        m1cm.src = imgsrc_base + output[cm_figs[1]]
        m2cr.src = imgsrc_base + output[cr_figs[2]];
        m2cm.src = imgsrc_base + output[cm_figs[2]]
        //load daily user activity figure
        todays_user_act.src = imgsrc_base + output[other_figs[0]]
        canvas_todays_user_act_stats.style.left = model_stats_width + "px";
    }
    m1cr.onload = function () {
        ctx_model_stats.drawImage(m1cr, 0, cr1_y_offset, cr_width, cr_height);
    }
    m1cm.onload = function () {
        ctx_model_stats.drawImage(m1cm, cm_x_offset, cm1_y_offset, cm_width, cm_height);
    }
    m2cr.onload = function () {
        ctx_model_stats.drawImage(m2cr, 0, cr2_y_offset, cr_width, cr_height);
    }
    m2cm.onload = function () {
        ctx_model_stats.drawImage(m2cm, cm_x_offset, cm2_y_offset, cm_width, cm_height);
    }
    todays_user_act.onload = function () {
        tua_width = todays_user_act.getBoundingClientRect().width;
        tua_scale_factor = right_side_width / tua_width;
        tua_width = tua_width*tua_scale_factor
        tua_height = todays_user_act.getBoundingClientRect().height*tua_scale_factor;
        canvas_todays_user_act_stats.width = tua_width;
        canvas_todays_user_act_stats.height = tua_height;
        ctx_todays_user_act_stats.clearRect(0, 0, canvas_todays_user_act_stats.width, canvas_todays_user_act_stats.height)
        ctx_todays_user_act_stats.drawImage(todays_user_act, 0, 0, tua_width, tua_height);
        //start loading remaining figures
        right_side_fig_height = window.innerHeight - title_offset - tua_height - margin
        right_side_fig_width = (right_side_width-2*margin)/3;
        canvas_continuous_stats.style.left = model_stats_width + "px";
        canvas_continuous_stats.style.top = tua_height + +title_offset + "px";
        pred_acc_date.src = imgsrc_base + output[other_figs[1]]
    }
    var right_side_fig_width, pad_width, uu_width
    var right_side_fig_height
    var pad_offset, uu_x_offset
    pred_acc_date.onload = function () {
        canvas_continuous_stats.width = right_side_width;
        canvas_continuous_stats.height = right_side_fig_height;
        pad_width = pred_acc_date.getBoundingClientRect().width;
        pad_height = pred_acc_date.getBoundingClientRect().height;
        pad_width_scale_factor = right_side_fig_width/pad_width;
        pad_height_scale_factor = right_side_fig_height/pad_height;
        if (pad_width_scale_factor <= pad_height_scale_factor){
            pad_width = pad_width*pad_width_scale_factor;
            pad_height = pad_height*pad_width_scale_factor;
        }
        else {
            pad_width = pad_width*pad_height_scale_factor;
            pad_height = pad_height*pad_height_scale_factor;
        }
        pad_offset = right_side_fig_height - pad_height ;
        ctx_continuous_stats.clearRect(0, 0, canvas_continuous_stats.width, canvas_continuous_stats.height)
        ctx_continuous_stats.drawImage(pred_acc_date, 0, pad_offset, pad_width, pad_height);
        //continue loading remaining figures
        user_usage.src = imgsrc_base + output[other_figs[2]]
    }
    user_usage.onload = function () {
        uu_width = user_usage.getBoundingClientRect().width;
        uu_height = user_usage.getBoundingClientRect().height;
        uu_width_scale_factor = right_side_fig_width/uu_width;
        uu_height_scale_factor = right_side_fig_height/uu_height;
        if (uu_width_scale_factor <= uu_height_scale_factor){
            uu_width = uu_width*uu_width_scale_factor;
            uu_height = uu_height*uu_width_scale_factor;
        }
        else {
            uu_width = uu_width*uu_height_scale_factor;
            uu_height = uu_height*uu_height_scale_factor;
        }
        uu_y_offset = right_side_fig_height - uu_height;
        uu_x_offset = pad_width + margin;
        ctx_continuous_stats.drawImage(user_usage, uu_x_offset, uu_y_offset, uu_width, uu_height);
        //load remaining figure
        gest_counts.src = imgsrc_base + output[other_figs[3]]
    }
    gest_counts.onload = function () {
        gc_width = gest_counts.getBoundingClientRect().width;
        gc_height = gest_counts.getBoundingClientRect().height;
        gc_width_scale_factor = right_side_fig_width/gc_width;
        gc_height_scale_factor = right_side_fig_height/gc_height;
        if (gc_width_scale_factor <= gc_height_scale_factor){
            gc_width = gc_width*gc_width_scale_factor;
            gc_height = gc_height*gc_width_scale_factor;
        }
        else {
            gc_width = gc_width*gc_height_scale_factor;
            gc_height = gc_height*gc_height_scale_factor;
        }
        gc_y_offset = right_side_fig_height - gc_height;
        gc_x_offset = uu_x_offset + uu_width+ margin;
        ctx_continuous_stats.drawImage(gest_counts, gc_x_offset, gc_y_offset, gc_width, gc_height);
    }
});