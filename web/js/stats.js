/* TODO:
Add search functionality
*/


const updateRate = 10_000;

class StatEntry {
    constructor(rank, uuid, username, value) {
        this.rank = rank;
        this.uuid = uuid;
        this.username = username;
        this.value = value;
    }
}

async function fetchLeaderboard() {
    try {
        const stat = document.getElementById("stat-select");
        const selectedOption = stat.options[stat.selectedIndex];
        const statType = selectedOption.getAttribute("data-stat-type");

        let response;
        if (statType === "0") {
            response = await fetch(`/api/get_general_leaderboard/${stat.value}`);
        } else if (statType === "1") {
            response = await fetch(`/api/get_custom_stat/${stat.value}`);
        }

        const data = await response.json();
        
        const entries = data.leaderboard.map((entry, index) => {
            return new StatEntry(
                index + 1,
                entry.uuid,
                entry.name,
                entry.value
            );
        });

        return {
            entries: entries,
            units: data.units
        };

    } catch (error) {
        console.error(error);
        return null;
    }
}

function sortLeaderboard(data, sortMethod) {
    const entriesCopy = [...data];  // Copy to avoid bunging the original data

    // Sorted by rank rather than value, as if there are ties the ranks can be out of order,
    // which would look funny.
    switch (sortMethod) {
        case "high-to-low":
            return entriesCopy.sort((a, b) => a.rank - b.rank);
        case "low-to-high":
            return entriesCopy.sort((a, b) => b.rank - a.rank);
        case "username":
            return entriesCopy.sort((a, b) => a.username.localeCompare(b.username));
    }
}

function onLoadAddFakeStats() {    // Takes a while to populate the cards, so add some placeholders on page load
    const statsContainer = document.querySelector(".stats-container");

    for (let i = 0; i < 30; i++) {
        const entryDiv = document.createElement("div");
        entryDiv.className = "stat-entry";

        fakeProfilePic = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'%3E%3Crect width='20' height='20' fill='grey'/%3E%3C/svg%3E";
        entryDiv.innerHTML = `
            <h3 class="player-rank">⠀⠀⠀</h3>
            <img class="player-face" src="${fakeProfilePic}">
            <h3 class="player-name">⠀⠀⠀</h3>
            <h3 class="player-stat-value mono-font">⠀⠀⠀</h3>
        `;
        
        statsContainer.appendChild(entryDiv);
    }
}
onLoadAddFakeStats();

function renderLeaderboard(data, unit, currentSort) {
    // Clears the current entries, but not the search error message
    const statsContainerSelector = document.querySelector(".stats-container");
    statsContainerSelector.querySelectorAll(".stat-entry").forEach(el => el.remove());

    const unitLabel = document.getElementById("unit-label");
    unitLabel.textContent = unit.charAt(0).toUpperCase() + unit.slice(1);

    
    // Create and append new entries
    const statsContainer = document.querySelector(".stats-container");
    const sortedData = sortLeaderboard(data, currentSort);

    sortedData.forEach(entry => {
        const entryDiv = document.createElement("div");
        entryDiv.className = "stat-entry";

        entryDiv.innerHTML = `
            <h3 class="player-rank">#${entry.rank}</h3>
            <img class="player-face" src="/api/player_face/${entry.uuid}">
            <h3 class="player-name">${entry.username}</h3>
            <h3 class="player-stat-value mono-font">${entry.value.toLocaleString()}</h3>
        `;
        
        statsContainer.appendChild(entryDiv);
    });
}

async function initializeLeaderboard() {
    const statSelect = document.getElementById("stat-select");
    const sortSelect = document.getElementById("sort-select");
    //const search = document.getElementById("search");


    // Read initial values from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const statParam = urlParams.get('stat');
    const sortParam = urlParams.get('sort');

    // Set initial values from URL or defaults
    if (statParam) {
        statSelect.value = statParam;
    }

    if (sortParam && ['high-to-low', 'low-to-high', 'username'].includes(sortParam)) {
        sortSelect.value = sortParam;
    }

    let currentSort = sortSelect.value;
    //let searchQuery = "";
    let currentData = null;

    function updateUrlParams() {
        const newParams = new URLSearchParams();
        newParams.set('stat', statSelect.value);
        newParams.set('sort', currentSort);
        const newUrl = `${window.location.pathname}?${newParams.toString()}`;
        history.replaceState(null, '', newUrl);
    }

    // Initial load
    currentData = await fetchLeaderboard();
    if (currentData) {
        renderLeaderboard(currentData.entries, currentData.units, currentSort);
        updateUrlParams();
    }

    // Sort method changes
    sortSelect.addEventListener("change", () => {
        currentSort = sortSelect.value;
        if (currentData) renderLeaderboard(currentData.entries, currentData.units, currentSort);
        updateUrlParams();
    });

    // Selected stat changes
    statSelect.addEventListener("change", async () => {
        currentData = await fetchLeaderboard();
        if (currentData) {
            renderLeaderboard(currentData.entries, currentData.units, currentSort);
            updateUrlParams();
        }
    });

    // Search input
    // will add later

    // Periodic updates
    setInterval(async () => {
        currentData = await fetchLeaderboard();
        if (currentData) renderLeaderboard(currentData.entries, currentData.units, currentSort);
    }, updateRate);
}
initializeLeaderboard();
