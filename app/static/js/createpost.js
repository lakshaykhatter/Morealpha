$( document ).ready(function() {
   var div = document.createElement("div");

	var el = $(".ql-editor").children()

	for ( i=0; i < el.length; i++ ) {
		div.appendChild(el[i]);
	}
	
	console.log(div.innerHTML)
});