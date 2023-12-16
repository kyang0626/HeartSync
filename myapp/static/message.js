  // Send Message Function
  function sendMessage(chatId) {
    var senderId = getUserId();
    const messageInput = $("#messageInput");
    const message = messageInput.val();
    messageInput.val("");

    var notification = "message";

    $.ajax({
        type: "POST",
        url: "/messages",
        data: { action: "send-message", chatUserId: chatId, content: message},
        success: function(response) {
            console.log("Success", response);
            // socket.emit("notification", { senderId: senderId, recipientId: chatId, notification: notification});
            socket.emit("message", {senderId: senderId, recipientId: chatId, message: message, senderPic: response.senderPic, recipientPic: response.recipientPic});
        },
        error: function(error) {
            console.error("Error in sending message to user", error);
        }
    });
}

// Initiate conversation with selected user
$("#sendMessageOnNotification").on("click", function() {
    var senderId = $(".user-container").data("user-id");
    console.log("datauserid: ", senderId);

    window.location.href = "/messages?senderId=" + senderId;
});

$("#sendMessageOnSelect").on("click", function() {
    var senderId = $(".selected-user").data("selected-id");
    console.log("datauserid: ", senderId);

    window.location.href = "/messages?senderId=" + senderId;
});

// Send message
$("#sendButton").on("click", function() {
    chatUserId = $("#chat-window").data("user-id");
    // console.log("chat user id: ", chatUserId);

    sendMessage(chatUserId);
});

// send message sound
var sendSound = new Audio('../static/sound/send-msg.mp3');
function sendAudio() {
    sendSound.play();
}

// receive message
var receiveSound = new Audio('../static/sound/receive-msg.mp3');
function receiveAudio() {
    receiveSound.play();
}

// Get message and display to chat log
socket.on("message", (data) => {
    var currentUserId = getUserId();

    socket.emit('join_room', {room: data.room});

    // If user is the receiver
    if (currentUserId === data.room) {
        $("#output .message-left:last .message-pic-div").remove();
        $("#output").append("<div class='message-left'><div class='message-pic-div'><img class='message-pic' src='" + data.senderPic + "'></div><p class='messageP' id='message-left'>" + data.message + "</p></div>");
        $("#message-nav").css("background-color", "red");
        $(".senderMessage").text(data.message);
        console.log(data.message)
        $("#output").scrollTop($("#output")[0].scrollHeight);
    }
    // or if user is sender
    else {
        $("#output").append("<div class='message-right'><p class='messageP' id='message-right'>" + data.message + "</p></div>");
        console.log("Message sent");
        sendAudio();
        $(".senderMessage").text("");
        $("#output").scrollTop($("#output")[0].scrollHeight);
    }
});