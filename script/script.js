updateChat = function(data){
    $.ajax({type: "GET", url: ("/chat"), success:function(result){
        if(result === "error"){
            showWarning("Warning: Update chat message failed");
        }
        else{
            document.getElementById("chat-content-list").innerHTML = result;
        }
    }}).error(function(){
        showWarning("Warning: Channel failed when updating chat message");
    });
};

sendChat = function(){
    var chat_line = new Object();
    chat_line.user_name = document.getElementById("name").innerHTML;
    chat_line.avatar_url = document.getElementById("avatar_url").innerHTML;
    var chat_content = document.getElementById("user-chat-content").value;
    if(chat_content.length == 0){
        showWarning("Warning: Please enter chat content");
        return;
    }
    chat_line.chat_content = chat_content;
    chat_line = JSON.stringify(chat_line);
    $.ajax({type: "POST", url: ("/chat"), 
            data: {chat: chat_line}, success:function(result){
        if(result === "error"){
            showWarning("Warning: Send chat message failed");
        }
        else{
            document.getElementById("user-chat-content").value = "";
        }
    }}).error(function(){
        showWarning("Warning: Channel failed when sending chat message");
    });
};

showWarning = function(warning){
    document.getElementById("warning").innerHTML = warning;
    document.getElementById("warning").style.background = "#FF0000";
    setTimeout(hideWarning, 5000);
};

hideWarning = function(){
    document.getElementById("warning").style.background = "#FFFFFF";
};

onOpened = function(){
	showWarning("Build chat channel success");
    updateChat("chat change")
};

onMessage = function(m){
    updateChat(m.data);
};

initialize = function() {
    var token = document.getElementById("token").innerHTML;
    var channel = new goog.appengine.Channel(token);
    var handler = {
      'onopen': onOpened,
      'onmessage': onMessage,
      'onerror': function() {},
      'onclose': function() {}
    };
    var socket = channel.open(handler);
    socket.onopen = onOpened;
    socket.onmessage = onMessage;
};      

setTimeout(initialize, 100);