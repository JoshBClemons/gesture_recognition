//get elements
var title = document.getElementById('title');
tables = document.getElementById("tables");
figures = document.getElementById("figures");
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

//position title
margin = 1;
title_offset = window.innerHeight*.08
title.style.textAlign = 'center';
total_height = window.innerHeight-title_offset;

//position tables
tables.style.height = total_height + "px";
tables_width = 40;
tables.style.width = tables_width + "%";
tables.style.left = 0 + "px";
tables.style.top = title_offset + "px";
table_height = 100/3 - margin;
m0cr.style.left = m1cr.style.left = m2cr.style.left = 0;
m0cr.style.width = m1cr.style.width = m2cr.style.width = 49 - margin + "%";
m0cr.style.margin = m1cr.style.margin = m2cr.style.margin = margin + "%";
m0cm.style.left = m1cm.style.left = m2cm.style.left = 49 + "%";
m0cm.style.margin = m1cm.style.margin = m2cm.style.margin = margin + "%";
m0cm.style.width = m1cm.style.width = m2cm.style.width = 49 - margin + "%";
m0cr.style.height = m1cr.style.height = m2cr.style.height = m0cm.style.height = m1cm.style.height = m2cm.style.height = table_height + "%";
m1cr.style.top = m1cm.style.top = table_height + margin + "%";
m2cr.style.top = m2cm.style.top = 2*(table_height + margin) + "%";

//position figures
figures.style.height = total_height + "px";
figures.style.width = 100 - tables_width + "%";
figures.style.left = tables_width + "%";
figures.style.top = title_offset + "px";

//canvas variables
var canvas_todays_user_act_stats = document.getElementById("todays_user_act_stats")
var ctx_todays_user_act_stats = canvas_todays_user_act_stats.getContext("2d");
var canvas_continuous_stats = document.getElementById("continuous_stats")
var ctx_continuous_stats = canvas_continuous_stats.getContext("2d");
var imgsrc_base = 'data:image/jpeg;base64,';

//socket variables
const apiServer = window.location.origin;
var socket = io.connect(location.protocol + '//' + location.hostname + ':' + location.port);

//request updated stats every 5 seconds
(function request_stats() {
    socket.emit('request_stats');
    setTimeout(() => {
        request_stats(); 
    }, 5000)  
})()

var update_table = function (table, data) {
    if (table.tHead.children[0].childElementCount == 0) {
        // create caption
        table.createCaption();
        table.caption.innerHTML = data.caption;
        // create headers
        headers = data.columns;
        var tr = table.tHead.children[0];
        th = document.createElement('th');
        th.innerHTML = '';
        tr.appendChild(th);
        var i;
        for (i = 0; i < headers.length; i++) {
            th = document.createElement('th');
            th.innerHTML = headers[i];
            tr.appendChild(th);
        }
    }
    rows = data.data;
    index = data.index;
    var i
    for (i = 0; i < rows.length; i++) {
        // debugger
        if (table.children[1].childElementCount > rows.length+1){
            table.deleteRow(i+1);
        }
        row = rows[i]
        row.unshift(index[i])
        var table_row = table.insertRow(i+1);
        for (j = 0; j < row.length; j++) {
            cell = table_row.insertCell(j);
            cell.innerHTML = row[j];  
        }  
    }
};

socket.on('stats', function(figure_data) {
    title.innerHTML='Hand Gesture Model and User Statistics<br>' + figure_data.message
    title.style.left = (window.innerWidth-title.getBoundingClientRect().width)/2 + "px";
    
    var cr_figs = figure_data['cr_figs'];
    var cm_figs = figure_data['cm_figs'];
    var other_figs = figure_data['other_figs'];
    figure_data_keys = Object.keys(figure_data);

    //update tables
    if (figure_data_keys.includes(cr_figs[0])){
        m0cr_data = figure_data[cr_figs[0]];
        update_table(m0cr, m0cr_data);
    };
    if (figure_data_keys.includes(cm_figs[0])){
        m0cm_data = figure_data[cm_figs[0]];
        update_table(m0cm, m0cm_data); 
    }
    if (figure_data_keys.includes(cr_figs[1])){
        m1cr_data = figure_data[cr_figs[1]];
        update_table(m1cr, m1cr_data);
    }
    if (figure_data_keys.includes(cm_figs[1])){
        m1cm_data = figure_data[cm_figs[1]];
        update_table(m1cm, m1cm_data);
    }
    if (figure_data_keys.includes(cr_figs[2])){
        m2cr_data = figure_data[cr_figs[2]];
        update_table(m2cr, m2cr_data);  
    }
    if (figure_data_keys.includes(cm_figs[2])){
        m2cm_data = figure_data[cm_figs[2]];
        update_table(m2cm, m2cm_data); 
    }

    //update figures
    todays_user_act.src = imgsrc_base + figure_data[other_figs[0]]
    todays_user_act.onload = function () {
        tua_width = todays_user_act.getBoundingClientRect().width;
        right_side_width = figures.getBoundingClientRect().width;
        tua_scale_factor = right_side_width / tua_width;
        tua_width = tua_width*tua_scale_factor
        tua_height = todays_user_act.getBoundingClientRect().height*tua_scale_factor;
        canvas_todays_user_act_stats.width = tua_width;
        canvas_todays_user_act_stats.height = tua_height;
        ctx_todays_user_act_stats.clearRect(0, 0, canvas_todays_user_act_stats.width, canvas_todays_user_act_stats.height)
        ctx_todays_user_act_stats.drawImage(todays_user_act, 0, 0, tua_width, tua_height);
        //start loading remaining figures
        right_side_fig_height = total_height - tua_height - total_height*margin/100;
        right_side_fig_width = right_side_width/3 - right_side_width*margin/100;
        canvas_continuous_stats.style.top = tua_height + total_height*margin/100 + "px";
        canvas_continuous_stats.width = right_side_width;
        canvas_continuous_stats.height = right_side_fig_height;
        pred_acc_date.src = imgsrc_base + figure_data[other_figs[1]];
    }
    var right_side_fig_width, pad_width, uu_width
    var right_side_fig_height
    var pad_offset, uu_x_offset
    pred_acc_date.onload = function () {
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
        pad_offset = right_side_fig_height - pad_height;
        ctx_continuous_stats.clearRect(0, 0, canvas_continuous_stats.width, canvas_continuous_stats.height)
        ctx_continuous_stats.drawImage(pred_acc_date, 0, pad_offset, pad_width, pad_height);
        //continue loading remaining figures
        user_usage.src = imgsrc_base + figure_data[other_figs[2]]
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
        uu_x_offset = pad_width + right_side_width*margin/100;
        ctx_continuous_stats.drawImage(user_usage, uu_x_offset, uu_y_offset, uu_width, uu_height);
        //load remaining figure
        gest_counts.src = imgsrc_base + figure_data[other_figs[3]]
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
        gc_x_offset = uu_x_offset + uu_width + right_side_width*margin/100;
        ctx_continuous_stats.drawImage(gest_counts, gc_x_offset, gc_y_offset, gc_width, gc_height);
    }
});