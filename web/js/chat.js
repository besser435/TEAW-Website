// --- SEARCH ---
let currentSearchTerm = "";
function setupSearch() {
    const searchInput = document.getElementById("chat-search");
    const noMessagesFound = document.getElementById("no-messages-found");

    searchInput.addEventListener("input", () => {
        const searchTerm = searchInput.value.toLowerCase();
        const messages = document.querySelectorAll(".message-container");

        let found = false;

        messages.forEach((message) => {
            const sender = message.querySelector(".sender");
            const messageText = message.querySelector(".message-text");

            // If search is empty, restore original text without the highlight spans
            if (!searchTerm) {
                // Just setting the text content will remove all HTML tags
                sender.textContent = sender.textContent;
                messageText.textContent = messageText.textContent;
                message.style.display = "flex";
                found = true;
            } else if (sender.textContent.toLowerCase().includes(searchTerm) || 
                       messageText.textContent.toLowerCase().includes(searchTerm)) {

                message.style.display = "flex";
                found = true;

                highlightText(sender, searchTerm);
                highlightText(messageText, searchTerm);
            } else {
                message.style.display = "none";
            }
        });
        currentSearchTerm = searchTerm;

        noMessagesFound.style.display = found ? "none" : "block";

        scrollToBottom();
    });
}
window.addEventListener("load", setupSearch);

function highlightText(element, searchTerm) {
    const originalText = element.textContent;
    const regex = new RegExp(`(${searchTerm})`, "gi");
    const highlightedHTML = originalText.replace(regex, '<span class="highlight">$1</span>');

    element.innerHTML = highlightedHTML;
}



// --- SCROLLING ---
let autoScrollEnabled = true;
function scrollToBottom() {
    const chatFeed = document.querySelector(".chat-feed");
    chatFeed.scrollTop = chatFeed.scrollHeight;
}

function handleScroll() {
    const chatFeed = document.querySelector(".chat-feed");
    const scrollToBottomButton = document.getElementById("scroll-to-bottom");

    if (!chatFeed) return;

    const isAtBottom = Math.abs(chatFeed.scrollHeight - chatFeed.scrollTop - chatFeed.clientHeight) < 5;

    if (isAtBottom) {
        autoScrollEnabled = true;
        if (scrollToBottomButton) {
            scrollToBottomButton.style.display = "none";
        }
    } else {
        autoScrollEnabled = false;
        if (scrollToBottomButton) {
            scrollToBottomButton.style.display = "block";
        }
    }
}

function setupScrollBehavior() {
    const chatFeed = document.querySelector(".chat-feed");

    if (chatFeed) {
        chatFeed.addEventListener("scroll", handleScroll);
    }
}

window.addEventListener("load", () => {
    setupScrollBehavior();
});



// --- MESSAGE HELPERS ---
const updateRate = 3_000;

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
        }
        else if (this.type === "discord") {
            this.profilePicObj = document.createElement("img");
            this.profilePicObj.className = "profile-pic";
            this.profilePicObj.src = "/imgs/discord_mark.svg";

        } else {
            this.profilePicObj = document.createElement("span");
            this.profilePicObj.className = "material-symbols-rounded";
        
            switch (this.type) {
                case "join":
                    this.profilePicObj.innerHTML = "login";
                    break;
                case "quit":
                    this.profilePicObj.innerHTML = "logout";
                    break;
                case "advancement":
                    this.profilePicObj.innerHTML = "trophy";
                    break;
                case "death":
                    this.profilePicObj.innerHTML = "skull";
                    break;
                case "status":
                    this.profilePicObj.innerHTML = "dns";
                    break;
            }
        }
    }
}

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

