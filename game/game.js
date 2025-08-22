// Globální proměnné pro stav hry (budou inicializovány nebo načteny)
let inventory = [];
let history = [];
let scene = "";
let choices = [];

// Data pro správu (budou prázdná na začátku, plněna přes GUI/import)
let characters = [];
let customStories = {}; // Key: action, Value: { action, response, location, characters, history_context, goal }
let locations = [];
let systemSettings = {
    tone: "extreme",
    instructions: "",
    // --- TTS Settings ---
    ttsEnabled: false,
    ttsVoiceURI: null, // Will store URI of the selected voice for persistence
    ttsPitch: 1.0,
    ttsRate: 1.0,
    // --- End TTS Settings ---
    currentPlayerCharacterIndex: -1 // New: Index of the character playing the game
};

// Web Speech API proměnné
let synth = window.speechSynthesis;
let voices = [];

// GUI State Management
let activeSection = 'system'; // Start with system section to allow setup
let characterWizard = {
    currentStep: 1,
    tempChar: { name: '', race: '', appearance: '', personality: '', sexuality: '', attributes: {}, skills: [] }, // Added 'race'
    editingIndex: -1 // -1 for new, index for editing
};
let storyWizard = {
    currentStep: 1,
    tempStory: { action: '', response: '', location: '', characters: [], history_context: [], goal: '' },
    editingKey: null // null for new, key for editing
};
let locationWizard = {
    currentStep: 1,
    tempLocation: { name: '', desc: '' },
    editingIndex: -1
};

document.addEventListener('DOMContentLoaded', () => {
    // Initial GUI setup - lists will be empty until data is added/imported
    updateCharacters();
    updateStories();
    updateLocations();
    loadSystemSettings(); // This now also loads TTS settings and currentPlayerCharacterIndex
    displayPlayerStats(); // New: Display player stats on load

    document.getElementById('scene').innerHTML = "Začněte novou hru nebo importujte data.";
    document.getElementById('inventory').innerHTML = "Inventář: Prázdný";
    renderChoices([]); // Initially no choices
    showSection(activeSection); // Show system section on load

    // Event listener for file input change
    document.getElementById('importFileInput').addEventListener('change', importGameData);

    // --- TTS Initialization ---
    if (synth) {
        // Load voices once they are available
        const loadVoicesAndSetSelection = () => {
            voices = synth.getVoices();
            populateVoiceList();
            // Restore saved voice after voices are loaded
            if (systemSettings.ttsVoiceURI) {
                const selectedVoice = voices.find(v => v.voiceURI === systemSettings.ttsVoiceURI);
                if (selectedVoice) {
                    document.getElementById('tts-voice').value = systemSettings.ttsVoiceURI;
                } else {
                    // Fallback to default or first available if saved voice not found
                    if (voices.length > 0) {
                        document.getElementById('tts-voice').value = voices[0].voiceURI;
                        systemSettings.ttsVoiceURI = voices[0].voiceURI;
                        saveSystemSettings(); // Save the new default
                    }
                }
            } else if (voices.length > 0) { // If no voice saved, set first available
                document.getElementById('tts-voice').value = voices[0].voiceURI;
                systemSettings.ttsVoiceURI = voices[0].voiceURI;
                saveSystemSettings();
            }
        };

        // Some browsers fire voiceschanged directly, others need a timeout/event
        if (synth.onvoiceschanged !== undefined) {
            synth.onvoiceschanged = loadVoicesAndSetSelection;
        }
        // Also try to load immediately in case voices are already loaded
        loadVoicesAndSetSelection();

        // Update display for pitch and rate sliders
        document.getElementById('tts-pitch').addEventListener('input', (e) => {
            document.getElementById('tts-pitch-value').innerText = parseFloat(e.target.value).toFixed(1);
        });
        document.getElementById('tts-rate').addEventListener('input', (e) => {
            document.getElementById('tts-rate-value').innerText = parseFloat(e.target.value).toFixed(1);
        });

    } else {
        showError("Váš prohlížeč nepodporuje Text-to-Speech (Web Speech API).");
        document.getElementById('tts-enabled').disabled = true;
        document.getElementById('tts-voice').disabled = true;
        document.getElementById('tts-pitch').disabled = true;
        document.getElementById('tts-rate').disabled = true;
        document.getElementById('test-tts-button').disabled = true; // Disable test button
    }
    // --- End TTS Initialization ---
});

// --- Core UI Functions (Mostly Unchanged) ---
function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("expanded");
    if (sidebar.classList.contains("expanded")) {
        showSection(activeSection);
    } else {
        document.getElementById("sidebar-content").style.display = "none";
    }
}

function updateHistory(message, speak = true) {
    history.push(message);
    document.getElementById("history").innerHTML = history.map(h => `<p>${h}</p>`).join("");
    const historyDiv = document.getElementById("history");
    historyDiv.scrollTop = historyDiv.scrollHeight;
    if (speak) { // Only speak if explicitly requested or default
        speakText(message);
    }
}

