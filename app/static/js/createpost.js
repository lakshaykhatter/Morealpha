$( document ).ready(function() {

	$('form').on('submit', function(event) {

		var div = document.createElement("div");

		var el = $(".ql-editor").children();
	
		for ( i=0; i < el.length; i++ ) {
			div.appendChild(el[i]);
		}

		$.ajax({
			data : {
				title : $("#title").val(),
				ticker1 : $("#ticker1").val(),
				ticker2 : $("#ticker2").val(),
				ticker3 : $("#ticker3").val(),
				ticker4 : $("#ticker4").val(),
				ticker5 : $("#ticker5").val(),
				post : div.innerHTML

			},

			type : 'POST',
			url : '/post'
		})
		
		.done(function(data) {

			if (data.error) {
				$('#errorAlert').text(data.error).show();
				$('#successAlert').hide();
			}
			else {
				$('#successAlert').text(data.success).show();
				$('#errorAlert').hide();
			}

		});

		event.preventDefault();

	});

});