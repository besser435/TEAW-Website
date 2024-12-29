document.addEventListener("DOMContentLoaded", () => {
    const showcaseGrid = document.querySelector(".showcase-grid");

    fetch("/api/showcase_manifest")
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to fetch showcase data");
            }
            return response.json();
        })
        .then(data => {
            showcaseGrid.innerHTML = "";

            data.forEach(item => {
                // Create a photo card for each item
                const photoCard = document.createElement("div");
                photoCard.className = "photo-card";

                // Image
                const photoImage = document.createElement("img");
                photoImage.src = `/api/showcase_img/${item.img_src}`;
                photoImage.alt = item.photo_title;
                photoImage.className = "photo-image";

                // Info
                const photoInfo = document.createElement("div");
                photoInfo.className = "photo-info";

                const photoTitle = document.createElement("h3");
                photoTitle.className = "photo-title";
                photoTitle.textContent = item.photo_title;

                const photoDetails = document.createElement("p");
                photoDetails.className = "photo-details";

                const formattedDate = new Date(`${item.photo_date}T00:00:00`).toLocaleDateString(undefined, {
                    month: "long",
                    day: "numeric",
                    year: "numeric"
                });

                photoDetails.innerHTML = `<span id="info-date">${formattedDate}</span> by <span id="info-photographer">${item.photographer}</span>`;


                photoInfo.appendChild(photoTitle);
                photoInfo.appendChild(photoDetails);
                photoCard.appendChild(photoImage);
                photoCard.appendChild(photoInfo);

                showcaseGrid.appendChild(photoCard);
            });
        })
        .catch(error => {
            console.error("Failed to fetch showcase data:", error);
            showcaseGrid.innerHTML = `<p class="error-message">Unable to load showcase data. Please try again later.</p>`;
        });
});