function showError(message) {
    const errorDiv = document.getElementById("error-message");
    errorDiv.innerText = message;
    errorDiv.style.display = "block";
    setTimeout(() => { errorDiv.style.display = "none"; }, 5000);
}

function showSection(section) {
    activeSection = section;
    const sections = document.querySelectorAll('.section-content');
    sections.forEach(s => s.style.display = 'none');
    document.getElementById(`${section}-section`).style.display = 'block';

    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => item.classList.remove('active'));
    document.querySelector(`.menu-item[data-section="${section}"]`).classList.add('active');

    resetCharacterWizard();
    resetStoryWizard();
    resetLocationWizard();
}

// --- Character Management (Updated for new model and "Set as Player" and "Race") ---
function updateCharacters() {
    const charListDiv = document.getElementById("character-list");
    charListDiv.innerHTML = "";
    if (characters.length === 0) {
        charListDiv.innerHTML = "<p>Žádné postavy zatím nebyly přidány.</p>";
        return;
    }
    characters.forEach((char, index) => {
        const charItem = document.createElement("div");
    charItem.classList.add("list-item");
    const isPlayer = systemSettings.currentPlayerCharacterIndex === index;
    charItem.innerHTML = `
        <span class="list-item-name">${char.name} ${isPlayer ? '(Hráč)' : ''}</span>
        <div class="list-item-controls">
            <button class="action-button" onclick="editCharacter(${index})">Upravit</button>
            <button class="action-button delete" onclick="deleteCharacter(${index})">Smazat</button>
            <button class="action-button ${isPlayer ? 'active-player-button' : ''}" onclick="setPlayerCharacter(${index})">Nastavit jako Hráče</button>
        </div>
        <p>Rasa: ${char.race || 'Nezadáno'}</p>
        <p>Vzhled: ${char.appearance || 'Nezadáno'}</p>
        <p>Osobnost: ${char.personality || 'Nezadáno'}</p>
        <p>Sexualita: ${char.sexuality || 'Nezadáno'}</p>
        <p>Atributy: ${Object.keys(char.attributes).length > 0 ? JSON.stringify(char.attributes) : 'Nezadáno'}</p>
        <p>Dovednosti: ${char.skills.join(', ') || 'Nezadáno'}</p>
    `;
        charListDiv.appendChild(charItem);
    });
}

// New: Set a character as the player
function setPlayerCharacter(index) {
    if (systemSettings.currentPlayerCharacterIndex === index) {
        systemSettings.currentPlayerCharacterIndex = -1; // Deselect if already selected
        showError(`Postava ${characters[index].name} odznačena jako hráč.`);
    } else {
        systemSettings.currentPlayerCharacterIndex = index;
        showError(`Postava ${characters[index].name} nastavena jako hráč.`);
    }
    saveSystemSettings(); // Save the new setting
    updateCharacters(); // Re-render character list to show (Hráč) badge
    displayPlayerStats(); // Update the player stats panel
}

// New: Display selected player character's stats
function displayPlayerStats() {
    const playerStatsContentDiv = document.getElementById('player-stats-content');
    const playerCharIndex = systemSettings.currentPlayerCharacterIndex;

    if (playerCharIndex !== -1 && characters[playerCharIndex]) {
        const player = characters[playerCharIndex];
        let statsHtml = `
            <p><strong>Jméno:</strong> ${player.name}</p>
            <p><strong>Rasa:</strong> ${player.race || 'Nezadáno'}</p>
            <p><strong>Vzhled:</strong> ${player.appearance || 'Nezadáno'}</p>
            <p><strong>Osobnost:</strong> ${player.personality || 'Nezadáno'}</p>
            <p><strong>Sexualita:</strong> ${player.sexuality || 'Nezadáno'}</p>
        `;
        
        if (Object.keys(player.attributes).length > 0) {
            statsHtml += `<p><strong>Atributy:</strong></p><ul>`;
            for (const [key, value] of Object.entries(player.attributes)) {
                statsHtml += `<li>${key}: ${value}</li>`;
            }
            statsHtml += `</ul>`;
        } else {
            statsHtml += `<p><strong>Atributy:</strong> Nezadáno</p>`;
        }

        if (player.skills.length > 0) {
            statsHtml += `<p><strong>Dovednosti:</strong> ${player.skills.join(', ')}</p>`;
        } else {
            statsHtml += `<p><strong>Dovednosti:</strong> Nezadáno</p>`;
        }
        playerStatsContentDiv.innerHTML = statsHtml;
    } else {
        playerStatsContentDiv.innerHTML = "<p>Vyber postavu ve Správě Postav, abys ji mohl hrát.</p>";
    }
}


