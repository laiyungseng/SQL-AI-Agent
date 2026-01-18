console.log("SQL AI Agent Frontend Loaded");

// DOM Elements
const sidebar = document.getElementById('sidebar');
const toggleSidebarBtn = document.getElementById('toggle-sidebar');
const openSidebarBtn = document.getElementById('open-sidebar');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatHistory = document.getElementById('chat-history');
const llmConfigForm = document.getElementById('llm-config-form');

// Connection Elements
const btnConfigureDb = document.getElementById('btn-configure-db');
const dbModal = document.getElementById('db-modal');
const closeModalBtn = document.getElementById('close-modal');
const dbConfigForm = document.getElementById('db-config-form');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const dbSelectGroup = document.getElementById('db-select-group');
const dbSelect = document.getElementById('db-name');
const refreshDbsBtn = document.getElementById('refresh-dbs');

// State
let isProcessing = false;
let currentConfig = {
    host: '127.0.0.1',
    port: 3306,
    user: 'root',
    password: '',
    database: ''
};

// Helpers
function scrollToBottom() {
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function appendMessage(role, content) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;

    let formattedContent = content
        .replace(/</g, "&lt;").replace(/>/g, "&gt;")
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/\n/g, '<br>');

    // Icons (SVGs could be used here for more premium look)
    const avatarContent = role === 'user'
        ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        : '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 4V6M12 18V20M6 12H4M20 12H18M15.54 15.54L14.12 14.12M9.88 9.88L8.46 8.46M15.54 8.46L14.12 9.88M9.88 14.12L8.46 15.54" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';

    msgDiv.innerHTML = `
        <div class="avatar">${avatarContent}</div>
        <div class="message-content">
            <p>${formattedContent}</p>
        </div>
    `;

    chatHistory.appendChild(msgDiv);
    scrollToBottom();
    return msgDiv;
}

function updateConnectionStatus(isConnected) {
    if (isConnected) {
        statusDot.className = 'status-dot connected';
        statusText.textContent = 'Connected';
        dbSelectGroup.style.display = 'block';
    } else {
        statusDot.className = 'status-dot disconnected';
        statusText.textContent = 'Disconnected';
        dbSelectGroup.style.display = 'none';
    }
}

async function fetchDatabases() {
    try {
        const response = await fetch('/api/databases');
        if (!response.ok) throw new Error('Failed to fetch databases');
        const data = await response.json();

        let dbs = [];
        if (Array.isArray(data.databases)) {
            dbs = data.databases;
        } else if (typeof data.databases === 'string') {
            // Fallback for string legacy (though server is updated)
            try {
                const matches = data.databases.matchAll(/'([^']*)'/g);
                dbs = Array.from(matches, m => m[1]);
            } catch (e) { dbs = []; }
        }

        // Save current selection to restore if possible
        const currentSelection = dbSelect.value;

        dbSelect.innerHTML = '<option value="" disabled selected>Select Database</option>';
        dbs.forEach(db => {
            // Filter out error messages from being selectable options if possible, 
            // though server should have handled it.
            if (db.startsWith("Error:")) {
                alert("Database Error: " + db);
                return;
            }

            const option = document.createElement('option');
            option.value = db;
            option.textContent = db;
            if (db === currentConfig.database) {
                option.selected = true;
            }
            dbSelect.appendChild(option);
        });

        // If we found databases, we are connected
        updateConnectionStatus(true);

    } catch (error) {
        console.error("Error loading DBs:", error);
        updateConnectionStatus(false);
    }
}

async function saveDbConfig(newConfig) {
    try {
        const response = await fetch('/api/config/db', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newConfig)
        });

        if (response.ok) {
            currentConfig = { ...currentConfig, ...newConfig };
            return true;
        } else {
            alert("Failed to save config.");
            return false;
        }
    } catch (e) {
        alert("Error saving config: " + e.message);
        return false;
    }
}

// Event Listeners

// Sidebar Toggle
toggleSidebarBtn.addEventListener('click', () => {
    sidebar.classList.add('collapsed');
    openSidebarBtn.style.display = 'block';
});

openSidebarBtn.addEventListener('click', () => {
    sidebar.classList.remove('collapsed');
    openSidebarBtn.style.display = 'none';
});

// Modal Actions
btnConfigureDb.addEventListener('click', () => {
    dbModal.style.display = 'flex';
});

closeModalBtn.addEventListener('click', () => {
    dbModal.style.display = 'none';
});

dbModal.addEventListener('click', (e) => {
    if (e.target === dbModal) {
        dbModal.style.display = 'none';
    }
});

// Database Config Submit
dbConfigForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(dbConfigForm);
    const data = Object.fromEntries(formData.entries());

    // We update currentConfig with form data (Host, Port, User, Pass, optional DB)
    const newConfig = {
        host: data.host,
        port: parseInt(data.port),
        user: data.user,
        password: data.password,
        database: data.database || currentConfig.database // Use entered or keep existing
    };

    const success = await saveDbConfig(newConfig);

    if (success) {
        dbModal.style.display = 'none';
        await fetchDatabases(); // Refresh status and list
    }
});

