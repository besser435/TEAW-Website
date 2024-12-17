// Scroll detection listener for when the user scrolls up and wants to view older messages
// NOTE: untested. probably doesnt work given we dont set a scroll threshold.
// document.getElementById("chat-feed").addEventListener("scroll", function() {
//     const chatFeed = document.getElementById("chat-feed");
//     if (chatFeed.scrollTop === 0) {
//         const messages = document.getElementsByClassName("message-container");
//         if (messages.length > 0) {
//             const oldestMessageID = messages[0].id;
//             updateNewMessages(oldestMessageID);
//         }
//         console.log(`Scrolled to to: ${chatFeed.scrollTop}`);
//     }
// });


const updateRate = 2_000;


// Should only be called for player messages. Otherwise use CSS to select the correct icon
function getPlayerProfilePicObj(sender_uuid) {
    // For if we ever add Discord sender PFPs
    // if (messageType === "discord") {
    //     const discordProfilePic = document.createElement("img");
    //     discordProfilePic.className = "profile-pic";
    //     discordProfilePic.src = "";

    //     return discordProfilePic;

    // } else 
    const profilePic = document.createElement("img");
    profilePic.className = "profile-pic";
    profilePic.src = "/api/player_face/" + sender_uuid;

    return profilePic;
}

function messageBolder(message, messageType) {
    switch (messageType) {
        case "join":
        case "quit":
        case "death":
        case "status":
            return message.replace(/^(\w+)/, "<b>$1</b>");
        
        case "advancement":
            return message
                .replace(/^(\w+)/, "<b>$1</b>")
                .replace(/(\[.*\])/, "<b>$1</b>");
        default:
            return message;
    }
}


function formatEpochTime(epochTime) {
    const now = Date.now();
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
     * @param {string} sender - The name of the sender.
     * @param {string} sender_uuid - The UUID of the sender. May be a player or a Discord user.
     * @param {string} message - The content of the message.
     * @param {number} timestamp - The timestamp of the message.
     * @param {string} type - The type of the message.
     */
    constructor(id, sender, sender_uuid, message, timestamp, type) {
        /** @type {number} */
        this.id = id;
        /** @type {string} */
        this.sender = sender;
        /** @type {string} */
        this.sender_uuid = sender_uuid;
        /** @type {string} */
        this.message = message;
        /** @type {string} */
        this.formatted_timestamp = formatEpochTime(timestamp);
        this.epoch_timestamp = timestamp;
        /** @type {string} */
        this.type = type;

        if (this.type === "chat") {
            this.profilePicObj = getPlayerProfilePicObj(sender_uuid); 
        } else {
            this.profilePicObj = document.createElement("div");
            this.profilePicObj.className = `info-icon ${this.type}`;
            this.profilePicObj.dataset.messageType = this.type;
        }
    }
}


function addMessage(messageObj) {
    const chatFeed = document.getElementsByClassName("chat-feed");  // Main message container


    // Create the message info div (the part before the message)
    let messageInfo = document.createElement("div");
    messageInfo.className = "message-info";

    // PFP
    const profilePic = messageObj.profilePicObj;
    messageInfo.appendChild(profilePic);

    // Add sender name, or message type
    const sender = document.createElement("div");
    sender.className = "sender";
    
    if (messageObj.type === "chat" || messageObj.type === "discord") {
        sender.innerHTML = messageObj.sender;
    } else {
        sender.innerHTML = messageObj.type[0].toUpperCase() + messageObj.type.slice(1);
    }

    messageInfo.appendChild(sender);

    // Add timestamp
    let timestamp = document.createElement("div");
    timestamp.className = "timestamp";
    timestamp.innerHTML = messageObj.formatted_timestamp;
    messageInfo.appendChild(timestamp);
    timestamp.setAttribute("data-epoch-timestamp", messageObj.epoch_timestamp); // For updating timestamps later

    // Add message type CSS data class
    messageInfo.setAttribute("data-message-type", messageObj.type);

    // The actual message part
    // Message text
    const messageText = document.createElement("div");
    messageText.className = "message-text";
    //messageText.innerHTML = messageObj.message;
    messageText.innerHTML = messageBolder(messageObj.message, messageObj.type);


    // Package up the message info and message text
    const messageContainer = document.createElement("div");
    messageContainer.className = "message-container";
    messageContainer.id = messageObj.id;
    messageContainer.style.display = "flex"; // So we can hide messages on searches later

    messageContainer.appendChild(messageInfo);
    messageContainer.appendChild(messageText);



    // NOTE: newest messages will appear at the top. fix later if desired
    chatFeed[0].appendChild(messageContainer);
}


// TODO: handle errors
let firstLoad = true;
function getNewMessages(oldest_message_id = 0) {
    const processMessages = (messages) => {
        for (const message of messages) {
            addMessage(new Message(
                message.id, 
                message.sender, 
                message.sender_uuid, 
                message.message, 
                message.timestamp, 
                message.type
            ));
        }
    };

    if (firstLoad) {    // First load, get all messages (200 newest messages)
        fetch("/api/chat_messages")
            .then(response => response.json())
            .then(data => {
                processMessages(data);
                firstLoad = false;

            });
    } else if (oldest_message_id !== 0) {   // The user is scrolling and wants older messages (200 messages older than the current oldest message)
        fetch(`/api/chat_messages?oldest_message_id=${oldest_message_id}`)
            .then(response => response.json())
            .then(data => {
                processMessages(data);
            });
    } else {    // Standard update, get messages newer than the newest message  (limit to 200 messages)
        const messages = document.getElementsByClassName("message-container");
        const newestMessageID = messages[messages.length - 1]?.id;

        fetch(`/api/chat_messages?newest_message_id=${newestMessageID}`)
            .then(response => response.json())
            .then(data => {
                processMessages(data);
            });
    }
}
getNewMessages();
setInterval(getNewMessages, updateRate);


