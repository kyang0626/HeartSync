// Get current user id
function getUserId() {
    var userInSession = $(".user-panel").data("userid");
    // console.log("user in session: ", userInSession);

    return userInSession;
}

// Send Message Function
function sendMessage(chatId) {
var senderId = getUserId();
var chatId = $("#chat-window").data("user-id");
const messageInput = $("#messageInput");
const message = messageInput.val();
messageInput.val("");

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

$(document).ready(function() {

    // Initiate conversation with selected user
    $("#sendMessageOnNotification").on("click", function() {

        var chatId = $(".user-container").data("user-id");

        window.location.href = "/messages?senderId=" + chatId;

    });

    $("#sendMessageOnSelect").on("click", function() {

        var chatId = $(".selected-user-container").data("selected-id");

        window.location.href = "/messages?senderId=" + chatId;

    });

    // Send message
    $("#sendButton").on("click", function() {
        chatUserId = $("#chat-window").data("user-id");
        // console.log("chat user id: ", chatUserId);

        sendMessage(chatUserId);
    });

    // OPEN CHAT WINDOW from Message route
    $(".conversation-slot").on("click", function() {
        var chatUserId = $(this).data("user-id");

        console.log("Open chat User ID:", chatUserId);

        $.ajax({
            type: "POST",
            url: "/messages",
            data: { action: "display-conversation", selectedUser: chatUserId },
            success: function(response) {
                // console.log("success", response);
                // console.log("messages", response.allMessages);
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

            },
            error: function(error) {
                console.log("error in showing conversation", error);
            }
        });

    });

    // Check if the current URL contains "/messages"
    if (window.location.href.includes("/messages?senderId=")) {
        // If the URL contains "/messages?senderId=", trigger the modal toggle
        var currentUrl = window.location.href;

        var urlObj = new URL(currentUrl);
        var searchParams = urlObj.searchParams;
        var senderId = searchParams.get('senderId');

        if (senderId) {        
            console.log("senderId from urlParams: ", senderId);

            $.ajax({
                type: "GET",
                url: "/get-user",
                data: { sender: senderId },
                success: function(response) {
                    console.log("success", response);

                    $("#chatWindowModal").modal("toggle");
                    $("#chat-window").attr("data-user-id", response.userData.user_id);
                    $("#user-message-img").attr("src", response.userData.picture);
                    $("#user-message-name").text(response.userData.full_name);

                    for (var i = 0; i < response.messageData.length; i++) {

                        if (currentUserId === response.messageData[i].recipient_id) {
                            $("#output").append("<div class='message-left'><div class='message-pic-div'><img class='message-pic' src='" + response.selectedUserProfile.picture + 
                            "' alt=''></div><p class='messageP' id='message-left'>" + response.allMessages[i].content + "</p></div>");
                        }
                        else if (currentUserId === response.messageData[i].sender_id) {
                            $("#output").append("<div class='message-right'><p class='messageP' id='message-right'>" + response.messageData[i].content + "</p></div>");
                        }
                    }

                },
                error: function(error) {
                    console.log("error in retrieving user's profile");
                }
            })
            

        }
        else {
            console.log("unable to retrieve senderid params");
        }
    }

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

    // console.log("chat room: ", chatWindow);

    // console.log("sender: ", data.senderId);
    // console.log("recipient: ", data.recipientId);

    // If user is the receiver
    if (currentUserId === data.room) {
        // remove previous pic message
        $("#output .message-left:last .message-pic-div").remove();        

        // Check if the chat window is the user
        if (chatWindow === data.senderId) {
            console.log("its this!")
            $("#output").append("<div class='message-left'><div class='message-pic-div'><img class='message-pic' src='" + data.senderPic + "'></div><p class='messageP' id='message-left'>" + data.message + "</p></div>");
            $("#message-nav").css("background-color", "red");

            // chat-window scrolls down when send
            $("#output").scrollTop($("#output")[0].scrollHeight);

            // display user's message on card-slot
            $(".senderMessage").text(data.message);

        }
        // else if user is the recipient
        else if (currentUserId === data.recipientId) {
            console.log("its this 2");
            $("#output").append("<div class='message-left'><div class='message-pic-div'><img class='message-pic' src='" + data.senderPic + "'></div><p class='messageP' id='message-left'>" + data.message + "</p></div>");
            $("#message-nav").css("background-color", "red");
            
            // chat-window scrolls down when send
            $("#output").scrollTop($("#output")[0].scrollHeight);
            $(".senderMessage").text(data.message);
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