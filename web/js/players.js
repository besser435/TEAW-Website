/* 
Please for the love of god update this at some point to just update the data
on the cards, not destroy and recreate them like the USAI page. 
Recreating each card on each update caused so many problems.

Create the cards on page load. Add new players if present. 
Then update each card with the new data.

There should be a function that only creates cards. It will be called
on page load and when a new player is seen.

Then just update the data on the cards.

*/

// --- HELPER FUNCTIONS --- 
let currentSortMethod = "last_online";



let currentSearchTerm = "";



function sortPlayers(players) {
    if (currentSortMethod === "username") {
        return players.sort((a, b) => a.name.localeCompare(b.name));
    } else {
        return players.sort((a, b) => {
            if (a.status === "online" && b.status !== "online") return -1;
            if (a.status !== "online" && b.status === "online") return 1;
            
            return b.last_online - a.last_online;
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const sortSelect = document.getElementById('sort-select');
    
    sortSelect.addEventListener('change', (e) => {
        currentSortMethod = e.target.value;
        updatePlayers();    // bad, but it works.
    });
});

function getPlayerSkinObj(sender_uuid) {
    const profilePic = document.createElement("img");
    profilePic.className = "player-skin";
    profilePic.src = "/api/player_skin/" + sender_uuid;
    profilePic.alt = "Player skin";

    return profilePic;
}

function formatDuration(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) {
        return `${days} day${days > 1 ? 's' : ''}`;
    } else if (hours > 0) {
        return `${hours} hour${hours > 1 ? 's' : ''}`;
    } else if (minutes > 0) {
        return `${minutes} minute${minutes > 1 ? 's' : ''}`;
    } else {
        return `0 minutes`;
    }
}

function getStatusText(playerObj) {
    if (playerObj.name === "josamo8") {
        const lastOnline = playerObj.last_online;
        const timeNow = Date.now();
        const durationSinceLastOnline = timeNow - lastOnline;
        return `Banned ${formatDuration(durationSinceLastOnline)} ago`;
    }

    if (playerObj.status === "online") {
        const onlineDuration = playerObj.online_duration;
        return `Online for ${formatDuration(onlineDuration)}`;
    } else if (playerObj.status === "afk") {
        const afkDuration = playerObj.afk_duration;
        return `AFK for ${formatDuration(afkDuration)}`;
    } else if (playerObj.status === "offline") {
        const lastOnline = playerObj.last_online;
        const timeNow = Date.now();
        const durationSinceLastOnline = timeNow - lastOnline;
        return `Last online ${formatDuration(durationSinceLastOnline)} ago`;
    }
}



// --- OBJECTS --- 
class Player {
    constructor(
        uuid, name, 
        online_duration, afk_duration, 
        town_name, nation_name, 
        last_online, status) {
        
        this.uuid = uuid;
        this.name = name;
        this.online_duration = online_duration;
        this.afk_duration = afk_duration;
        this.town_name = (town_name.replace(/_/g, " ")) || null;
        this.nation_name = (nation_name.replace(/_/g, " ")) || null;
        this.status = status;
        this.last_online = last_online;
    
        this.text_status = getStatusText(this);
        this.playerSkin = getPlayerSkinObj(this.uuid);
    }
}

function onLoadAddFakePlayers() {   // Takes a while to populate the player cards, so add some placeholders on page load
    const playerGrid = document.querySelector(".player-grid");  // Main player container
    const fakePlayer = document.createElement("div");
    fakePlayer.className = "player-card";

    const statusLight = document.createElement("div");
    statusLight.className = "status-light";
    statusLight.setAttribute("data-state", "off");
    fakePlayer.appendChild(statusLight);

    for (let i = 0; i < 50; i++) {
        playerGrid.appendChild(fakePlayer.cloneNode(true));
    }
}
onLoadAddFakePlayers();

function addPlayerCard(playerObj) {
    // Main card
    const card = document.createElement("div");
    card.className = "player-card";
    card.id = playerObj.uuid;

    // Player skin
    card.appendChild(playerObj.playerSkin);

    const playerDetails = document.createElement("div");
    playerDetails.className = "player-details";

    // Username
    const name = document.createElement("h2");
    name.textContent = playerObj.name;
    name.className = "player-name";
    playerDetails.appendChild(name);

    // Status text
    const textStatus = document.createElement("p");
    textStatus.textContent = playerObj.text_status;
    playerDetails.appendChild(textStatus);

    // Nation and town (doing it this way prevents HTML injection)
    // Probably can just clean it in the API to avoid this (is it even possible to inject HTML from Towny?)
    const nationName = document.createElement("p");
    const nationLabel = document.createElement("b");
    nationLabel.textContent = "Nation: ";
    nationName.className = "nation-name";
    nationName.appendChild(nationLabel);
    nationName.appendChild(document.createTextNode(playerObj.nation_name));
    playerObj.nation_name ? playerDetails.appendChild(nationName) : null;   // Only add if the player is in a nation
    
    const townName = document.createElement("p");
    const townLabel = document.createElement("b");
    townLabel.textContent = "Town: ";
    townName.className = "town-name";
    townName.appendChild(townLabel);
    townName.appendChild(document.createTextNode(playerObj.town_name));
    playerObj.town_name ? playerDetails.appendChild(townName) : null;   // Only add if the player is in a town
    

    // Status light
    const statusLight = document.createElement("div");
    statusLight.className = "status-light";
    switch (playerObj.status) {
        case "online":
            statusLight.setAttribute("data-state", "green");
            break;
        case "afk":
            statusLight.setAttribute("data-state", "yellow");
            break;
        case "offline":
            statusLight.setAttribute("data-state", "off");
            break;
    }

    if (playerObj.name === "josamo8") {
        statusLight.setAttribute("data-state", "red");
        statusLight.setAttribute("data-pulse", "true");
    }

    card.appendChild(playerDetails);
    card.appendChild(statusLight);

    return card;
}



// --- PLAYER UPDATES --- 
const updateRate = 3_000;

async function getPlayers() {
    const players = [];
    try {
        const response = await fetch("/api/players");
        const data = await response.json();

        data.forEach(player => {
            const playerObj = new Player(
                player.uuid, player.name, 
                player.online_duration, player.afk_duration, 
                player.town_name, player.nation_name, 
                player.last_online, player.status
            );
            players.push(playerObj);
        });

    } catch (error) {
        console.error("Failed to fetch players:", error);
    }
    return players;
}

// async function updatePlayers() {
//     const players = await getPlayers();

//     // Prevent clearing the player grid if the call fails
//     if (players.length === 0) {
//         return;
//     }

//     // Removes the old stuff, while keeping the "No messages found" message
//     const playerGrid = document.querySelector(".player-grid");
//     playerGrid.querySelectorAll(".player-card").forEach(el => el.remove());

//     const sortedPlayers = sortPlayers(players);

//     sortedPlayers.forEach(player => {
//         const card = addPlayerCard(player);


//         // If there's an active search, only show matching players
//         if (currentSearchTerm !== "") {
//             const username = player.name.toLowerCase();

//             if (!username.includes(currentSearchTerm.toLowerCase())) {
//                 card.style.display = "none";
//             } else {
//                 highlightText(card.querySelector(".player-name"), currentSearchTerm);
//             }
//         }
//         playerGrid.appendChild(card);
//     });
// }


async function updatePlayers() {
    const players = await getPlayers();

    // Prevent clearing the player grid if the call fails
    if (players.length === 0) {
        return;
    }

    const playerGrid = document.querySelector(".player-grid");
    playerGrid.querySelectorAll(".player-card").forEach(el => el.remove());

    const sortedPlayers = sortPlayers(players);

    sortedPlayers.forEach(player => {
        const card = addPlayerCard(player);

        // If there's an active search, only show matching players
        if (currentSearchTerm !== "") {
            const searchTerm = currentSearchTerm.toLowerCase();
            const username = player.name.toLowerCase();
            const nationName = player.nation_name?.toLowerCase() || "";
            const nationNameNoLabel = nationName.split(": ")[1] || nationName;
            const townName = player.town_name?.toLowerCase() || "";
            const townNameNoLabel = townName.split(": ")[1] || townName;

            // Check if the search term matches any field
            const matchesUsername = username.includes(searchTerm);
            const matchesNation = nationNameNoLabel.includes(searchTerm);
            const matchesTown = townNameNoLabel.includes(searchTerm);

            if (matchesUsername || matchesNation || matchesTown) {
                // Highlight matching fields
                if (matchesUsername) highlightText(card.querySelector(".player-name"), searchTerm);
                if (matchesNation) highlightText(card.querySelector(".nation-name"), searchTerm);
                if (matchesTown) highlightText(card.querySelector(".town-name"), searchTerm);
            } else {
                card.style.display = "none"; // Hide if no match is found
            }
        }

        playerGrid.appendChild(card);
    });
}




updatePlayers();
setInterval(updatePlayers, updateRate);



// --- MISC. UPDATES ---
function updateInfoBubbles() {
    const activePlayersBubble = document.getElementById("active-count");
    const totalPlayersBubble = document.getElementById("total-count");
    const totalMoneyBubble = document.getElementById("total-player-money");

    fetch("/api/players_misc")
        .then(response => response.json())
        .then(data => {
            activePlayersBubble.innerHTML = data.active_players.toLocaleString();
            totalPlayersBubble.innerHTML = data.total_players.toLocaleString();
            totalMoneyBubble.innerHTML = `$${data.total_money.toLocaleString()}`;
        });
}
updateInfoBubbles();
setInterval(updateInfoBubbles, updateRate);


// --- SEARCH ---



/*
NOTE:
SPACES ARE FUCK
When searching for a space, we also get the town/nation label ex. "town: ".
When searching for a space, this is also a problem.
The message bolder also does not apply on searched and highlighted terms.

In the players object, the label and content should be different elements.

*/



// function setupSearch() {
//     const searchInput = document.getElementById("player-search");
//     const noPlayersFound = document.getElementById("no-players-found");

//     searchInput.addEventListener("input", () => {
//         const searchTerm = searchInput.value.toLowerCase();
//         const players = document.querySelectorAll(".player-card");

//         let found = false;

//         players.forEach((player) => {
//             const username = player.querySelector(".player-name").textContent.toLowerCase();

//             if (username.includes(searchTerm)) {
//                 highlightText(player.querySelector(".player-name"), searchTerm);
//                 player.style.display = "flex";
//                 found = true;
//             } else {
//                 player.style.display = "none";
//             }
            
//         });
//         currentSearchTerm = searchTerm;

//         noPlayersFound.style.display = found ? "none" : "block";
//     });
// }


function setupSearch() {
    const searchInput = document.getElementById("player-search");
    const noPlayersFound = document.getElementById("no-players-found");

    searchInput.addEventListener("input", () => {
        const searchTerm = searchInput.value.toLowerCase();
        const players = document.querySelectorAll(".player-card");

        let found = false;

        players.forEach((player) => {
            const username = player.querySelector(".player-name").textContent.toLowerCase();
            const nationName = player.querySelector(".nation-name")?.textContent.toLowerCase() || "";
            const nationNameNoLabel = nationName.split(": ")[1] || nationName;
            const townName = player.querySelector(".town-name")?.textContent.toLowerCase() || "";
            const townNameNoLabel = townName.split(": ")[1] || townName;

            console.log(nationNameNoLabel);
            console.log(townNameNoLabel);
            // Check if the search term matches any of the fields
            if (username.includes(searchTerm) || nationNameNoLabel.includes(searchTerm) || townNameNoLabel.includes(searchTerm)) {
                highlightText(player.querySelector(".player-name"), searchTerm);
                highlightText(player.querySelector(".nation-name"), searchTerm);
                highlightText(player.querySelector(".town-name"), searchTerm);
                player.style.display = "flex";
                found = true;
            } else {
                player.style.display = "none";
            }
        });
        currentSearchTerm = searchTerm;

        noPlayersFound.style.display = found ? "none" : "block";
    });
}



function highlightText(element, searchTerm) {
    if (!element) return;
    
    const originalText = element.textContent;
    const regex = new RegExp(`(${searchTerm})`, "gi");
    const highlightedHTML = originalText.replace(regex, '<span class="highlight">$1</span>');

    element.innerHTML = highlightedHTML;
}

window.addEventListener("load", setupSearch);

