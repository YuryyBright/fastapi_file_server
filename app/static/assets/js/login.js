$(document).ready(function () {
  // Show/Hide Password
  $(".show-hide").click(function () {
    let passwordField = $("input[type='password']");
    if (passwordField.attr("type") === "password") {
      passwordField.attr("type", "text");
      $(this).find("span").text("Hide");
    } else {
      passwordField.attr("type", "password");
      $(this).find("span").text("Show");
    }
  });

  // Handle form submission
  $("#loginForm").submit(function (event) {
    event.preventDefault(); // Prevent form from submitting normally

    // Get email and password values
    let email = $("#email").val();
    let password = $("#password").val();

    // Basic form validation
    if (!email || !password) {
      showError("Please fill in both fields.");
      return;
    }

    // Prepare data to be sent
    let loginData = {
      email: email,
      password: password,
    };

    // Send AJAX request to backend API
    $.ajax({
      url: "/login/", // URL of your backend login endpoint
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(loginData),
      success: function (response) {
        // On success, handle the response (e.g., redirect or show message)
        if (response.token) {
          // Store the token in localStorage for future requests
          alert("Login successful!");

          // Отримуємо JWT токен з серверної змінної
          const token = response.token; // Тут токен передається через Jinja2

          // Тепер ви можете використовувати токен для запитів
          console.log("JWT Token:", token);

          // Приклад запиту з використанням токену
          fetch("/users", {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          })
            .then((response) => response.json())
            .then((data) => console.log(data))
            .catch((error) => console.error("Error:", error));
        } else {
          showError("Invalid credentials. Please try again.");
        }
      },
      error: function (xhr, status, error) {
        // Handle error response
        let errorMessage = "An error occurred. Please try again later.";

        // Handle specific backend error messages
        if (xhr.status === 400) {
          const response = JSON.parse(xhr.responseText); // Get the response body

          showError(response.detail); // Display the error message
        } else {
          showError(errorMessage); // Display the error message
        }
      },
    });
  });

  // Function to show error message
  function showError(message) {
    // Set the error message and show the error block
    $("#error-message").text(message).show();
  }
});
