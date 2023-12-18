// show edit
function toggleEditProfile() {
    var editProfile = document.getElementById("edit-profile");
    if (editProfile.style.display === 'none') {
        editProfile.style.display = "block";
        console.log(editProfile.style);
    } else {
        editProfile.style.display = "none";
        console.log(editProfile.style);
    }
}

// Get current user id
function getUserId() {
    var userInSession = $(".user-panel").data("userid");
    // console.log("user in session: ", userInSession);

    return userInSession;
}

// Display notification
function fetchNotifications() {
    $.ajax({
        type: "POST", 
        url: "/notification",
        data: { action: "get-user-notification" },
        success: function(response) {
            console.log("Notifications fetched successfully:", response);

            if (response == null) {
                console.log("No notifications");
            }
        },
        error: function(error) {
            console.error("Error fetching notifications:", error);
        }
    });
}

 // next function
 function nextUser() {
    // get main user
    var currentUserId = getUserId();

    $.ajax({
        type: "GET",  
        url: "/matches/next-user",  
        data: { action: "next-user", currentUserId: currentUserId},
        success: function(response) {

            console.log(response);
            // Create a temporary element to hold the response HTML
            // var tempElement = $('<div>').html(response);

            // // Extract the data from the HTML
            // var userId = tempElement.find('#random-user').data('user-id');
            // var picture = tempElement.find('#random-user-img').attr('src');
            // var fullname = tempElement.find('#random-user-fullname').text();
            // var age = tempElement.find('#random-user-age').text();

            // // Log or use the extracted data as needed
            // console.log("Random-user-id: ", userId);
            // console.log("Picture: ", picture);
            // console.log("Fullname: ", fullname);
            // console.log("Age: ", age);

            $("#random-user").attr("data-user-id", response.userid);
            $("#random-user-img").attr("src",  response.picture);
            $("#random-user-fullname").text(response.fullname);
            $("#random-user-age").text(response.age);
        },
        error: function(error) {
            console.error("Error in displaying random users:", error);
        }
    });
}

$(document).ready(function() {

    // close footer
    $("#closeFooter").on("click", function() {
        $(".footer").css("display", "none");
    })

    // next user
    $("#next-btn").on("click", function() {
        nextUser();
    });

    // return to random users
   $("#selected-user-img").on("click", () => {
        location.reload();
    })

     // like button
    $("body").on("click", "#interested", function() {
        var senderId = getUserId();
        var recipientId = $("#random-user").data("user-id");

        console.log("You liked: ", recipientId);

        const notification = "like";

        $.ajax({
            type: "POST",  
            url: "/matches",  
            data: { action: "interested", user_id: recipientId, notification: notification },
            success: function(response) {
                $("#random-user").removeAttr("data-user-id")
                console.log(response.userid + " has been liked and removed from display!");
                console.log("Interest inserted successfully", response);
                socket.emit("notification", { senderId: senderId, recipientId: recipientId, notification: notification});
                
                cardHTML = '<div class="card display-user" data-selected-id="' + response.userid + '">' +
                '<img src="' + response.picture + '" alt="matches-pic" data-interest-pic="' + response.picture + '">' +
                '<div class="card-body" style="height: 300px; width: 100%;"></div>' +
                '<p><a href="#" class="matches-name" id="interest-name">' + response.fullname + '</a></p>' +
                '</div>';           
                
                // append card to panel
                $(".card-slots").append(cardHTML);

                // location.reload();
                nextUser();
            },
            error: function(error) {
                console.error("Error inserting interest:", error);
            }
        });
    });

    // dislike 
    $("#not-interested").on("click", function() {
        var userId = $(this).data("user-id");

        $.ajax({
            type: "POST",  
            url: "/matches",  
            data: { action: "not-interested", user_id: userId },
            success: function(response) {
                console.log("Marked as not interested successfully");
                location.reload()
            },
            error: function(error) {
                console.error("Error marking not interested:", error);
            }
        });
    });

    // show selected user's info
   $(".card-slots").on("click", ".display-user", function() {
        var selectedUser = $(this).data("selected-id");
        // var interestPic = $(this).data("interest-pic");

        console.log("selectedUser:", selectedUser);
        // console.log("Interest Pic:", interestPic);

        $('#selectedUserModal').modal('toggle');

        $.ajax({
            type: "POST",
            url: "/matches",
            data: { action: "display-user", selectedUser: selectedUser },
            dataType: "json",
            success: function(response) {
                console.log("User retrieve from client", response);
                // $(".random-users").css("display", "none");
                // $(".selected-user").css("display", "block");
                $(".selected-user-container").attr("data-selected-id", response.userid)
                $("#selected-user-fullname").text(response.fullname);
                $("#selected-user-img").attr("src", response.picture);
                $("#selected-age").text(response.age);
                $("#selected-city").text(response.city);
                $("#selected-state").text(response.state);
                $("#selected-school").text(response.school);
                $("#selected-company").text(response.company);
            },
            error: function(error) {
                console.error("Error in retrieving userid and userpic:", error);
            }
        });
   });

   // OPEN CHAT WINDOW from Messge route
   $(".conversation-slot").on("click", function() {
        var currentUserId = getUserId();
        var chatUserId = $(this).data("user-id");

        console.log("Open chat User ID:", chatUserId);

        // var senderInfo = "?senderId=" + chatUserId;

        // window.location.href = senderInfo;

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
        })

    });
    
    // like back and add to interest
    $("#acceptLike").on("click", function() {
        var currentUserId = getUserId();
        var sender_interest = $(".user-container").data("user-id");
        var notification = "accept";
        
        $.ajax({
            type: "POST",  
            url: "/notification",  
            data: { action: "accept", senderId: sender_interest},
            success: function(response) {
                // console.log("Interest inserted successfully");
                socket.emit("notification", { senderId: currentUserId, recipientId: sender_interest, notification: notification})
                $("#sendMessageOnNotification").css("display", "block");
                $("#declineLike").css("display", "none");
                
            },
            error: function(error) {
                console.error("Error inserting interest:", error);
            }
        });
    })

    // decline like and add to non-interest
    $("#declineLike").on("click", function() {
        var currentUserId = getUserId();
        var sender_interest = $(".user-container").data("user-id");
        
        $.ajax({
            type: "POST",  // Change to "GET" if your server endpoint expects a GET request
            url: "/notification",  // Replace with the actual endpoint URL
            data: { action: "decline", senderId: sender_interest},
            success: function(response) {
                console.log("Successfully decline user interest");
                window.location.href = "/matches";
                
            },
            error: function(error) {
                console.error("Error inserting interest:", error);
            }
        });
    })
});

// display more info about users
function moreInfo() {
    $(".more-info").css("display", "block");
    console.log("working");
}


// LISTENERS
const socket = io.connect('http://127.0.0.1:5000');

// Test Connection
socket.on("connect", () => {
    // testing connection
    console.log("Connected to server");

    // Call the function to get the user ID
    var currentUserId = getUserId();
    // console.log(currentUserId);

    socket.emit('join_room', { room: currentUserId} );
});


