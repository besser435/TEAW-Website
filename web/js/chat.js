




// NOTE: old USAI Code. Edit/uncomment as needed
// document.addEventListener("DOMContentLoaded", function () {
//     window.onload = function () {
//         // Set the default scroll position to the bottom
//         // wait for the chat messages and CSS to load,
//         // or else the scrollHeight will be incorrect (something with CSS margins loading later)
//         const messageWindow = document.getElementById("message-window");
//         if (messageWindow) {
//             messageWindow.scrollTop = messageWindow.scrollHeight;
//         }

//         // Add a scroll event listener to the message window
//         //messageWindow.addEventListener("scroll", updateButtonVisibility);

//         // Disable auto-scroll if the user manually scrolls up and vice versa
//         const autoScrollCheckbox = document.getElementById("auto-scroll");
//         messageWindow.addEventListener("scroll", function () {
//             if (isScrolledToBottom(messageWindow)) {
//                 autoScrollCheckbox.checked = true;
//             } else {
//                 autoScrollCheckbox.checked = false;
//             }
//             updateButtonVisibility();
//         });
//     };
// });



// Should only be called for player messages. Otherwise use CSS to select the correct icon
function getPlayerProfilePicObj(sender_uuid) {
    // For if we ever add Discord sender PFPs
    // if (messageType === "discord") {
    //     const discordProfilePic = document.createElement("img");
    //     discordProfilePic.className = "profile-pic";
    //     discordProfilePic.src = "";   // Google Material Icon

    //     return discordProfilePic;

    // } else 
    const profilePic = document.createElement("img");
    profilePic.className = "profile-pic";
    profilePic.src = "/api/player_face/" + sender_uuid;

    return profilePic;
}


function formatEpochTime(epochTime) {
    //const now = Date.now();
    const now = 1734195037000;
    const diffInMs = now - epochTime;
    const diffInSeconds = Math.floor(diffInMs / 1000);

    if (diffInSeconds < 60) {
        return "Now";
    }

    const diffInMinutes = Math.floor(diffInSeconds / 60);
    if (diffInMinutes < 60) {
        return `${diffInMinutes}m`;
    }

    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) {
        return `${diffInHours}h`;
    }

    const date = new Date(epochTime);
    return date.toISOString().split("T")[0];
}


class Message {
    /**
     * @param {number} id - Auto-incremented value by the DB.
     * @param {string} sender_name - The name of the sender.
     * @param {string} sender_uuid - The UUID of the sender. May be a player or a Discord user.
     * @param {string} message - The content of the message.
     * @param {number} timestamp - The timestamp of the message. Provided epoch will be formatted.
     * @param {string} type - The type of the message.
     */
    constructor(id, sender_name, sender_uuid, message, timestamp, type) {
        /** @type {number} */
        this.id = id;
        /** @type {string} */
        this.sender_name = sender_name;
        /** @type {string} */
        this.sender_uuid = sender_uuid;
        /** @type {string} */
        this.message = message;
        /** @type {string} */
        this.timestamp = formatEpochTime(timestamp);
        /** @type {string} */
        this.type = type;

        if (this.type === "chat") {
            this.profilePicObj = getPlayerProfilePicObj(sender_uuid); 
        } else {

            // Cant use null, as a TypeError will be thrown. Just redo how 
            // we handle the PFPs. The stuff below is a placeholder
            this.profilePicObj = document.createElement("img");
            this.profilePicObj.className = "profile-pic";
            this.profilePicObj.src = "/http/501";
        }
    }
}



// NOTE: newest messages will appear at the top. fix later if desired
// Need to add bold tags depending on message type
function addMessageToChatFeed(messageObj) {
    const chatFeed = document.getElementsByClassName("chat-feed");  // Main message container


    // Create the message info div (the part before the message)
    const messageInfo = document.createElement("div");
    messageInfo.className = "message-info";

    // PFP
    const profilePic = messageObj.profilePicObj;
    messageInfo.appendChild(profilePic);

    // Add sender name, or message type
    const sender = document.createElement("div");
    sender.className = "sender";
    
    if (messageObj.type === "chat" || messageObj.type === "discord") {
        sender.innerHTML = messageObj.sender_name;
    } else {
        sender.innerHTML = messageObj.type[0].toUpperCase() + messageObj.type.slice(1);
    }

    messageInfo.appendChild(sender);

    // Add timestamp
    const timestamp = document.createElement("div");
    timestamp.className = "timestamp";
    timestamp.innerHTML = messageObj.timestamp;
    messageInfo.appendChild(timestamp);

    // Add message type CSS data class
    messageInfo.setAttribute("data-message-type", messageObj.type);


    // The actual message part
    // Message text
    const messageText = document.createElement("div");
    messageText.className = "message-text";
    messageText.innerHTML = messageObj.message;


    // Package up the message info and message text
    const messageContainer = document.createElement("div");
    messageContainer.className = "message-container";
    messageContainer.id = messageObj.id;

    messageContainer.appendChild(messageInfo);
    messageContainer.appendChild(messageText);


    // NOTE: newest messages will appear at the top. fix later if desired
    chatFeed[0].appendChild(messageContainer);
    // while debugging
    messageContainer.style.color = "white";
    chatFeed[0].appendChild(document.createElement("br"));
    //chatFeed.scrollTop = messageWindow.scrollHeight;
}


// status
addMessageToChatFeed(new Message(
    1, 
    "SERVER", 
    "null", 
    "TEAW has started!",
    1733330977000,
    "status"
));

// join
addMessageToChatFeed(new Message(
    2, 
    "SERVER", 
    "5663c72f-18c5-4012-b28c-78784c2ca736", 
    "SaxboyLaFranks joined the game",  
    1734180577000, 
    "join"
));

// chat
addMessageToChatFeed(new Message(
    3, 
    "SaxboyLaFranks", 
    "5663c72f-18c5-4012-b28c-78784c2ca736", 
    "it was for morale boost!",  
    1734194977000, 
    "chat"
));

// discord
addMessageToChatFeed(new Message(
    4, 
    "besser", 
    "232014294303113216", 
    "something fruity",  
    1734195037000, 
    "discord"
));

// advancement
addMessageToChatFeed(new Message(
    5, 
    "SERVER", 
    "5663c72f-18c5-4012-b28c-78784c2ca736", 
    "SaxboyLaFranks has made the advancement [Monster Hunter]",
    1734138565720,
    "advancement"
));

// death
addMessageToChatFeed(new Message(
    6, 
    "SERVER", 
    "5663c72f-18c5-4012-b28c-78784c2ca736", 
    "SaxboyLaFranks was slain by Zombie",
    1734138565720,
    "death"
));

// quit
addMessageToChatFeed(new Message(
    7, 
    "SERVER", 
    "5663c72f-18c5-4012-b28c-78784c2ca736", 
    "SaxboyLaFranks left the game",
    1734138565720,
    "quit"
));


// scroll test
for (let i = 8; i < 100; i++) {
    addMessageToChatFeed(new Message(
        i, 
        "SERVER", 
        "5663c72f-18c5-4012-b28c-78784c2ca736", 
        "SaxboyLaFranks left the game",
        1734138565720,
        "quit"
    ));
}