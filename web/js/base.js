// Highlight the current page in navbar
const currentPath = window.location.pathname;
switch (currentPath) {
    case "/players":
        const playersLink = document.getElementById("players-link");
        playersLink.classList.add("active");
        break;
    case "/chat":
        const chatLink = document.getElementById("chat-link");
        chatLink.classList.add("active");
        break;
    case "/towns":
        const townsLink = document.getElementById("towns-link");
        townsLink.classList.add("active");
        break;
    case "/map":
        const mapLink = document.getElementById("map-link");
        mapLink.classList.add("active");
        break;
    case "/showcase":
        const showcaseLink = document.getElementById("showcase-link");
        showcaseLink.classList.add("active");
        break;
}



function chooseAlternateImage() {
    const randomNumber = Math.floor(Math.random() * 100);
    if (randomNumber === 1) {
        document.getElementById("nav-img").src = "/imgs/coconut.webp";
    }
}
chooseAlternateImage();



let failureCount = 0;
let lastSuccessfulUpdate = Date.now();
function updateStatus() {
    fetch("/api/status")
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const currentTime = Date.now();

            const onlineCount = document.getElementById("online-count");
            const statusLight = document.getElementById("nav-status-light");

            if (data.status === "ok") {
                statusLight.dataset.state = "green";
                onlineCount.textContent = `${data.online_players} player${data.online_players === 1 ? '' : 's'} online`;

                lastSuccessfulUpdate = currentTime;
                failureCount = 0;
            } else {
                statusLight.dataset.state = "red";

                const minutesSinceUpdate = Math.floor((Date.now() - lastSuccessfulUpdate) / 60000);
                onlineCount.textContent = `Last update ${minutesSinceUpdate}m ago`;
            }
        })
        .catch(error => {
            failureCount += 1;

            const statusLight = document.getElementById("nav-status-light");
            // Sometimes the browser puts the tab to sleep or the network is unstable, so we give it a few chances
            if (failureCount > 5) {
                statusLight.dataset.state = "red";
                
                const onlineCount = document.getElementById("online-count");
                const minutesSinceUpdate = Math.floor((Date.now() - lastSuccessfulUpdate) / 60000);
                onlineCount.textContent = `Offline for ${minutesSinceUpdate}m`;
            }
        });
}
updateStatus();
setInterval(updateStatus, 2000);