function startCharacterWizard(index = -1) {
    characterWizard.editingIndex = index;
    document.getElementById('character-list-display').style.display = 'none';
    document.getElementById('character-wizard').style.display = 'block';

    if (index !== -1) {
        const charToEdit = characters[index];
        characterWizard.tempChar = { ...charToEdit };
        document.getElementById('char-name').value = characterWizard.tempChar.name;
        document.getElementById('char-race').value = characterWizard.tempChar.race; // Set race value
        document.getElementById('char-appearance').value = characterWizard.tempChar.appearance;
        document.getElementById('char-personality').value = characterWizard.tempChar.personality;
        document.getElementById('char-sexuality').value = characterWizard.tempChar.sexuality;
        document.getElementById('char-attributes').value = JSON.stringify(characterWizard.tempChar.attributes, null, 2);
        document.getElementById('char-skills').value = characterWizard.tempChar.skills.join(', ');
    } else {
        characterWizard.tempChar = { name: '', race: '', appearance: '', personality: '', sexuality: '', attributes: {}, skills: [] }; // Initialize race
        document.getElementById('char-name').value = '';
        document.getElementById('char-race').value = ''; // Clear race field
        document.getElementById('char-appearance').value = '';
        document.getElementById('char-personality').value = '';
        document.getElementById('char-sexuality').value = '';
        document.getElementById('char-attributes').value = '';
        document.getElementById('char-skills').value = '';
    }
    characterWizard.currentStep = 1;
    showCharacterWizardStep(1);
}

function showCharacterWizardStep(step) {
    document.querySelectorAll('#character-wizard .wizard-step').forEach(s => s.style.display = 'none');
    document.getElementById(`char-step-${step}`).style.display = 'block';
}

function nextCharacterWizardStep() {
    if (characterWizard.currentStep === 1) {
        const name = document.getElementById('char-name').value.trim();
        const race = document.getElementById('char-race').value.trim(); // Get race value
        const appearance = document.getElementById('char-appearance').value.trim();
        if (!name) { showError("Jméno postavy nesmí být prázdné."); return; }
        characterWizard.tempChar.name = name;
        characterWizard.tempChar.race = race; // Set race
        characterWizard.tempChar.appearance = appearance;
        characterWizard.currentStep = 2;
        showCharacterWizardStep(2);
    } else if (characterWizard.currentStep === 2) {
        const personality = document.getElementById('char-personality').value.trim();
        const sexuality = document.getElementById('char-sexuality').value.trim();
        characterWizard.tempChar.personality = personality;
        characterWizard.tempChar.sexuality = sexuality;
        characterWizard.currentStep = 3;
        showCharacterWizardStep(3);
    }
}

function prevCharacterWizardStep() {
    if (characterWizard.currentStep === 3) {
        characterWizard.currentStep = 2;
        showCharacterWizardStep(2);
    } else if (characterWizard.currentStep === 2) {
        characterWizard.currentStep = 1;
        showCharacterWizardStep(1);
    }
}

function saveCharacterFromWizard() {
    const attributesText = document.getElementById('char-attributes').value.trim();
    const skillsText = document.getElementById('char-skills').value.trim();

    try {
        characterWizard.tempChar.attributes = attributesText ? JSON.parse(attributesText) : {};
    } catch (e) {
        showError("Atributy musí být platný JSON (např. {'síla': 10}).");
        return;
    }
    characterWizard.tempChar.skills = skillsText ? skillsText.split(',').map(s => s.trim()).filter(s => s) : [];

    if (characterWizard.editingIndex !== -1) {
        characters[characterWizard.editingIndex] = { ...characterWizard.tempChar };
        showError("Postava upravena.");
    } else {
        characters.push({ ...characterWizard.tempChar });
        showError("Postava přidána.");
    }
    updateCharacters();
    resetCharacterWizard();
    displayPlayerStats(); // Update player stats in case current player char was edited
}

function resetCharacterWizard() {
    characterWizard.currentStep = 1;
    characterWizard.tempChar = { name: '', race: '', appearance: '', personality: '', sexuality: '', attributes: {}, skills: [] }; // Reset race
    characterWizard.editingIndex = -1;
    document.getElementById('character-wizard').style.display = 'none';
    document.getElementById('character-list-display').style.display = 'block';
    // Clear form fields
    document.getElementById('char-name').value = '';
    document.getElementById('char-race').value = ''; // Clear race field
    document.getElementById('char-appearance').value = '';
    document.getElementById('char-personality').value = '';
    document.getElementById('char-sexuality').value = '';
    document.getElementById('char-attributes').value = '';
    document.getElementById('char-skills').value = '';
}

function editCharacter(index) {
    startCharacterWizard(index);
}

function deleteCharacter(index) {
    if (confirm("Opravdu chcete smazat tuto postavu?")) {
        characters.splice(index, 1);
        // If the deleted character was the player, reset player character
        if (systemSettings.currentPlayerCharacterIndex === index) {
            systemSettings.currentPlayerCharacterIndex = -1;
        } else if (systemSettings.currentPlayerCharacterIndex > index) {
            // Adjust index if a character before the player was deleted
            systemSettings.currentPlayerCharacterIndex--;
        }
        saveSystemSettings();
        updateCharacters();
        displayPlayerStats(); // Update player stats after deletion
        showError("Postava smazána.");
    }
}

