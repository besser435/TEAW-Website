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
        return `${seconds} second${seconds > 1 ? 's' : ''}`;
    }
}

function getStatusText(PlayerObj) {
    if (PlayerObj.status === "online") {
        const onlineDuration = PlayerObj.online_duration;
        return `Online for ${formatDuration(onlineDuration)}`;
    } else if (PlayerObj.status === "afk") {
        const afkDuration = PlayerObj.afk_duration;
        return `AFK for ${formatDuration(afkDuration)}`;
    } else if (PlayerObj.status === "offline") {
        const lastOnline = PlayerObj.last_online;
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

// rather than creating separate function, this one should also update player cards if the card already exist
function addPlayerCard(playerObj) { // Adds a player card to the grid
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
    const name = document.createElement("h3");
    name.textContent = playerObj.name;
    playerDetails.appendChild(name);

    // Status text
    const textStatus = document.createElement("p");
    textStatus.textContent = playerObj.text_status;
    //textStatus.textContent = "Last online 2 hours ago";
    playerDetails.appendChild(textStatus);

    // Nation and town (doing it this way prevents HTML injection)
    // Probably can just clean it in the API to avoid this (is it even possible to inject HTML from Towny?)
    const nationName = document.createElement("p");
    const nationLabel = document.createElement("b");
    nationLabel.textContent = "Nation: ";
    nationName.appendChild(nationLabel);
    nationName.appendChild(document.createTextNode(playerObj.nation_name));
    playerObj.nation_name ? playerDetails.appendChild(nationName) : null;
    

    const townName = document.createElement("p");
    const townLabel = document.createElement("b");
    townLabel.textContent = "Town: ";
    townName.appendChild(townLabel);
    townName.appendChild(document.createTextNode(playerObj.town_name));
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

    card.appendChild(playerDetails);
    card.appendChild(statusLight);
    playerGrid.appendChild(card);
}

async function initializePlayers() { // Create all player cards on page load
    const players = await getPlayers();

    players.forEach(player => {
        addPlayerCard(player);
    });
}
initializePlayers();


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