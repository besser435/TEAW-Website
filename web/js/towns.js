/* 
Please for the love of god update this at some point to just update the data
on the cards, not destroy and recreate them like the USAI page. 
Recreating each card on each update caused so many problems.

Create the cards on page load. Add new cards if present. 
Then update each card with the new data.

There should be a function that only creates cards. It will be called
on page load and when a new town is seen.

Then just update the data on the cards.

*/

// --- HELPER FUNCTIONS --- 
let currentSortMethod = "a-z-grouped";
let currentSearchTerm = "";


function sortTowns(towns) {
    switch (currentSortMethod) {
        case "a-z-grouped":
            return towns;

        case "active-a-z":
            const active = towns.filter(town => town.is_active).sort((a, b) => a.name.localeCompare(b.name));
            const inactive = towns.filter(town => !town.is_active).sort((a, b) => a.name.localeCompare(b.name));
            return [...active, ...inactive];

        case "old-new":
            return towns.slice().sort((a, b) => a.founded - b.founded);

        default:
            console.warn("Unknown sort method: ", currentSortMethod);
            return towns;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const sortSelect = document.getElementById('sort-select');
    
    sortSelect.addEventListener('change', (e) => {
        currentSortMethod = e.target.value;
        updateTowns();    // bad, but it works.
    });
});



// --- OBJECTS --- 
class Town {
    constructor(
        uuid, name, town_color, 
        nation_name, nation_color, spawn_x, spawn_z, spawn_y, 
        mayor, founded, 
        is_active
    ) {
        this.uuid = uuid;
        this.name = (name.replace(/_/g, " "));
        this.town_color = town_color;
        this.nation_name = (nation_name.replace(/_/g, " ")) || null;
        this.nation_color = nation_color || null;
        this.spawn_x = spawn_x;
        this.spawn_z = spawn_z;
        this.spawn_y = spawn_y;
        this.mayor = mayor;
        this.founded = Number(founded);
        this.formatted_founded = new Date(this.founded).toLocaleDateString();
        this.is_active = Boolean(is_active);
    }
}

function onLoadAddFakeCards() {   // Takes a while to populate the cards, so add some placeholders on page load
    const containerGrid = document.querySelector(".container-grid");

    // Card container
    const fakeCard = document.createElement("div");
    fakeCard.className = "card-container";

    // Color pill
    const colorPill = document.createElement("div");
    colorPill.className = "color-pill";
    colorPill.style.backgroundColor = "rgb(69, 69, 69)";
    colorPill.style.borderColor = "rgb(46, 46, 46)";
    fakeCard.appendChild(colorPill);

    // Status light
    const statusLight = document.createElement("div");
    statusLight.className = "status-light";
    statusLight.setAttribute("data-state", "off");
    fakeCard.appendChild(statusLight);

    for (let i = 0; i < 50; i++) {
        containerGrid.appendChild(fakeCard.cloneNode(true));
    }
}
onLoadAddFakeCards();

function addTownCard(townObj) {
    // Main card
    const card = document.createElement("div");
    card.className = "card-container";
    card.id = townObj.uuid;

    // Color pill
    const colorPill = document.createElement("div");
    colorPill.className = "color-pill";

    const formatColor = (hexColor) => {
        const r = parseInt(hexColor.slice(0, 2), 16);
        const g = parseInt(hexColor.slice(2, 4), 16);
        const b = parseInt(hexColor.slice(4, 6), 16);
        
        // Darken
        const darkenAmount = 0.9;
        const darkened = {
            r: Math.floor(r * darkenAmount),
            g: Math.floor(g * darkenAmount),
            b: Math.floor(b * darkenAmount)
        };
        
        // Opacity
        return `rgba(${darkened.r}, ${darkened.g}, ${darkened.b}, 0.7)`;
    };

    colorPill.style.backgroundColor = formatColor(townObj.town_color);
    colorPill.style.borderColor = townObj.nation_color ? 
        formatColor(townObj.nation_color) : 
        formatColor(townObj.town_color);
    card.appendChild(colorPill);

    // Town details
    const townDetails = document.createElement("div");
    townDetails.className = "card-details";

    // Town name
    const name = document.createElement("h2");
    name.textContent = townObj.name;
    name.className = "town-name";
    townDetails.appendChild(name);

    // Nation name
    const nationName = document.createElement("p");
    const nationLabel = document.createElement("b");
    nationLabel.textContent = "Nation: ";
    nationName.className = "nation-name";
    nationName.appendChild(nationLabel);
    nationName.appendChild(document.createTextNode(townObj.nation_name));
    townObj.nation_name ? townDetails.appendChild(nationName) : null;

    // Mayor name
    const mayorName = document.createElement("p");
    const mayorLabel = document.createElement("b");
    mayorLabel.textContent = "Mayor: ";
    mayorName.className = "mayor-name";
    mayorName.appendChild(mayorLabel);
    mayorName.appendChild(document.createTextNode(townObj.mayor));
    townObj.mayor ? townDetails.appendChild(mayorName) : null;

    // Founding date
    const foundingDate = document.createElement("p");
    const foundingDateLabel = document.createElement("b");
    foundingDateLabel.textContent = "Founded: ";
    foundingDate.className = "founding-date";
    foundingDate.appendChild(foundingDateLabel);
    foundingDate.appendChild(document.createTextNode(townObj.formatted_founded));
    townObj.formatted_founded ? townDetails.appendChild(foundingDate) : null;

    // Status light
    const statusLight = document.createElement("div");
    statusLight.className = "status-light";
    switch (townObj.is_active) {
        case true:
            statusLight.setAttribute("data-state", "green");
            break;
        case false:
            statusLight.setAttribute("data-state", "off");
            break;
    }

    // Bluemap link
    // See this message in the Bluemap Discord for docs:
    // https://discord.com/channels/665868367416131594/1155554866077376653/1155555842511360091
    const distance = 400;
    card.addEventListener("click", () => {
        window.open(
            `https://map.toendallwars.org/#teaw_v4:${townObj.spawn_x}:${townObj.spawn_y}:${townObj.spawn_z}:` +
            `${distance}:0:0:0:0:perspective`, 
            "_blank"
        );
    });


    card.appendChild(townDetails);
    card.appendChild(statusLight);

    return card;
}



