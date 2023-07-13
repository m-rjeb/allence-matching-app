var questionStates = {}; // Object to store the button states for each question

function buttonClicked(button, questionIndex) {
    if (!questionStates[questionIndex]) {
        questionStates[questionIndex] = {
            activeButton: null,
        };
    }

    var activeButton = questionStates[questionIndex].activeButton;

    if (button !== activeButton) {
        if (activeButton !== null) {
            activeButton.classList.remove("clicked");
        }
        button.classList.add("clicked");
        questionStates[questionIndex].activeButton = button;
        // Send an AJAX request to the backend
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/button-clicked", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(JSON.stringify({ value: button.value, questionIndex: questionIndex }));
    } else {
        button.classList.remove("clicked");
        questionStates[questionIndex].activeButton = null;
    }
}

function onSubmit() {
    console.log("onSubmit")
    var button = document.getElementById("resultsBtn");
    var spinnerIcon = document.getElementById("spinnerIcon");
    var buttonText = document.getElementById("buttonText");
    var xhr = new XMLHttpRequest();

    // Show the spinner icon and hide the button text
    button.disabled = true; // Disable the button to prevent multiple clicks
    spinnerIcon.style.display = "inline-block";
    buttonText.classList.add("hidden");

    // Perform your desired action here
    xhr.open("POST", "/results", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    console.log("JSON response");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            console.log("Sucessfully sent results")
        }
    };
    xhr.send();
    console.log("Sucessfully sent results 22222222")

    setTimeout(function () {
        button.disabled = false; // Enable the button again
        spinnerIcon.style.display = "none";
        buttonText.classList.remove("hidden");
        loadModal();
    }, 5000);
}

function loadModal() {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/modal", true);
    xhr.onreadystatechange = function () {
        console.log("load modal")
        if (xhr.readyState === 4 && xhr.status === 200) {
            console.log("Sucessfully sent results 33333333333333")
            document.getElementById("modalPlaceholder").innerHTML = xhr.responseText;
            const modal = new bootstrap.Modal(document.getElementById("staticBackdrop"));
            modal.show();
            console.log("Sucessfully loaded modal")
        }
    };
    xhr.send();
    console.log("Sucessfully sent results 44444444444444")
}

function redirectToLogin() {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/dismiss-modal", true);
    window.location.href = "/";
    xhr.send();
}

function loadIndexModal() {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/index-modal", true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            document.getElementById("indexModalPlacholder").innerHTML = xhr.responseText;
            const modal = new bootstrap.Modal(document.getElementById("indexModal"));
            modal.show();
        }
    };
    xhr.send();
}

function getResults() {
    var usernameInput = document.getElementById("exist-username");
    var username = usernameInput.value;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/get-index-modal-username", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            document.getElementById("resultModalPlacholder").innerHTML = xhr.responseText;
            const modal = new bootstrap.Modal(document.getElementById("indexModal2"));
            spinner();
            modal.show();
        }
    };
    xhr.send(JSON.stringify({ existUsername: username }));
}

function spinner() {
    $("#indexModal").modal("hide");
    var spinner = document.getElementById("spinner");
    var content = document.getElementById("content");
    content.style.display = "none";
    setTimeout(function () {
        spinner.style.cssText = "display: none !important";
        content.style.display = "block";
    }, 5000);
}
