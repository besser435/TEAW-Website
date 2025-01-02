/* 
Please for the love of god do not use the same architecture 
as the USAI page. Recreating each card on each update caused so many problems.

Create the cards on page load. Add new players if present. 
Then update each card with the new data.



There should be a function that only creates cards. It will be called
on page load and when a new player is seen.

Then just update the data on the cards.

*/

// --- HELPER FUNCTIONS --- 
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
        this.town_name = town_name || null;
        this.nation_name = nation_name || null;
        this.status = status;
        this.last_online = last_online;
    
        this.text_status = getStatusText(this);
        this.playerSkin = getPlayerSkinObj(this.uuid);
    }
}

function onLoadAddFakePlayers() {   // Takes a while to populate the player cards, so add some fake players on page load
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



// --- PLAYER UPDATES --- 
const updateRate = 10_000;

function addPlayerCard(playerObj) {
    // rather than creating separate function, this one should also update player cards if the card already exist.
    // Could maybe update the position of the cards in the DOM based on the API order if it differs from the current order.
    // Skip player image updates, as those are slow and not necessary. The page auto refreshes every 24hrs anyway.
    const playerGrid = document.querySelector(".player-grid");  // Main player container

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
    nationName.appendChild(nationLabel);
    nationName.appendChild(document.createTextNode(playerObj.nation_name?.replace(/_/g, " ")));
    playerObj.nation_name ? playerDetails.appendChild(nationName) : null;
    
    const townName = document.createElement("p");
    const townLabel = document.createElement("b");
    townLabel.textContent = "Town: ";
    townName.appendChild(townLabel);
    townName.appendChild(document.createTextNode(playerObj.town_name?.replace(/_/g, " ")));
    playerObj.town_name ? playerDetails.appendChild(townName) : null;
    

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
    playerGrid.appendChild(card);
}

async function initializePlayers() {
    const players = await getPlayers();

    // Prevent clearing the player grid if the call fails
    if (players.length === 0) {
        return;
    }

    const playerGrid = document.querySelector(".player-grid");
    playerGrid.innerHTML = "";

    players.forEach(player => {
        addPlayerCard(player);
    });
}
initializePlayers();
setInterval(initializePlayers, updateRate);


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
