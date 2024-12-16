const updateRate = 2_000;


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
     * @param {number} timestamp - The timestamp of the message. Provided epoch will be formatted.
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
        this.timestamp = formatEpochTime(timestamp);
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

// NOTE: newest messages will appear at the top. fix later if desired
// Need to add bold tags depending on message type
function createMessage(messageObj) {
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


// TODO: handle errors
let firstLoad = true;
function updateNewMessages(oldest_message_id = 0) {
    // If its the first load, request messages with no filter to get the newest messages.
    // Otherwise, send a request for messages with an ID greater than the newest message ID.


    const processMessages = (messages) => {
        for (const message of messages) {
            createMessage(new Message(
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
updateNewMessages();
setInterval(updateNewMessages, updateRate);


function updateInfoBubbles() {
    const messagesLoggedBubble = document.getElementById("message-count");
    const daysElapsedBubble = document.getElementById("days-elapsed");
    const worldWeatherBubble = document.getElementById("world-weather");

    const worldTimeBubble = document.getElementById("world-time");  // Either remove, or add code to interpolate time between updates

    fetch("/api/chat_misc")
        .then(response => response.json())
        .then(data => {
            messagesLoggedBubble.innerHTML = data.messages_logged.toLocaleString();
            daysElapsedBubble.innerHTML = data.days_elapsed.toLocaleString();
            worldWeatherBubble.innerHTML = data.world_weather;

            // https://minecraft.wiki/w/Daylight_cycle
            // Replace real time with time according to the Minecraft day cycle. This prevents
            // sporadic time updates.
            worldTimeBubble.innerHTML = data.world_time;
        });
}
updateInfoBubbles();
setInterval(updateInfoBubbles, updateRate);



// status
// createMessage(new Message(
//     1, 
//     "SERVER", 
//     "null", 
//     "TEAW has started!",
//     Date.now(),
//     "status"
// ));

// // join
// createMessage(new Message(
//     2, 
//     "SERVER", 
//     "5663c72f-18c5-4012-b28c-78784c2ca736", 
//     "SaxboyLaFranks joined the game",  
//     1734180577000, 
//     "join"
// ));

// // chat
// createMessage(new Message(
//     3, 
//     "SaxboyLaFranks", 
//     "6c7ab286-3ea3-42b4-af47-55376c963d92", 
//     "it was for morale boost!",  
//     1734194977000, 
//     "chat"
// ));

// // discord
// createMessage(new Message(
//     4, 
//     "besser", 
//     "232014294303113216", 
//     "something fruity. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. This message is very long, and wraps. ",  
//     1734195037000, 
//     "discord"
// ));

// // advancement
// createMessage(new Message(
//     5, 
//     "SERVER", 
//     "5663c72f-18c5-4012-b28c-78784c2ca736", 
//     "SaxboyLaFranks has made the advancement [Monster Hunter]",
//     1734138565720,
//     "advancement"
// ));

// // death
// createMessage(new Message(
//     6, 
//     "SERVER", 
//     "5663c72f-18c5-4012-b28c-78784c2ca736", 
//     "SaxboyLaFranks was slain by Zombie",
//     1734138565720,
//     "death"
// ));

// // quit
// createMessage(new Message(
//     7, 
//     "SERVER", 
//     "5663c72f-18c5-4012-b28c-78784c2ca736", 
//     "SaxboyLaFranks left the game",
//     1734138565720,
//     "quit"
// ));

// // tests
// createMessage(new Message(
//     8, 
//     "SaxboyLaFranks", 
//     "6c7ab286-3ea3-42b4-af47-55376c963d92", 
//     "HTML injection test <b>bold</b> <i>italic</i> <a href='https://google.com'>link</a> <img src='https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png'>",  
//     1734194977000, 
//     "chat"
// ));

// createMessage(new Message(
//     9, 
//     "SaxboyLaFranks", 
//     "6c7ab286-3ea3-42b4-af47-55376c963d92", 
//     "emoji rendering test \ud83d\ude14",  
//     1734194977000, 
//     "chat"
// ));

// createMessage(new Message(
//     10, 
//     "SaxboyLaFranks", 
//     "6c7ab286-3ea3-42b4-af47-55376c963d92", 
//     "control char rendering test \"real\" \"fake\"",  
//     1734194977000, 
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