
    // open the notification
    $(".notification-slot").on("click", function() {
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


// Listener
socket.on("notification", (data) => {
    // console.log("Client side: notification received", data);

    // console.log("Client side: recipient: ", data.room);
    socket.emit('join_room', {room: data.room});

    var currentUserId = getUserId();

    var notificatonSound = new Audio('../static/sound/notification.mp3');

    function playSound() {
        notificatonSound.play();
    }

    //if user is the recipient
    if (currentUserId === data.room) {
        playSound();
        console.log("You've received a notification from " + data.senderId);
        $(".notification-list").append("<li class='notification-slot' data-user-id='" + data.senderId + "'>" + data.senderId + " has liked you</li>");
        $(".fa-bell").css({"color": "orange", "font-size": "1.8em"}).addClass("fa-shake");

        $("#exampleModal").modal("show");
    }
});