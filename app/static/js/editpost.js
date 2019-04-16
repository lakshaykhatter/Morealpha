
$( document ).ready(function() {	

	$('form').on('submit', function(event) {

		var div = document.createElement("div");

		var el = $(".ql-editor").children();
	
		for ( i=0; i < el.length; i++ ) {
			div.appendChild(el[i]);
		}
		var url = window.location.href;  
		var id = url.split("/")[url.split("/").length-1];

		$.ajax({
			data : {
				title : $("#title").val(),
				tickers: $("#tickers").val(),
				post : div.innerHTML

			},

			type : 'POST',
			url : '/editpost/' + id 
		})
		
		.done(function(data) {
			console.log(data)

			if (data.error) {
				$('#errorAlert').text(data.error).show();
				$('#successAlert').hide();
				$('.ql-editor').appendChild(div.innerHTML);
			}
			else {
				$('#successAlert').text(data.success).show();
				$('#errorAlert').hide();
				$('.ql-editor').appendChild(div.innerHTML);
			}

		});

		event.preventDefault();

	});

});