//Get the popup div
var popup = document.getElementById("popupDiv");

//Get the button that opens it
var btn = document.getElementById("popupBtn");

//Get the element with the close button
var span = document.getElementsByClassName("closeBtn")[0];

btn.onclick = function(){
	popup.style.display = "block";
}

span.onclick = function(){
	popup.style.display = "none";
}

window.onclick = function(event){
	if(event.target == popup){
		popup.style.display = "none";
	}
}