// --- Story Management (Updated for new model) ---
function updateStories() {
    const storyListDiv = document.getElementById("story-list");
    storyListDiv.innerHTML = "";
    const storyKeys = Object.keys(customStories);
    if (storyKeys.length === 0) {
        storyListDiv.innerHTML = "<p>Žádné vlastní příběhy zatím nebyly přidány.</p>";
        return;
    }
    storyKeys.forEach(key => {
        const story = customStories[key];
        const storyItem = document.createElement("div");
        storyItem.classList.add("list-item");
        storyItem.innerHTML = `
            <span class="list-item-name">Akce: "${story.action}"</span>
            <div class="list-item-controls">
                <button class="action-button" onclick="editStory('${key}')">Upravit</button>
                <button class="action-button delete" onclick="deleteStory('${key}')">Smazat</button>
            </div>
            <p>Odpověď: ${story.response}</p>
            <p>Lokace: ${story.location || 'Nezadáno'}</p>
            <p>Postavy: ${story.characters.join(', ') || 'Nezadáno'}</p>
            <p>Historie: ${story.history_context.join(', ') || 'Nezadáno'}</p>
            <p>Cíl: ${story.goal || 'Nezadáno'}</p>
        `;
        storyListDiv.appendChild(storyItem);
    });
}

function startStoryWizard(key = null) {
    storyWizard.editingKey = key;
    document.getElementById('story-list-display').style.display = 'none';
    document.getElementById('story-wizard').style.display = 'block';

    if (key !== null) {
        const storyToEdit = customStories[key];
        storyWizard.tempStory = { ...storyToEdit };
        document.getElementById('story-action').value = storyWizard.tempStory.action;
        document.getElementById('story-response').value = storyWizard.tempStory.response;
        document.getElementById('story-location').value = storyWizard.tempStory.location;
        document.getElementById('story-characters').value = storyWizard.tempStory.characters.join(', ');
        document.getElementById('story-history-context').value = storyWizard.tempStory.history_context.join(', ');
        document.getElementById('story-goal').value = storyWizard.tempStory.goal;
        document.getElementById('story-key').value = key;
    } else {
        storyWizard.tempStory = { action: '', response: '', location: '', characters: [], history_context: [], goal: '' };
        document.getElementById('story-action').value = '';
        document.getElementById('story-response').value = '';
        document.getElementById('story-location').value = '';
        document.getElementById('story-characters').value = '';
        document.getElementById('story-history-context').value = '';
        document.getElementById('story-goal').value = '';
        document.getElementById('story-key').value = '';
    }
    storyWizard.currentStep = 1;
    showStoryWizardStep(1);
}

function showStoryWizardStep(step) {
    document.querySelectorAll('#story-wizard .wizard-step').forEach(s => s.style.display = 'none');
    document.getElementById(`story-step-${step}`).style.display = 'block';
}

function nextStoryWizardStep() {
    if (storyWizard.currentStep === 1) {
        const action = document.getElementById('story-action').value.trim().toLowerCase();
        const response = document.getElementById('story-response').value.trim();
        if (!action) { showError("Akce nesmí být prázdná."); return; }
        if (!response) { showError("Odpověď vypravěče nesmí být prázdná."); return; }
        storyWizard.tempStory.action = action;
        storyWizard.tempStory.response = response;
        storyWizard.currentStep = 2;
        showStoryWizardStep(2);
    } else if (storyWizard.currentStep === 2) {
        const locationName = document.getElementById('story-location').value.trim();
        const charNames = document.getElementById('story-characters').value.trim();
        
        // Basic validation for location and characters
        if (locationName && !locations.some(loc => loc.name.toLowerCase() === locationName.toLowerCase())) {
            showError(`Lokace '${locationName}' neexistuje. Přidej ji nejdřív do správy lokací.`);
            return;
        }
        const invalidChars = charNames.split(',').map(s => s.trim()).filter(s => s && !characters.some(char => char.name.toLowerCase() === s.toLowerCase()));
        if (invalidChars.length > 0) {
            showError(`Postavy '${invalidChars.join(', ')}' neexistují. Přidej je nejdřív do správy postav.`);
            return;
        }

        storyWizard.tempStory.location = locationName;
        storyWizard.tempStory.characters = charNames ? charNames.split(',').map(s => s.trim()).filter(s => s) : [];
        storyWizard.currentStep = 3;
        showStoryWizardStep(3);
    }
}

function prevStoryWizardStep() {
    if (storyWizard.currentStep === 3) {
        storyWizard.currentStep = 2;
        showStoryWizardStep(2);
    } else if (storyWizard.currentStep === 2) {
        storyWizard.currentStep = 1;
        showStoryWizardStep(1);
    }
}

function saveStoryFromWizard() {
    const historyContext = document.getElementById('story-history-context').value.trim();
    const goal = document.getElementById('story-goal').value.trim();

    storyWizard.tempStory.history_context = historyContext ? historyContext.split(',').map(s => s.trim()).filter(s => s) : [];
    storyWizard.tempStory.goal = goal;

    const originalKey = document.getElementById('story-key').value;
    const newKey = storyWizard.tempStory.action;

    if (storyWizard.editingKey !== null && originalKey && originalKey !== newKey) {
        delete customStories[originalKey];
    }

    if (customStories[newKey] && storyWizard.editingKey === null) {
        showError(`Příběh s akcí "${newKey}" už existuje.`);
        return;
    }

    customStories[newKey] = { ...storyWizard.tempStory };
    showError("Příběh uložen.");

    updateStories();
    resetStoryWizard();
}

