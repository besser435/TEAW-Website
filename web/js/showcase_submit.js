document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("showcase-form");
    const fileInput = document.getElementById("photo-file");
    const okSubmissionMessage = document.getElementById("submission-message");
    const sendingMessage = document.getElementById("sending-message");

    fileInput.addEventListener("change", (event) => {
        const file = event.target.files[0];
        if (file && file.size > 10 * 1024 * 1024) {
            alert("File size must not exceed 10MB.");
            fileInput.value = "";
        }
    });

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        const formData = new FormData(form);
        const submitButton = document.getElementById("submit-button");
        submitButton.disabled = true;

        okSubmissionMessage.hidden = true;
        sendingMessage.hidden = false;

        fetch("/api/submit_photo", {
            method: "POST",
            body: formData
        })
        .then(response => {
            if (response.ok) {
                sendingMessage.hidden = true;
                okSubmissionMessage.hidden = false;

                form.reset();
            } else {
                return response.json().then(data => {
                    throw new Error(data.message || "Failed to submit your photo. Please try again later.");
                });
            }
        })
        .catch(error => {
            alert(error.message);
        })
        .finally(() => {
            submitButton.disabled = false;
        });
    });
});