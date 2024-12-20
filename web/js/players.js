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
function getPlayerSkin(sender_uuid) {
    const profilePic = document.createElement("img");
    profilePic.className = "player-skin";
    profilePic.src = "/api/player_skin/" + sender_uuid;

    return profilePic;
}

function formatEpochTime(duration) {    // Converts an epoch to a string like "1 hour" or "3 days"
    return 1; // Placeholder
}


// "AFK for 38 minutes", "Online for 2 hours", or "Last online 2 days ago"
function getStatusText(PlayerObj) {
    if (PlayerObj.status === "online") {
        return `Online for ${formatEpochTime(PlayerObj.online_duration)}`;
    } else if (PlayerObj.status === "afk") {
        return `AFK for ${formatEpochTime(PlayerObj.afk_duration)}`;
    } else if (PlayerObj.status === "offline") {
        return `Last online ${formatEpochTime(PlayerObj.last_online)} ago`;
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
        this.town_name = town_name || "none";
        this.nation_name = nation_name || "none";
        this.text_status = getStatusText(this);
        this.last_online = last_online;
        this.status = status;

        this.playerSkin = getPlayerSkin(this.uuid);
    }
}


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
    //textStatus.textContent = playerObj.text_status;
    textStatus.textContent = "Last online 2 hours ago";
    playerDetails.appendChild(textStatus);


    // Nation and town (doing it this way prevents HTML injection)
    // Probably can just clean it in the API to avoid this (is it even possible to inject HTML from Towny?)
    const nationName = document.createElement("p");
    const nationLabel = document.createElement("b");
    nationLabel.textContent = "Nation: ";
    nationName.appendChild(nationLabel);
    nationName.appendChild(document.createTextNode(playerObj.nation_name));
    
    // delete this if we want to keep the "none" text
    // conditional doesnt work for some reason
    //if (!playerObj.nation_name == "none") {
        playerDetails.appendChild(nationName);
    //}


    const townName = document.createElement("p");
    const townLabel = document.createElement("b");
    townLabel.textContent = "Town: ";
    townName.appendChild(townLabel);
    townName.appendChild(document.createTextNode(playerObj.town_name));

    //if (!playerObj.town_name == "none") {
        playerDetails.appendChild(townName);
    //}
    

    // Status light
    const statusLight = document.createElement("div");
    statusLight.className = "status-light";
    statusLight.setAttribute("data-state", "red");


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