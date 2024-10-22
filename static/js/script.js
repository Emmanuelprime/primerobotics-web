function validateForm(event) {
    event.preventDefault();

    const surname = document.getElementById('surname').value.trim();
    const firstName = document.getElementById('first_name').value.trim();
    const lastName = document.getElementById('last_name').value.trim();
    const email = document.getElementById('email').value.trim();
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    let valid = true;

    document.getElementById('error-message').innerText = "";

    if (surname === "") {
        valid = false;
        document.getElementById('error-message').innerText += "Surname must be filled out.\n";
    }

    if (firstName === "") {
        valid = false;
        document.getElementById('error-message').innerText += "First name must be filled out.\n";
    }

    if (lastName === "") {
        valid = false;
        document.getElementById('error-message').innerText += "Last name must be filled out.\n";
    }

    if (!emailPattern.test(email)) {
        valid = false;
        document.getElementById('error-message').innerText += "Please enter a valid email address.\n";
    }

    if (valid) {
        document.getElementById('registration-form').submit();
    }
}

function filterCourses() {
    const searchInput = document.getElementById('courseSearch').value.toLowerCase();
    const courseItems = document.getElementsByClassName('course-item');
    let found = false;  

    for (let i = 0; i < courseItems.length; i++) {
        const courseName = courseItems[i].getElementsByClassName('card-title')[0].innerText.toLowerCase();
        if (courseName.includes(searchInput)) {
            courseItems[i].style.display = "";
            found = true;
        } else {
            courseItems[i].style.display = "none";
        }
    }

    const noResultsMessage = document.getElementById('no-results');
    if (!found) {
        noResultsMessage.style.display = "block";
    } else {
        noResultsMessage.style.display = "none";
    }
}
