// Highlight the current page in navbar
const currentPath = window.location.pathname;
const pageMappings = {
    '/players': 'players-link',
    '/chat': 'chat-link', 
    '/towns': 'towns-link',
    '/stats': 'stats-link',
    '/map': 'map-link',
    '/showcase': 'showcase-link',
    '/showcase/submit': 'showcase-link'
};

const linkId = pageMappings[currentPath];
if (linkId) {
    document.getElementById(linkId).classList.add('active');
}


// Trolling
function chooseAlternateImage() {
    const randomNumber = Math.floor(Math.random() * 100);
    if (randomNumber === 1) {
        document.getElementById("nav-img").src = "/imgs/coconut.webp";
    }
}
chooseAlternateImage();


// Status indicator
let failureCount = 0;
let lastSuccessfulUpdate = Date.now();
let lastUpdateMinsAgo;

function updateStatus() {
    fetch("/api/status")
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const onlineCount = document.getElementById("online-count");
            const statusLight = document.getElementById("nav-status-light");
            lastStatusData = data;

            if (data.status === "ok") {
                statusLight.dataset.state = "green";
                onlineCount.textContent = `${data.online_players} player${data.online_players === 1 ? '' : 's'} online`;
                failureCount = 0;
            } else {
                statusLight.dataset.state = "red";
                const offlineMinutes = Math.max(data.last_players_update_age, data.last_chat_update_age);
                lastUpdateMinsAgo = offlineMinutes
                onlineCount.textContent = `Last update ${offlineMinutes}m ago`;
            }
        })
        .catch(error => {
            failureCount += 1;

            const statusLight = document.getElementById("nav-status-light");
            // Sometimes the browser puts the tab to sleep or the network is unstable, so we give it a few chances
            if (failureCount > 5) {
                statusLight.dataset.state = "red";
                
                const onlineCount = document.getElementById("online-count");
                const minutesSinceUpdate = Math.floor((Date.now() - lastSuccessfulUpdate) / 60_000);
                onlineCount.textContent = `Offline for ${minutesSinceUpdate}m`;
            }
        });
}
updateStatus();
setInterval(updateStatus, 2000);

// Add an alert() to the status div (mainly used on mobile when there is no status text)
document.getElementById("nav-online-players").addEventListener("click", () => {
    const statusLight = document.getElementById("nav-status-light");
    
    if (statusLight.dataset.state === "red") {
        let message;
        
        if (failureCount > 5) {
            message = "Could not reach the web server. You are offline.";
        } else {
            message = `The last update was ${lastUpdateMinsAgo} minutes ago. ` +
            `This means the data on the page may be outdated. \n\n` +
            `If this persists for more than 5 minutes, contact besser.`;
        }
        
        alert(message);
    }
});


// Hamburger Nav
function hamburgerNav() {
    const navbar = document.getElementById("navbar");
    navbar.classList.toggle("nav-open");
}