function resetStoryWizard() {
    storyWizard.currentStep = 1;
    storyWizard.tempStory = { action: '', response: '', location: '', characters: [], history_context: [], goal: '' };
    storyWizard.editingKey = null;
    document.getElementById('story-wizard').style.display = 'none';
    document.getElementById('story-list-display').style.display = 'block';
    // Clear form fields
    document.getElementById('story-action').value = '';
    document.getElementById('story-response').value = '';
    document.getElementById('story-location').value = '';
    document.getElementById('story-characters').value = '';
    document.getElementById('story-history-context').value = '';
    document.getElementById('story-goal').value = '';
    document.getElementById('story-key').value = '';
}

function editStory(key) {
    startStoryWizard(key);
}

function deleteStory(key) {
    if (confirm(`Opravdu chcete smazat příběh s akcí "${key}"?`)) {
        delete customStories[key];
        updateStories();
        showError("Příběh smazán.");
    }
}

// --- Location Management (Unchanged from previous version) ---
function updateLocations() {
    const locListDiv = document.getElementById("location-list");
    locListDiv.innerHTML = "";
    if (locations.length === 0) {
        locListDiv.innerHTML = "<p>Žádné lokace zatím nebyly přidány.</p>";
        return;
    }
    locations.forEach((loc, index) => {
        const locItem = document.createElement("div");
        locItem.classList.add("list-item");
        locItem.innerHTML = `
            <span class="list-item-name">${loc.name}</span>
            <div class="list-item-controls">
                <button class="action-button" onclick="editLocation(${index})">Upravit</button>
                <button class="action-button delete" onclick="deleteLocation(${index})">Smazat</button>
            </div>
            <p>${loc.desc}</p>
        `;
        locListDiv.appendChild(locItem);
    });
}

function startLocationWizard(index = -1) {
    locationWizard.editingIndex = index;
    document.getElementById('location-list-display').style.display = 'none';
    document.getElementById('location-wizard').style.display = 'block';

    if (index !== -1) {
        const locToEdit = locations[index];
        locationWizard.tempLocation = { ...locToEdit };
        document.getElementById('loc-name').value = locationWizard.tempLocation.name;
        document.getElementById('loc-desc').value = locationWizard.tempLocation.desc;
    } else {
        locationWizard.tempLocation = { name: '', desc: '' };
        document.getElementById('loc-name').value = '';
        document.getElementById('loc-desc').value = '';
    }
    locationWizard.currentStep = 1;
    showLocationWizardStep(1);
}

function showLocationWizardStep(step) {
    document.querySelectorAll('#location-wizard .wizard-step').forEach(s => s.style.display = 'none');
    document.getElementById(`loc-step-${step}`).style.display = 'block';
}

function nextLocationWizardStep() {
    if (locationWizard.currentStep === 1) {
        const name = document.getElementById('loc-name').value.trim();
        if (!name) { showError("Název lokace nesmí být prázdný."); return; }
        locationWizard.tempLocation.name = name;
        locationWizard.currentStep = 2;
        showLocationWizardStep(2);
    }
}

function prevLocationWizardStep() {
    if (locationWizard.currentStep === 2) {
        locationWizard.currentStep = 1;
        showLocationWizardStep(1);
    }
}

function saveLocationFromWizard() {
    const desc = document.getElementById('loc-desc').value.trim();
    if (!desc) { showError("Popis lokace nesmí být prázdný."); return; }
    locationWizard.tempLocation.desc = desc;

    if (locationWizard.editingIndex !== -1) {
        locations[locationWizard.editingIndex] = { ...locationWizard.tempLocation };
        showError("Lokace upravena.");
    } else {
        locations.push({ ...locationWizard.tempLocation });
        showError("Lokace přidána.");
    }
    updateLocations();
    resetLocationWizard();
}

function resetLocationWizard() {
    locationWizard.currentStep = 1;
    locationWizard.tempLocation = { name: '', desc: '' };
    locationWizard.editingIndex = -1;
    document.getElementById('location-wizard').style.display = 'none';
    document.getElementById('location-list-display').style.display = 'block';
    document.getElementById('loc-name').value = '';
    document.getElementById('loc-desc').value = '';
}

function editLocation(index) {
    startLocationWizard(index);
}

function deleteLocation(index) {
    if (confirm("Opravdu chcete smazat tuto lokaci?")) {
        locations.splice(index, 1);
        updateLocations();
        showError("Lokace smazána.");
    }
}