// --- TOWN UPDATES --- 
const updateRate = 30_000;

async function getTowns() {
    const towns = [];
    try {
        const response = await fetch("/api/towns");
        const data = await response.json();

        data.forEach(town => {
            const townObj = new Town(
                town.uuid, town.name, town.town_color, town.nation_name,
                town.nation_color, town.spawn_x, town.spawn_z, town.spawn_y, town.mayor, town.founded,
                town.is_active
            );
            towns.push(townObj);
        });

    } catch (error) {
        console.error("Failed to fetch towns:", error);
    }
    return towns;
}

async function updateTowns() {
    const towns = await getTowns();

    // Prevent clearing the grid if the call fails
    if (towns.length === 0) {
        return;
    }

    // Removes the old stuff, while keeping the "No towns found" message
    const containerGrid = document.querySelector(".container-grid");
    containerGrid.querySelectorAll(".card-container").forEach(el => el.remove());

    const sortedTowns = sortTowns(towns);

    sortedTowns.forEach(town => {
        const card = addTownCard(town);

        // If there's an active search, only show matching towns
        if (currentSearchTerm !== "") {
            const townName = town.name.toLowerCase();

            if (!townName.includes(currentSearchTerm.toLowerCase())) {
                card.style.display = "none";
            } else {
                highlightText(card.querySelector(".town-name"), currentSearchTerm);
            }
        }
        containerGrid.appendChild(card);
    });
}
updateTowns();
setInterval(updateTowns, updateRate);



// --- MISC. UPDATES ---
function updateInfoBubbles() {
    const activeTownsBubble = document.getElementById("active-towns");
    const totalTownsBubble = document.getElementById("total-towns");

    const activeNationsBubble = document.getElementById("active-nations");
    const totalNationsBubble = document.getElementById("total-nations");

    const totalMoneyBubble = document.getElementById("total-money");    // Includes towns and nations

    fetch("/api/towns_misc")
        .then(response => response.json())
        .then(data => {
            activeTownsBubble.innerHTML = data.active_towns.toLocaleString();
            totalTownsBubble.innerHTML = data.total_towns.toLocaleString();

            activeNationsBubble.innerHTML = data.active_nations.toLocaleString();
            totalNationsBubble.innerHTML = data.total_nations.toLocaleString();

            totalMoneyBubble.innerHTML = `$${data.total_money.toLocaleString()}`;
        });
}
updateInfoBubbles();
setInterval(updateInfoBubbles, updateRate);



// TODO: add the ability to search nations and mayors
// --- SEARCH ---
function setupSearch() {
    const searchInput = document.getElementById("town-search");
    const noTownsFound = document.getElementById("no-towns-found");

    searchInput.addEventListener("input", () => {
        const searchTerm = searchInput.value.toLowerCase();
        const towns = document.querySelectorAll(".card-container");

        let found = false;

        towns.forEach((town) => {
            const townName = town.querySelector(".town-name");
            const townNameLower = townName.textContent.toLowerCase();

            if (!searchTerm) {
                // Clear highlights when search is empty
                townName.textContent = townName.textContent;
                town.style.display = "flex";
                found = true;
            } else if (townNameLower.includes(searchTerm)) {
                highlightText(townName, searchTerm);
                town.style.display = "flex";
                found = true;
            } else {
                town.style.display = "none";
            }
        });
        currentSearchTerm = searchTerm;

        noTownsFound.style.display = found ? "none" : "block";
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