function onLoadAddFakeMessages() {   // Takes a while to populate the cards, so add some placeholders on page load
    const messageFeed = document.querySelector(".chat-feed");

    // Message container
    const fakeMessage = document.createElement("div");
    fakeMessage.style.display = "flex";
    fakeMessage.className = "message-container";

    // Info container
    const fakeMessageInfo = document.createElement("div");
    fakeMessageInfo.className = "message-info";
    fakeMessageInfo.setAttribute("data-message-type", "chat");
    fakeMessage.appendChild(fakeMessageInfo);

    // Sender
    const fakeSender = document.createElement("div");
    fakeSender.className = "sender";
    fakeSender.innerHTML = "⠀⠀⠀⠀⠀⠀";
    fakeMessageInfo.appendChild(fakeSender);

    // PFP
    const fakeProfilePic = document.createElement("img");
    fakeProfilePic.className = "profile-pic";

    fakeProfilePic.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'%3E%3Crect width='20' height='20' fill='grey'/%3E%3C/svg%3E";
    fakeMessageInfo.appendChild(fakeProfilePic);

    // Message text
    const fakeMessageText = document.createElement("div");
    fakeMessageText.className = "message-text";
    fakeMessageText.innerHTML = "⠀";
    fakeMessage.appendChild(fakeMessageText);


    for (let i = 0; i < 50; i++) {
        messageFeed.appendChild(fakeMessage.cloneNode(true));
    }

    scrollToBottom();
}
onLoadAddFakeMessages();



// --- MESSAGE UPDATES ---
function addMessage(messageObj) {
    const chatFeed = document.getElementsByClassName("chat-feed");  // Main message container

    // Create the message info div (the part before the message)
    let messageInfo = document.createElement("div");
    messageInfo.className = "message-info";
    messageInfo.setAttribute("data-message-type", messageObj.type);

    // Add sender name, or message type
    const sender = document.createElement("div");
    sender.className = "sender";
    
    if (messageObj.type === "chat" || messageObj.type === "discord") {
        sender.innerHTML = messageObj.sender;
    } else {
        sender.innerHTML = messageObj.type[0].toUpperCase() + messageObj.type.slice(1);
    }

    messageInfo.appendChild(sender);

    // PFP
    const profilePic = messageObj.profilePicObj;
    messageInfo.appendChild(profilePic);

    // Message text
    const messageText = document.createElement("div");
    messageText.className = "message-text";
    messageText.innerHTML = messageBolder(messageObj.message, messageObj.type);


    // Package up the message info and message text
    const messageContainer = document.createElement("div");
    messageContainer.className = "message-container";
    messageContainer.id = messageObj.id;

    if (currentSearchTerm !== "") {
        messageContainer.style.display = "none";
    } else {
        messageContainer.style.display = "flex";
    }

    messageContainer.appendChild(messageInfo);
    messageContainer.appendChild(messageText);

    // Add timestamp
    let timestamp = document.createElement("div");
    timestamp.className = "timestamp";
    timestamp.innerHTML = messageObj.formatted_timestamp;
    timestamp.title = new Date(messageObj.epoch_timestamp).toLocaleString();
    messageContainer.appendChild(timestamp);
    timestamp.setAttribute("data-epoch-timestamp", messageObj.epoch_timestamp); // For updating timestamps later

    // NOTE: if we add the ability to fetch older messages, we can't just append to the top
    chatFeed[0].appendChild(messageContainer);


    if (autoScrollEnabled) {
        scrollToBottom();
    }
}

let firstLoad = true;
function getNewMessages() {
    //function getNewMessages(oldestMessageId = 0) {
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
                // Removes the placeholder messages, while keeping the "No messages found" message
                const chatFeed = document.querySelector(".chat-feed");
                chatFeed.querySelectorAll(".message-container").forEach(el => el.remove());

                processMessages(data);
                firstLoad = false;
            });
    // TODO: Add this feature
    // } else if (oldestMessageId !== 0) {   // The user is scrolling and wants older messages (200 messages older than the current oldest message)
    //     fetch(`/api/chat_messages?oldest_message_id=${oldest_message_id}`)
    //         .then(response => response.json())
    //         .then(data => {
    //             processMessages(data);
    //         });
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
    // Could we maybe just attach an event to the timestamp divs instead?

    const formattedTimestamps = document.getElementsByClassName("timestamp");

    for (const timestamp of formattedTimestamps) {
        const epochTimestampString = timestamp.getAttribute("data-epoch-timestamp");
        const epochTimestamp = Number(epochTimestampString);
        timestamp.innerHTML = formatEpochTime(epochTimestamp);
    }
}
setInterval(updateMessageTimestamps, 30_000);



// --- MISC. UPDATES ---
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