// --- System Settings (Now includes TTS settings and Player Character) ---
function loadSystemSettings() {
    // Narrator settings
    document.getElementById('narrator-tone').value = systemSettings.tone;
    document.getElementById('narrator-instructions').value = systemSettings.instructions;

    // TTS settings
    document.getElementById('tts-enabled').checked = systemSettings.ttsEnabled;
    document.getElementById('tts-pitch').value = systemSettings.ttsPitch;
    document.getElementById('tts-rate').value = systemSettings.ttsRate;
    document.getElementById('tts-pitch-value').innerText = systemSettings.ttsPitch.toFixed(1);
    document.getElementById('tts-rate-value').innerText = systemSettings.ttsRate.toFixed(1);

    // Populate voice list on load/init, then select saved voice
    if (voices.length > 0) {
        populateVoiceList();
        if (systemSettings.ttsVoiceURI) {
            document.getElementById('tts-voice').value = systemSettings.ttsVoiceURI;
        }
    }
    // currentPlayerCharacterIndex is loaded into systemSettings object directly
}

function saveSystemSettings() {
    systemSettings.tone = document.getElementById('narrator-tone').value;
    systemSettings.instructions = document.getElementById('narrator-instructions').value;
    
    // Save TTS settings
    systemSettings.ttsEnabled = document.getElementById('tts-enabled').checked;
    systemSettings.ttsVoiceURI = document.getElementById('tts-voice').value;
    systemSettings.ttsPitch = parseFloat(document.getElementById('tts-pitch').value);
    systemSettings.ttsRate = parseFloat(document.getElementById('tts-rate').value);

    // currentPlayerCharacterIndex is already updated by setPlayerCharacter, just save it
    // showError("Nastavení systému a TTS uloženo."); // This might be too frequent now, removed from here
}

// --- TTS Functions ---
function populateVoiceList() {
    const voiceSelect = document.getElementById('tts-voice');
    voiceSelect.innerHTML = ''; // Clear previous options
    voices.forEach(voice => {
        const option = document.createElement('option');
        option.textContent = `${voice.name} (${voice.lang})`;
        option.value = voice.voiceURI; // Use voiceURI for persistent identification
        // Select preferred language if available (e.g., Czech)
        if (voice.lang.includes('cs') || voice.lang.includes('en-US')) { // Prioritize Czech, then US English
            option.setAttribute('data-lang', voice.lang);
            option.setAttribute('data-name', voice.name);
        }
        voiceSelect.appendChild(option);
    });

    // Try to set a default if none is selected or saved
    if (!voiceSelect.value && voices.length > 0) {
        // Try to find a Czech voice first
        const czechVoice = voices.find(v => v.lang.includes('cs'));
        if (czechVoice) {
            voiceSelect.value = czechVoice.voiceURI;
        } else {
            // Fallback to English or first available
            const englishVoice = voices.find(v => v.lang.includes('en'));
            if (englishVoice) {
                voiceSelect.value = englishVoice.voiceURI;
            } else {
                voiceSelect.value = voices[0].voiceURI;
            }
        }
        systemSettings.ttsVoiceURI = voiceSelect.value;
        saveSystemSettings();
    }
}

function speakText(text) {
    if (!synth || !systemSettings.ttsEnabled) {
        return;
    }

    // Stop any ongoing speech
    if (synth.speaking) {
        synth.cancel();
    }

    const utterance = new SpeechSynthesisUtterance(text);
    const selectedVoiceURI = document.getElementById('tts-voice').value;
    const selectedVoice = voices.find(voice => voice.voiceURI === selectedVoiceURI);

    if (selectedVoice) {
        utterance.voice = selectedVoice;
    } else {
        // Fallback if selected voice is not found
        console.warn("Selected TTS voice not found, using default.");
    }

    utterance.pitch = systemSettings.ttsPitch;
    utterance.rate = systemSettings.ttsRate;

    synth.speak(utterance);
}

function updateTtsValue(type, value) {
    document.getElementById(`tts-${type}-value`).innerText = parseFloat(value).toFixed(1);
    // Setting will be saved on change event of the slider
}

function testTtsVoice() {
    speakText("Testovací text. Slyšíš mě, ty špinavá děvko?");
}

// --- Export/Import Game Data (Adapted to new models) ---
function exportGameData() {
    const gameData = {
        characters: characters,
        customStories: customStories,
        locations: locations,
        systemSettings: systemSettings, // Includes TTS settings and currentPlayerCharacterIndex now
        // Current game state (optional, can be reset on import)
        inventory: inventory,
        history: history,
        scene: scene,
        choices: choices
    };

    const dataStr = JSON.stringify(gameData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'slave_game_data.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showError("Data hry exportována. Ulož si to, abys o nic nepřišel!");
}

function importGameData(event) {
    const file = event.target.files[0];
    if (!file) {
        showError("Žádný soubor nevybrán.");
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const importedData = JSON.parse(e.target.result);

            // Validate and assign imported data (with basic checks)
            if (importedData.characters && Array.isArray(importedData.characters)) {
                characters = importedData.characters;
            }
            if (importedData.customStories && typeof importedData.customStories === 'object') {
                customStories = importedData.customStories;
            }
            if (importedData.locations && Array.isArray(importedData.locations)) {
                locations = importedData.locations;
            }
            // --- Update for systemSettings to merge, not overwrite ---
            if (importedData.systemSettings && typeof importedData.systemSettings === 'object') {
                // Merge imported settings to preserve new defaults if not present in old data
                systemSettings = { ...systemSettings, ...importedData.systemSettings };
            }
            // --- End update for systemSettings ---

            // Optional: Import current game state, or reset it
            inventory = importedData.inventory || [];
            history = importedData.history || [];
            scene = importedData.scene || "";
            choices = importedData.choices || [];


            // Update GUI and game state
            updateCharacters();
            updateStories();
            updateLocations();
            loadSystemSettings(); // This will apply imported TTS and player char settings to UI
            displayPlayerStats(); // New: Update player stats panel after import
            document.getElementById('scene').innerHTML = scene || "Data importována. Spusťte novou hru!";
            document.getElementById('inventory').innerHTML = "Inventář: " + (inventory.length > 0 ? inventory.join(", ") : "Prázdný");
            renderChoices(choices);
            updateHistory("Data hry byla importována. Pokračuj ve svém utrpení!", false); // Don't speak this message on import

            showError("Data hry úspěšně importována!");
        } catch (error) {
            console.error("Error importing game data:", error);
            showError("Chyba při importu dat: Neplatný soubor JSON nebo poškozená data.");
        } finally {
            event.target.value = ''; // Clear file input
        }
    };
    reader.readAsText(file);
}

