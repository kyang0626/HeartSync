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
    var currentUserId = getUserId();
    
    $.ajax({
        type: "POST",  
        url: "/matches",  
        data: { action: "next-user", currentUserId: currentUserId},
        success: function(response) {
            console.log("Server Response:", response);

            $("#random-user").attr("data-user-id", response.userid);
            $("#random-user-img").attr("src", response.picture);
            $("#random-user-fullname").text(response.fullname);
            $("#random-user-age").text(response.age);

            console.log("Random-user-id: ", response.userid);
            
            
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
    $("#interested").on("click", function() {
        var senderId = getUserId();
        var recipientId = $(".random-users").data("user-id");
        console.log("You liked: ", recipientId);
        const notification = "like";

        $.ajax({
            type: "POST",  
            url: "/matches",  
            data: { action: "interested", user_id: recipientId, notification: notification },
            success: function(response) {
                console.log("Interest inserted successfully");
                socket.emit("notification", { senderId: senderId, recipientId: recipientId, notification: notification});
                
                // card html
                var cardHTML = '<div class="card display-user" data-selected-id="' + response.id + '">' +
                '<img src="' + response.picture + '" alt="matches-pic" data-interest-pic="' + response.picture + '">' +
                '<div class="card-body" style="height: 300px; width: 100%;"></div>' +
                '<p><a href="#" class="matches-name" id="interest-name">' + response.fullname + '</a></p>' +
                '</div>';

                // append card to panel
                $(".card-slots").append(cardHTML);

                // window.location.href = "/matches";
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
   $(".display-user").on("click", function() {
        var selectedUser = $(this).data("selected-id");
        // var interestPic = $(this).data("interest-pic");

        console.log("selectedUser:", selectedUser);
        // console.log("Interest Pic:", interestPic);

        $.ajax({
            type: "POST",
            url: "/matches",
            data: { action: "display-user", selectedUser: selectedUser },
            dataType: "json",
            success: function(response) {
                console.log("User retrieve from client", response);
                $(".random-users").css("display", "none");
                $(".selected-user").css("display", "block");
                $(".selected-user").attr("data-selected-id", response.userid)
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
        chatUserId = $(this).data("user-id");
        // var interestPic = $(this).data("interest-pic");

        console.log("Open chat User ID:", chatUserId);
        // console.log("Interest Pic:", interestPic);

        var senderInfo = "?senderId=" + chatUserId;

        window.location.href = senderInfo;

        $.ajax({
            type: "POST",
            url: "/matches",
            data: { action: "display-conversation", selectedUser: chatUserId },
            success: function(response) {
                console.log("success");

                response.message.forEach(function(m) {
                    console.log(m);
                })
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


