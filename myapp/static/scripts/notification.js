// Get current user id
function getUserId() {
    var userInSession = $(".user-panel").data("userid");
    // console.log("user in session: ", userInSession);

    return userInSession;
}

$(document).ready(function() {

    // Display notification
    $(".panel-header-info").on("click", ".fetch-notifications", function() {

        $.ajax({
            type: "GET", 
            url: "/get-notification",
            success: function(response) {
                console.log("Notifications fetched successfully:", response);

                $(".notification-list").empty();
                
                for (var i = 0; i < response.notifications.length; i++) {
                    $(".notification-list").append("<li class='notification-slot' data-user-id='" 
                        + response.senderInfo[i].senderid + "'><img id='notification-img' src='" + response.senderInfo[i].senderPic 
                        + "'>You have received a " + response.notifications[i].notificationType + "</li>");
                }

            },
            error: function(error) {
                console.error("Error fetching notifications:", error);
            }
        });

    })
        

    // open the notification
    $(".notification-list").on("click", ".notification-slot", function() {
        var sender_notification = $(this).data("user-id");
        console.log(sender_notification);
    
        $.ajax({
            type: "POST",
            url: "/matches",
            data: { action: "show-sender-notification", senderId: sender_notification },
            success: function(response) {
                console.log("sender info", response);

                window.location.href = "/notification?senderId=" + sender_notification;

            },
            error: function(error) {
                console.log("Error in retrieving id", error);
            }
        })
    
    })

})

var notificatonSound = new Audio('../static/sound/notification.mp3');

function playSound() {
    notificatonSound.play();
}

// Listener
socket.on("notification", (data) => {
    // console.log("Client side: notification received", data);

    var currentUserId = getUserId();
    
    console.log("notification current user: ", currentUserId);
    
    socket.emit('join_room', {room: data.room});

    console.log(data.room);

    //if user is the recipient
    if (currentUserId === data.room) {
        playSound();
        console.log("You've received a notification from " + data.senderId);
        $(".notification-list").append("<li class='notification-slot' data-user-id='" + data.senderId + "'>" + data.senderId + " has liked you</li>");
        $(".fa-bell").css({"color": "orange", "font-size": "1.8em"}).addClass("fa-shake");

        $("#notificationModal").modal("show");
    }
});