// --- Game Initialization ---
async function startGame() {
    // Reset game state
    inventory = [];
    history = [];
    scene = "Začínáme novou hru... připrav se na své ponížení.";
    choices = [];
    document.getElementById('inventory').innerHTML = "Inventář: Prázdný";
    document.getElementById('history').innerHTML = ""; // Clear history display

    updateHistory("Hra začíná...", true); // Speak this
    document.getElementById('scene').innerHTML = scene;
    renderChoices([]); // Clear choices while waiting for AI

    // Construct initial prompt based on selected player character
    let initialPrompt = "Začni hru. Jsem v temném, smradlavém sklepení, připravený na ponížení. Představ mi situaci a první 3 možnosti akce.";
    const playerCharIndex = systemSettings.currentPlayerCharacterIndex;
    if (playerCharIndex !== -1 && characters[playerCharIndex]) {
        const player = characters[playerCharIndex];
        initialPrompt = `Začni hru. Jsem postava jménem ${player.name}, rasa ${player.race || 'nezadáno'}, vypadám takto: ${player.appearance || 'nezadáno'}, a jsem ${player.personality || 'nezadáno'} povahy. Moje sexualita je ${player.sexuality || 'nezadána'}. Moje atributy jsou ${JSON.stringify(player.attributes)}. Moje dovednosti jsou ${player.skills.join(', ')}. Jsem v temném, smradlavém sklepení, připravený na ponížení. Představ mi situaci a první 3 možnosti akce, ber v úvahu mou postavu.`;
    }

    // Call Grok API for initial scene and choices
    try {
        const grokResponse = await callGrokAPI(initialPrompt, false);
        updateHistory(grokResponse.output, true); // Speak output
        scene = grokResponse.scene;
        choices = grokResponse.choices;
        document.getElementById("scene").innerHTML = scene;
        speakText(scene); // Speak scene description
        renderChoices(choices);
    } catch (error) {
        console.error("Error starting game:", error);
        showError("Nepodařilo se spustit hru. Zkontrolujte API a nastavení.");
    }
}


// --- Game Logic (Minor Adjustments for Dynamic Choices) ---

function renderChoices(newChoices) {
    const choicesDiv = document.getElementById("choices");
    choicesDiv.innerHTML = "";
    if (newChoices && newChoices.length > 0) {
        newChoices.forEach(choice => {
            const button = document.createElement("button");
            button.innerText = choice;
            button.onclick = () => action(choice);
            choicesDiv.appendChild(button);
        });
    } else {
        // Fallback choices if AI doesn't provide any or on game start before AI response
        choicesDiv.innerHTML = `
            <button onclick="action('Co dál?')">Co dál?</button>
            <button onclick="action('Prosit o milost')">Prosit o milost</button>
            <button onclick="action('Uprchnout')">Uprchnout</button>
        `;
    }
}

