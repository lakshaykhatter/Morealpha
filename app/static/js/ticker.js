$( document ).ready(function() {


	var ticker = window.location.pathname.split('/').slice(-1)[0]

	// if follow doesn't button exists?
	if( $("#followButton").length != 0) {
	
		$("#followButton").click(function() {
		
		console.log('hello from below');

		$.get( '/follow/' + ticker, function( data ) {
    		$("#followButton").text("Remove from watchlist");	
    		$("#followButton").attr('id', 'unfollowButton');

		});
	});


	} else {

	$("#unfollowButton").click(function() {
		
		console.log('hello');

		$.get( '/unfollow/' + ticker, function( data ) {
	  		$("#unfollowButton").text("Add to watchlist");
	  		$("#unfollowButton").attr('id', 'followButton');
			console.log('hello from above')
		});
	});




	}

});