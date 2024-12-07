// Highlight the current page in navbar
const currentPath = window.location.pathname;
switch (currentPath) {
    case "/":
        const homeLink = document.getElementById("home-link");
        homeLink.classList.add("active");
        break;
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
    case "/wars":
        const warsLink = document.getElementById("wars-link");
        warsLink.classList.add("active");
        break;
    case "/showcase":
        const showcaseLink = document.getElementById("showcase-link");
        showcaseLink.classList.add("active");
        break;
}


