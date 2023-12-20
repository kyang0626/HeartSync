  // Send Message Function
  function sendMessage(chatId) {
    var senderId = getUserId();
    var chatId = $("#chat-window").data("user-id");
    const messageInput = $("#messageInput");
    const message = messageInput.val();
    messageInput.val("");

    var notification = "message";

    $.ajax({
        type: "POST",
        url: "/messages",
        data: { action: "send-message", chatUserId: chatId, content: message},
        success: function(response) {
            console.log("Success", response.content);
            // socket.emit("notification", { senderId: senderId, recipientId: chatId, notification: notification});
            
            socket.emit("message", {senderId: senderId, recipientId: chatId, message: message, senderPic: response.senderPic, recipientPic: response.recipientPic});
        },
        error: function(error) {
            console.error("Error in sending message to user", error);
        }
    });
}

$(document).ready(function () {

    // Initiate conversation with selected user
    $("#sendMessageOnNotification").on("click", function() {
        var senderId = $(".user-container").data("user-id");
        console.log("datauserid: ", senderId);

        window.location.href = "/messages?senderId=" + senderId;
    });

    $("#sendMessageOnSelect").on("click", function() {
        var chatId = $(".selected-user-container").data("selected-id");

        var message = "Hi";

        $.ajax({
            type: "POST",
            url: "/messages",
            data: { action: "quick-message", chatUserId: chatId, content: message},
            success: function(response) {
                console.log("Success", response.content);
                // socket.emit("notification", { senderId: senderId, recipientId: chatId, notification: notification});
                window.location.href = "/messages?senderId=" + chatId;

                socket.emit("message", {senderId: response.sender, recipientId: response.recipient, message: response.content, senderPic: response.senderPic, recipientPic: response.recipientPic});
                
            },
            error: function(error) {
                console.error("Error in sending message to user", error);
            }
        });

    });

    // Check if the current URL contains "/messages"
    // if (window.location.href.includes("/messages")) {
    //     // If the URL contains "/messages", trigger the modal toggle
    //     var currentUrl = window.location.href;

    //     console.log("url: ", currentUrl);

    //     var urlParams = new URLSearchParams(currentUrl);

    //     var senderId = urlParams.get("senderId");
    //     console.log("SenderId:", senderId);

    //     if (senderId) {
    //         console.log("SenderId:", senderId);

    //         $("#chatWindowModal").modal("toggle");
    //     }
    //     else {
    //         console.log("unable to retrieve senderid params");
    //     }

    // }

    // Send message
    $("#sendButton").on("click", function() {
        chatUserId = $("#chat-window").data("user-id");
        // console.log("chat user id: ", chatUserId);

        sendMessage(chatUserId);
    });

    // OPEN CHAT WINDOW from Message route
    $(".conversation-slot").on("click", function() {
        var currentUserId = getUserId();
        var chatUserId = $(this).data("user-id");

        console.log("Open chat User ID:", chatUserId);

        $.ajax({
            type: "POST",
            url: "/messages",
            data: { action: "display-conversation", selectedUser: chatUserId },
            success: function(response) {
                console.log("success", response);
                console.log("messages", response.allMessages);
                // emit("message", {"room": response.selectedUserProfile.user_id})
                $("#chatWindowModal").modal("toggle");

                $("#chat-window").attr("data-user-id", response.selectedUserProfile.user_id);
                $("#user-message-img").attr("src", response.selectedUserProfile.picture);
                $("#user-message-name").text(response.selectedUserProfile.full_name);

                $("#output").empty();

                console.log("chat user: ", response.selectedUserProfile.user_id);
                
                for (var i = 0; i < response.allMessages.length; i++) {

                    if (currentUserId === response.allMessages[i].recipient_id) {
                        $("#output").append("<div class='message-left'><div class='message-pic-div'><img class='message-pic' src='" + response.selectedUserProfile.picture + 
                        "' alt=''></div><p class='messageP' id='message-left'>" + response.allMessages[i].content + "</p></div>");
                    }
                    else if (currentUserId === response.allMessages[i].sender_id) {
                        $("#output").append("<div class='message-right'><p class='messageP' id='message-right'>" + response.allMessages[i].content + "</p></div>");
                    }
                }

                // $(".message-container").css("display", "block");
            },
            error: function(error) {
                console.log("error in showing conversation", error);
            }
        });

    });


});


// send message sound
var sendSound = new Audio('../static/sound/send-msg.mp3');
function sendAudio() {
    sendSound.play();
}

// Get message and display to chat log
socket.on("message", (data) => {
    var currentUserId = getUserId();

    socket.emit('join_room', {room: data.room});

    var chatWindow = $(".message-container").data("user-id");

    console.log("chat room: ", chatWindow);

    console.log("sender: ", data.senderId);
    console.log("recipient: ", data.recipientId);

    // If user is the receiver
    if (currentUserId === data.room) {
        // remove previous pic message
        $("#output .message-left:last .message-pic-div").remove();        

        // Check if the chat window is the user
        if (chatWindow === data.senderId) {
            console.log("its this!")
            $("#output").append("<div class='message-left'><div class='message-pic-div'><img class='message-pic' src='" + data.senderPic + "'></div><p class='messageP' id='message-left'>" + data.message + "</p></div>");
            $("#message-nav").css("background-color", "red");
            $(".senderMessage").text(data.message);
            $("#output").scrollTop($("#output")[0].scrollHeight);
        }
        // or if user is the recipient
        else if (currentUserId === data.recipientId) {
            console.log("its this 2");
            $("#output").append("<div class='message-left'><div class='message-pic-div'><img class='message-pic' src='" + data.senderPic + "'></div><p class='messageP' id='message-left'>" + data.message + "</p></div>");
            $("#message-nav").css("background-color", "red");
            $(".senderMessage").text(data.message);
            $("#output").scrollTop($("#output")[0].scrollHeight);
        }
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