// Database Selection Change
dbSelect.addEventListener('change', async (e) => {
    const selectedDb = e.target.value;
    const newConfig = { ...currentConfig, database: selectedDb };

    const success = await saveDbConfig(newConfig);
    if (success) {
        // Optional: Notify user
        // alert(`Switched to ${selectedDb}`);
    }
});

// Refresh Dbs
refreshDbsBtn.addEventListener('click', (e) => {
    e.preventDefault();
    fetchDatabases();
});

// LLM Config Logic
const llmProviderSelect = document.getElementById('llm-provider');
const llmModelInput = document.getElementById('llm-model');
const llmModelsList = document.getElementById('llm-models-list');
const llmApiKeyInput = document.getElementById('llm-api-key');
const apiKeyGroup = document.getElementById('api-key-group');

async function loadLLMConfig() {
    try {
        const response = await fetch('/api/config/llm');
        if (response.ok) {
            const config = await response.json();

            // Set Provider
            if (config.provider) {
                llmProviderSelect.value = config.provider;
            }

            // Show/Hide API Key field based on provider
            toggleApiKeyField(llmProviderSelect.value);

            // Fetch Models for this provider
            await updateModelOptions(llmProviderSelect.value);

            // Set Model (from env if available)
            if (config.model) {
                llmModelInput.value = config.model;
            }

            // Show placeholder if key exists
            if (config.has_openrouter_key) {
                llmApiKeyInput.placeholder = "•".repeat(config.key_length);
            }
        }
    } catch (e) {
        console.warn("Could not load LLM config:", e);
    }
}

function toggleApiKeyField(provider) {
    if (provider === 'openrouter') {
        apiKeyGroup.style.display = 'block';
    } else {
        apiKeyGroup.style.display = 'none';
        llmApiKeyInput.value = ''; // Clear if switching to local
    }
}

async function updateModelOptions(provider) {
    // Clear current options
    llmModelsList.innerHTML = '';
    llmModelInput.placeholder = "Loading models...";

    try {
        const response = await fetch(`/api/llm/models?provider=${provider}`);
        const data = await response.json();

        llmModelInput.placeholder = "Type to search or select...";

        if (data.models && data.models.length > 0) {
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                llmModelsList.appendChild(option);
            });
        } else {
            // Handle no models
            llmModelInput.placeholder = "No models found";
            if (data.error) {
                console.error(data.error);
                if (provider === 'openrouter') {
                    // alert("Could not fetch OpenRouter models. Check API Key in .env or Settings.");
                }
            }
        }
    } catch (e) {
        console.error("Error fetching models:", e);
        llmModelInput.placeholder = "Error loading models";
    }
}

// Listeners
llmProviderSelect.addEventListener('change', async (e) => {
    const provider = e.target.value;
    toggleApiKeyField(provider);
    await updateModelOptions(provider);
});

llmConfigForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(llmConfigForm);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/api/config/llm', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            alert("LLM Settings Saved!");
            // Refresh models in case key changed
            await updateModelOptions(data.provider);
            // Restore model text
            if (data.model) {
                llmModelInput.value = data.model;
            }
        } else {
            alert("Failed to save LLM settings.");
        }
    } catch (e) {
        alert("Error saving LLM settings: " + e.message);
    }
});

// Chat
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message || isProcessing) return;

    appendMessage('user', message);
    userInput.value = '';
    isProcessing = true;

    const loadingMsg = appendMessage('ai', 'Thinking...');

    try {
        const provider = llmProviderSelect.value;
        const model = llmModelInput.value;
        const apiKey = llmApiKeyInput.value; // Send if typed, else backend uses env

        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                provider: provider,
                model: model,
                api_key: apiKey
            })
        });

        if (!response.ok) throw new Error("API Error");

        const data = await response.json();

        chatHistory.removeChild(loadingMsg);
        appendMessage('ai', data.response);

    } catch (error) {
        chatHistory.removeChild(loadingMsg);
        appendMessage('ai', "Sorry, I encountered an error: " + error.message);
    } finally {
        isProcessing = false;
    }
});

async function loadDbConfig() {
    try {
        const response = await fetch('/api/config/db');
        if (response.ok) {
            const config = await response.json();
            // If we got valid config, update state and form
            if (config.host) {
                currentConfig = { ...currentConfig, ...config };

                // Update Form Fields
                if (document.getElementById('db-host')) document.getElementById('db-host').value = config.host;
                if (document.getElementById('db-port')) document.getElementById('db-port').value = config.port;
                if (document.getElementById('db-user')) document.getElementById('db-user').value = config.user;
                if (document.getElementById('db-pass')) document.getElementById('db-pass').value = config.password;
                if (document.getElementById('db-default')) document.getElementById('db-default').value = config.database;
            }
        }
    } catch (e) {
        console.warn("Could not load initial config:", e);
    }
}

// Init
(async () => {
    await loadDbConfig();
    await fetchDatabases();
    await loadLLMConfig();
})();
