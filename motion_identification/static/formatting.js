//position and size elements depending on screen resolution

//create canvas for displaying training image 
var drawCanvas = document.createElement('canvas');
drawCanvas.id = 'trainImage'
drawCanvas.style.width = video_width + "px";
drawCanvas.style.height = video_height + "px";
drawCanvas.style.left = 0.5*(window.innerWidth-video_width) + "px";
bottom_margin = window.innerHeight/128
drawCanvas.style.top = (window.innerHeight/4-bottom_margin+video_height) + "px";
drawCanvas.style.border = "thin solid";
document.body.appendChild(drawCanvas);
var drawCtx = drawCanvas.getContext("2d");
//canvas notes
// style width and height (px) define the overall size of the canvas on the document
// attribute width and height define the maximum range of values canvas object dimensions can be
// the ratio of draw / fill width and height and attribute width / height define how much a drawn objects fills a canvas
// example: a canvas with attribute height = width = 1000, drawing height = width = 250, and style height = width = 500px will take up a 500px X 500px plot on the document. The drawn object will occupy 1/16 of this plot

//modify position of text block elements
right_content = document.querySelector(".right_content")
left_content = document.querySelector(".left_content")
div_input_and_prediction = document.querySelector("div.input_and_prediction")
top_video = document.getElementById("myVideo").getBoundingClientRect()
bottom_video = document.getElementById("trainImage").getBoundingClientRect()

//position elements
max_width = 5*window.innerWidth/16;
padding = window.innerWidth/48;
right_content.style.maxWidth = max_width + "px"
right_content.style.paddingRight = padding + "px"
right_content.style.paddingLeft = padding + "px"
left_content.style.maxWidth = max_width + "px"
left_content.style.paddingRight = padding + "px"
left_content.style.paddingLeft = padding + "px"

top_video_bottom = top_video.bottom
bottom_video_top = bottom_video.top
video_center = top_video.left + top_video.width/2
div_input_and_prediction.style.left = video_center - div_input_and_prediction.getBoundingClientRect().width/2 + "px"
div_input_and_prediction.style.top = top_video_bottom + (bottom_video_top-top_video_bottom-div_input_and_prediction.getBoundingClientRect().height)/2 + "px"

//show elements
right_content.style.visibility = "visible"
left_content.style.visibility = "visible"
div_input_and_prediction.style.visibility = "visible"