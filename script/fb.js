window.fbAsyncInit = function() {
	FB.init({
	appId      : '280444438756675', // App ID
	channelUrl : '//yummy-webapp.appspot.com/channel.html', // Channel File
	status     : true, // check login status
	cookie     : true, // enable cookies to allow the server to access the session
	xfbml      : true  // parse XFBML
	});

	FB.getLoginStatus(function(response) {
	if (response.status === 'connected') {
		// connected
	} else if (response.status === 'not_authorized') {
		// not_authorized
	} else {
		// not_logged_in
	}
	});

	FB.Event.subscribe('auth.statusChange', handleStatusChange);
};

// Load the SDK Asynchronously
(function(d){
	var js, id = 'facebook-jssdk', ref = d.getElementsByTagName('script')[0];
	if (d.getElementById(id)) {return;}
	js = d.createElement('script'); js.id = id; js.async = true;
	js.src = "//connect.facebook.net/en_US/all.js";
	/* For debugging 
	js.src = "//connect.facebook.net/en_US/all/debug.js";
	*/
	ref.parentNode.insertBefore(js, ref);
}(document));


(function(d, s, id) {
	var js, fjs = d.getElementsByTagName(s)[0];
	if (d.getElementById(id)) return;
	js = d.createElement(s); js.id = id;
	js.src = "//connect.facebook.net/en_US/all.js#xfbml=1&appId=280444438756675";
	fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));
