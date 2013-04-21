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
			var facebook_id = response.authResponse.userID;
			var access_token = response.authResponse.accessToken;
			//alert(access_token);
			if (response.hasOwnProperty("error")) {
        		alert("Error: " + response.error.message);
    		}

			FB.api('/me', function(response) {
		    	alert("Name: "+ response.name + "\nFirst name: "+ response.first_name + 
		    		"\nLast name: " + response.last_name + "\nID: "+ response.id);
		    	var img_link = "http://graph.facebook.com/"+ response.id + "/picture?type=large";
		    	alert(img_link);
		    	// alert(response.gender + " " + response.updated_time + " ");

		    	var image = document.getElementById('image');
              	image.src = 'https://graph.facebook.com/' + response.id + '/picture?type=large';
              	var name = document.getElementById('name');
              	name.innerHTML = response.name
			});

			// another way to fetch the picture
			/* FB.api('/me/picture?type=large', function(response) {
		    	console.log(response.data.url);
			}); */ 


			// connected
		} else if (response.status === 'not_authorized') {
			// not_authorized
			login();
		} else {
			login();
			// not_logged_in
		}
	});


};

// Load the SDK Asynchronously
(function(d){
	var js, id = 'facebook-jssdk', ref = d.getElementsByTagName('script')[0];
	if (d.getElementById(id)) {return;}
	js = d.createElement('script'); js.id = id; js.async = true;
	js.src = "//connect.facebook.net/en_US/all.js";
	// For debugging 
	//js.src = "//connect.facebook.net/en_US/all/debug.js";
	
	ref.parentNode.insertBefore(js, ref);
}(document)); 


/*(function(d, s, id) {
	var js, fjs = d.getElementsByTagName(s)[0];
	if (d.getElementById(id)) return;
	js = d.createElement(s); js.id = id;
	js.src = "//connect.facebook.net/en_US/all.js";
	fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));*/

function testAPI() {
    console.log('Welcome!  Fetching your information.... ');
    FB.api('/me', function(response) {
        console.log('Good to see you, ' + response.name + '.');
    });
}


function login() {
    FB.login(function(response) {
        if (response.authResponse) {
            // connected
            testAPI();
        } else {
            // cancelled
        }
    });
}


function logout() {
    FB.logout(function(response) {
        console.log('User is now logged out');
    });
}