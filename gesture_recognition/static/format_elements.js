// create and size webcam video element height relative to title and user interface
u = document.getElementById("input_and_prediction")
// debugger
u_height = u.getBoundingClientRect().height
t = document.getElementById("title")
t_bottom = t.getBoundingClientRect().bottom
s = document.getElementById("myVideo")
var video_height = (window.innerHeight - t_bottom - u_height - 20)/2
var video_width = video_height*16/9
s.style.height = video_height + "px";
s.style.width = video_width + "px";

// center webcam video element and place below title
s.style.top = t_bottom + "px"
s.style.left = 0.5*(window.innerWidth-video_width) + "px";
s.style.border = "thin solid";

// position user interface relative to webcam canvas
u.style.top = s.getBoundingClientRect().bottom + "px"
u.style.width = video_width + "px"
u.style.left = 0.5*(window.innerWidth-video_width) + "px";

//position login centered on user interface
l = document.getElementById("log_form")
// l.style.height = u.getBoundingClientRect().height + "px"
l.style.width = video_width + "px"
l.style.top = s.getBoundingClientRect().bottom + (u.getBoundingClientRect().height - l.getBoundingClientRect().height)/2 + "px"
l.style.left = 0.5*(window.innerWidth-video_width) + "px";

//create canvas for displaying training image 
var drawCanvas = document.createElement('canvas');
drawCanvas.id = 'trainImage'
drawCanvas.style.width = video_width + "px";
drawCanvas.style.height = video_height + "px";
drawCanvas.style.left = 0.5*(window.innerWidth-video_width) + "px";
drawCanvas.style.top = u.getBoundingClientRect().bottom + "px";
drawCanvas.style.border = "thin solid";
document.body.appendChild(drawCanvas);
var drawCtx = drawCanvas.getContext("2d");
// style width and height (px) define the overall size of the canvas on the document
// attribute width and height define the maximum range of values canvas object dimensions can be
// the ratio of draw / fill width and height and attribute width / height define how much a drawn objects fills a canvas
// example: a canvas with attribute height = width = 1000, drawing height = width = 250, and style height = width = 500px will take up a 500px X 500px plot on the document. The drawn object will occupy 1/16 of this plot

//size text block elements to fill page and position them below log in information
right_content = document.querySelector(".right_content")
left_content = document.querySelector(".left_content")
width = (window.innerWidth - drawCanvas.getBoundingClientRect().width)/2;
padding = 25;
content_offset = 135
right_content.style.top = content_offset + "px"
right_content.style.maxWidth = width + "px"
right_content.style.padding = padding + "px"
right_content.style.right = 0 + "px"
left_content.style.top = content_offset + "px"
left_content.style.maxWidth = width + "px"
left_content.style.padding = padding + "px"
left_content.style.left = 0 + "px"

//show elements
right_content.style.visibility = "visible"
left_content.style.visibility = "visible"
