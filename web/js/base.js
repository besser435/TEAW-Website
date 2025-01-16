// Highlight the current page in navbar
window.addEventListener("load", () => {
    const currentPath = window.location.pathname;
    switch (currentPath) {  // TODO: redo, kind of long
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
        case "/stats":
            const statsLink = document.getElementById("stats-link");
            statsLink.classList.add("active");
            break;
        case "/map":
            const mapLink = document.getElementById("map-link");
            mapLink.classList.add("active");
            break;
        case "/showcase":
            const showcaseLink = document.getElementById("showcase-link");
            showcaseLink.classList.add("active");
            break;
        case "/showcase/submit":
            const showcaseSubmitLink = document.getElementById("showcase-link");
            showcaseSubmitLink.classList.add("active");
            break;
    }
});

// cleaned version of the above code. However, the above code doesnt work. Get that working before using this.
// It broke after we added the hamburger nav
// const currentPath = window.location.pathname;
// const pageMappings = {
//     '/players': 'players-link',
//     '/chat': 'chat-link', 
//     '/towns': 'towns-link',
//     '/stats': 'stats-link',
//     '/map': 'map-link',
//     '/showcase': 'showcase-link',
//     '/showcase/submit': 'showcase-link'
// };

// const linkId = pageMappings[currentPath];
// if (linkId) {
//     document.getElementById(linkId).classList.add('active');
// }



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
                // Update the status
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
                const minutesSinceUpdate = Math.floor((Date.now() - lastSuccessfulUpdate) / 60000);
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
    let x = document.getElementById("navbar");
    if (x.className === "navbar") {
        x.className += " nav-open";
    } else {
        x.className = "navbar";
    }
}

// Is the above breaking the highlight current page code?
// I tried this, but its still broken.
// function hamburgerNav() {
//     const navbar = document.getElementById("navbar");
//     navbar.classList.toggle("nav-open");
// }
