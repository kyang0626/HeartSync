
// show edit
function toggleEditProfile() {
    var editProfile = document.getElementById("edit-profile");
    if (editProfile.style.display === 'none') {
        editProfile.style.display = "block";

    } else {
        editProfile.style.display = "none";
        console.log(editProfile.style);
    }
}

// Load Google API client library and intitialize
// gapi.load('client:auth2', function() {
//     gapi.client.init({
//         apiKey: 'AIzaSyAD6xEDqaLQoWe9fKEjXp1H5awAylBlm6w',
//         clientId: '314699075676-2ph28e4q452v7q74hd4dcq7t4i4biri9.apps.googleusercontent.com',
//         discoveryDocs: ["https://www.googleapis.com/discovery/v1/apis/drive/v3/rest"],
//         scope: 'https://www.googleapis.com/auth/drive.file',
//         redirect_uri: 'http://127.0.0.1:5000/profile'
//     }).then(function() {

//         console.log("google API intialized!");
        
//     });

// });

// $("#uploadForm").on("submit", function(event) {
//     event.preventDefault();

//     // Replace with your actual file input element
//     var fileInput = $("#profilePhoto").prop("files")[0];
  
//     // Check if the user is already signed in
//     if (!gapi.auth2.getAuthInstance().isSignedIn.get()) {
//         // If not signed in, initiate the sign-in process
//         gapi.auth2.getAuthInstance().signIn().then(function() {
//             // Once signed in, proceed with the file upload
//             uploadFile(fileInput);
//         });
//     } else {
//         // If already signed in, proceed with the file upload
//         uploadFile(fileInput);
//     }

// });
    
  
// function uploadFile(fileInput) {
//     // Get the authenticated user's access token
//     var accessToken = gapi.auth2.getAuthInstance().currentUser.get().getAuthResponse().access_token;

//     // Define the API endpoint and parameters
//     var apiUrl = 'https://www.googleapis.com/upload/drive/v3/files';
//     var uploadType = 'media';

//     // Create headers with Authorization and Content-Type
//     var headers = {
//         'Authorization': 'Bearer ' + accessToken,
//         'Content-Type': fileInput.type || 'application/octet-stream'
//     };

//     // Create a FormData object to send the file
//     var formData = new FormData();
//     formData.append('file', fileInput);

//     // Make the POST request using Fetch API
//     fetch(`${apiUrl}?uploadType=${uploadType}`, {
//         method: 'POST',
//         headers: headers,
//         body: formData
//     })
//     .then(response => {
//         if (response.ok) {
//             return response.json();
//         } else {
//             throw new Error(`Failed to upload file. Status code: ${response.status}`);
//         }
//     })
//     .then(data => {
//         console.log('File uploaded successfully:', data);
//     })
//     .catch(error => {
//         console.error(error.message);
//     });
// }

$(document).ready(function() {

    $("#updateProfile").on("click", function() {

        var bio = $("#bio").val();
        var name = $("#name").val();
        var age = $("#age").val();
        var city = $("#city").val();
        var state = $("#state").val();
        var school = $("#school").val();
        var company = $("#company").val();
        var gender = $("#gender").val();
        var sex = $("#sexuality").val();

        console.log(bio, name, age, city, state, school, company, gender, sex);

        $.ajax({
            type: "POST",
            url: "/update_profile",
            data: {bioVal: bio, nameVal: name, ageVal: age, cityVal: city, stateVal: state, schoolVal: school, companyVal: company, genderVal: gender, sexVal: sex},
            success: function(response) {
                location.reload();
                console.log("Successfully updated profile", response);
            },
            error: function(error) {
                console.log("Error in updating profile");
            }
        })
    })
})