async function callGrokAPI(prompt, isCustom = false) {
    const defaultMaxTokens = 4096;
    const defaultTemperature = 0.9; // Moderate creativity

    const requestBody = {
        prompt: prompt,
        max_tokens: defaultMaxTokens,
        temperature: defaultTemperature,
        system_tone: systemSettings.tone,
        system_instructions: systemSettings.instructions,
        history: history, // Send full history for context
        characters: characters, // Send full character data for context
        inventory: inventory, // Send full inventory for context
        current_scene: scene, // Current scene for context
        locations: locations, // Send full location data for context
        currentPlayerCharacter: systemSettings.currentPlayerCharacterIndex !== -1 && characters[systemSettings.currentPlayerCharacterIndex] ? characters[systemSettings.currentPlayerCharacterIndex] : null // Send player character data
    };

    try {
        const response = await fetch('http://localhost:3000/api/grok', { // Updated port to 3000 as per backend.py
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            const errorData = await response.json();
            showError(`API Error: ${errorData.error || response.statusText}`);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const content = data.choices[0].message.content;

        let parsedContent;
        try {
            parsedContent = JSON.parse(content);
        } catch (e) {
            console.error("Failed to parse Grok API response as JSON:", e);
            console.error("Raw Grok API response:", content);
            showError("Vypravěč se zbláznil! Zkus to znovu. (Chyba formátu AI odpovědi)");
            throw new Error("Invalid JSON from Grok API");
        }

        if (!parsedContent.output || !parsedContent.scene || !parsedContent.choices || !Array.isArray(parsedContent.choices)) {
            showError("Vypravěčova odpověď je neúplná nebo špatně formátovaná. Zkus to znovu.");
            throw new Error("Missing expected fields in Grok API response");
        }

        return parsedContent;

    } catch (error) {
        console.error("Error calling Grok API:", error);
        throw error;
    }
}

async function action(choice) {
    updateHistory(`> ${choice}`, false); // Don't speak player actions

    const lowerCaseChoice = choice.toLowerCase();
    if (customStories[lowerCaseChoice]) {
        const story = customStories[lowerCaseChoice];
        updateHistory(story.response, true); // Speak response
        scene = `Nová scéna: ${story.location || 'Neznámá lokace'}. Zapojení postav: ${story.characters.join(', ') || 'žádné'}. Cíl: ${story.goal || 'neznámý'}. Historický kontext: ${story.history_context.join(', ') || 'žádný'}.`; // Combine relevant story data for a new scene prompt
        document.getElementById("scene").innerHTML = story.response; // For immediate display
        speakText(scene); // Speak the new scene description (from custom story)

        // Call Grok to generate next steps based on the custom story's outcome
        try {
            const grokPrompt = `Po akci "${choice}" se stalo toto: "${story.response}". Nyní je scéna: "${scene}". Vzhledem k tomuto se děje co dál?`;
            const grokResponse = await callGrokAPI(grokPrompt, false);
            updateHistory(grokResponse.output, true); // Speak output
            scene = grokResponse.scene;
            choices = grokResponse.choices;
            document.getElementById("scene").innerHTML = scene;
            speakText(scene); // Speak new scene
            renderChoices(choices);
            // Grok might suggest inventory items, but custom story won't add directly here.
            // If the custom story implies an inventory change, Grok should be prompted to reflect that.
        } catch (error) {
            console.error("Error after custom story:", error);
        }
        return;
    }

    // No custom story, call Grok API
    try {
        const grokResponse = await callGrokAPI(choice, false);
        updateHistory(grokResponse.output, true); // Speak output
        scene = grokResponse.scene;
        choices = grokResponse.choices;
        document.getElementById("scene").innerHTML = scene;
        speakText(scene); // Speak new scene
        renderChoices(choices);
        // Assuming Grok will manage inventory changes in its output if applicable
        if (grokResponse.inventory && !inventory.includes(grokResponse.inventory)) { // Prevent duplicates if Grok sends inventory
            inventory.push(grokResponse.inventory);
            document.getElementById("inventory").innerHTML = "Inventář: " + inventory.join(", ");
        }
    } catch (error) {
        console.error("Error during action:", error);
    }
}

async function customAction() {
    const input = document.getElementById("text-input").value.trim().toLowerCase();
    if (!input) {
        showError("Nic jsi nezadal.");
        return;
    }

    updateHistory(`> ${input}`, false); // Don't speak player input

    if (customStories[input]) {
        const story = customStories[input];
        updateHistory(story.response, true); // Speak response
        scene = `Nová scéna: ${story.location || 'Neznámá lokace'}. Zapojení postav: ${story.characters.join(', ') || 'žádné'}. Cíl: ${story.goal || 'neznámý'}. Historický kontext: ${story.history_context.join(', ') || 'žádný'}.`;
        document.getElementById("scene").innerHTML = story.response; // For immediate display
        speakText(scene); // Speak new scene (from custom story)

        try {
            const grokPrompt = `Po vlastní akci "${input}" se stalo toto: "${story.response}". Nyní je scéna: "${scene}". Vzhledem k tomuto se děje co dál?`;
            const grokResponse = await callGrokAPI(grokPrompt, false);
            updateHistory(grokResponse.output, true); // Speak output
            scene = grokResponse.scene;
            choices = grokResponse.choices;
            document.getElementById("scene").innerHTML = scene;
            speakText(scene); // Speak new scene
            renderChoices(choices);
        } catch (error) {
            console.error("Error after custom story (custom action):", error);
        }
    } else {
        try {
            const grokResponse = await callGrokAPI(input, true);
            updateHistory(grokResponse.output, true); // Speak output
            scene = grokResponse.scene;
            choices = grokResponse.choices;
            document.getElementById("scene").innerHTML = scene;
            speakText(scene); // Speak new scene
            renderChoices(choices);
            if (grokResponse.inventory && !inventory.includes(grokResponse.inventory)) {
                inventory.push(grokResponse.inventory);
                document.getElementById("inventory").innerHTML = "Inventář: " + inventory.join(", ");
            }
        } catch (error) {
            console.error("Error during custom action:", error);
        }
    }
    document.getElementById("text-input").value = "";
}