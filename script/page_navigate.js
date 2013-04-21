function openGroupsPage(){
    document.getElementById("groups-page").style.display = "block";
    document.getElementById("profile-page").style.display = "none";
}

function openProfilePage(){
    document.getElementById("profile-page").style.display = "block";
    document.getElementById("groups-page").style.display = "none";
}

function openGroupInfoPage(){
    document.getElementById("group-info-page").style.display = "block";
    document.getElementById("chat-page").style.display = "none";
}

function openChatPage(){
    document.getElementById("chat-page").style.display = "block";
    document.getElementById("group-info-page").style.display = "none";
}

function openPopupBox(){
    $("#popup-box").fadeToggle(200);
}