function updateMessageTimestamps() {
    // Once messages are added, their timestamps are not magically updated.
    // This fixes that.

    const formatted_timestamps = document.getElementsByClassName("timestamp");
    for (const timestamp of formatted_timestamps) {
        const epoch_timestamp = parseInt(timestamp.getAttribute("data-epoch-timestamp"));
        timestamp.innerHTML = formatEpochTime(epoch_timestamp);
    }
}
setInterval(updateMessageTimestamps, 30_000);


function updateInfoBubbles() {
    const messagesLoggedBubble = document.getElementById("message-count");
    const daysElapsedBubble = document.getElementById("days-elapsed");
    const worldWeatherBubble = document.getElementById("world-weather");
    const worldTimeBubble = document.getElementById("world-time");

    fetch("/api/chat_misc")
        .then(response => response.json())
        .then(data => {
            messagesLoggedBubble.innerHTML = data.messages_logged.toLocaleString();
            daysElapsedBubble.innerHTML = data.days_elapsed.toLocaleString();
            worldWeatherBubble.innerHTML = data.world_weather;

            // We use stages rather than the real time, as the time is only updated every few seconds,
            // and would look funny if it was constantly changing by large amounts.
            const hour = parseInt(data.world_time.split(":")[0]);
            let timeStage;

            // Stages according to: https://minecraft.wiki/w/Daylight_cycle#24-hour_Minecraft_day
            if (hour >= 6 && hour < 12) {
                timeStage = "Day";
            } else if (hour >= 12 && hour < 18) {
                timeStage = "Noon";
            } else if (hour >= 18 && hour < 19) {
                timeStage = "Sunset";
            } else if (hour >= 19 || hour < 5) {
                timeStage = "Night";
            } else if (hour >= 0 && hour < 5) {
                timeStage = "Midnight";
            } else if (hour >= 5 && hour < 6) {
                timeStage = "Sunrise";
            } else {
                timeStage = "Unknown";
            }

            worldTimeBubble.innerHTML = timeStage;
        });
}
updateInfoBubbles();
setInterval(updateInfoBubbles, updateRate);


// Style stuff
function setMessageInfoHeight() {
    const messageContainers = document.querySelectorAll(".message-container");

    messageContainers.forEach(container => {
        const messageInfo = container.querySelector(".message-info");
        if (messageInfo) {
            messageInfo.style.height = "auto";

            const containerHeight = container.offsetHeight;

            messageInfo.style.height = `${containerHeight}px`;
        }
    });
}
window.addEventListener("load", setMessageInfoHeight);
window.addEventListener("resize", setMessageInfoHeight);


// status
// addMessage(new Message(
//     1, 
//     "SERVER", 
//     "null", 
//     "TEAW has started!",
//     Date.now(),
//     "status"
// ));

// // join
// addMessage(new Message(
//     2, 
//     "SERVER", 
//     "5663c72f-18c5-4012-b28c-78784c2ca736", 
//     "SaxboyLaFranks joined the game",  
//     1734180577000, 
//     "join"
// ));

// // chat
// addMessage(new Message(
//     3, 
//     "SaxboyLaFranks", 
//     "6c7ab286-3ea3-42b4-af47-55376c963d92", 
//     "it was for morale boost!",  
//     1734194977000, 
//     "chat"
// ));

// // discord
// addMessage(new Message(
//     4, 
//     "besser", 
//     "232014294303113216", 
//     "something fruity. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. ",  
//     1734195037000, 
//     "discord"
// ));

// // advancement
// addMessage(new Message(
//     5, 
//     "SERVER", 
//     "5663c72f-18c5-4012-b28c-78784c2ca736", 
//     "SaxboyLaFranks has made the advancement [Monster Hunter]",
//     1734138565720,
//     "advancement"
// ));

// // death
// addMessage(new Message(
//     6, 
//     "SERVER", 
//     "5663c72f-18c5-4012-b28c-78784c2ca736", 
//     "SaxboyLaFranks was slain by Zombie",
//     1734138565720,
//     "death"
// ));

// // quit
// addMessage(new Message(
//     7, 
//     "SERVER", 
//     "5663c72f-18c5-4012-b28c-78784c2ca736", 
//     "SaxboyLaFranks left the game",
//     1734138565720,
//     "quit"
// ));

// tests
// addMessage(new Message(
//     8, 
//     "SaxboyLaFranks", 
//     "6c7ab286-3ea3-42b4-af47-55376c963d92", 
//     "HTML injection test <b>bold</b> <i>italic</i> <a href='https://google.com'>link</a> <img src='https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png'>",  
//     1734194977000, 
//     "chat"
// ));

// addMessage(new Message(
//     9, 
//     "SaxboyLaFranks", 
//     "6c7ab286-3ea3-42b4-af47-55376c963d92", 
//     "emoji rendering test \ud83d\ude14",  
//     1734194977000, 
//     "chat"
// ));

// addMessage(new Message(
//     10, 
//     "SaxboyLaFranks", 
//     "6c7ab286-3ea3-42b4-af47-55376c963d92", 
//     "control char rendering test \"real\" \"fake\"",  
//     Date.now() - 58_000, 
//     "chat"
// ));

// // scroll test
// for (let i = 8; i < 100; i++) {
//     addMessageToChatFeed(new Message(
//         i, 
//         "SERVER", 
//         "5663c72f-18c5-4012-b28c-78784c2ca736", 
//         "SaxboyLaFranks left the game",
//         1734138565720,
//         "quit"
//     ));
// }