// DOM Elements
const chatHistory = document.getElementById('chat-history');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const themeToggle = document.getElementById('theme-toggle');
const saveConfigBtn = document.getElementById('save-config');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const featureBtns = document.querySelectorAll('.feature-btn');

// App State
let config = {
    deepseekKey: '',
    isDarkMode: false
};

// Initialize the app
function initApp() {
    loadConfig();
    updateTheme();
    checkApiStatus();
    
    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    
    themeToggle.addEventListener('click', toggleTheme);
    saveConfigBtn.addEventListener('click', saveConfig);
    
    featureBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const command = e.target.dataset.command;
            if (command) {
                userInput.value = command;
                sendMessage();
            }
        });
    });
}

// Load configuration from localStorage
function loadConfig() {
    const savedConfig = localStorage.getItem('aiAssistantConfig');
    if (savedConfig) {
        config = JSON.parse(savedConfig);
        document.getElementById('deepseek-key').value = config.deepseekKey || '';
    }
}

// Save configuration to localStorage
function saveConfig() {
    config.deepseekKey = document.getElementById('deepseek-key').value;
    
    localStorage.setItem('aiAssistantConfig', JSON.stringify(config));
    
    addMessage('Configuration saved successfully!', 'ai');
    checkApiStatus();
}

// Toggle dark/light mode
function toggleTheme() {
    config.isDarkMode = !config.isDarkMode;
    localStorage.setItem('aiAssistantConfig', JSON.stringify(config));
    updateTheme();
}

// Update theme based on config
function updateTheme() {
    if (config.isDarkMode) {
        document.documentElement.classList.add('dark-mode');
        themeToggle.textContent = '☀️';
    } else {
        document.documentElement.classList.remove('dark-mode');
        themeToggle.textContent = '🌙';
    }
}

// Add message to chat history
function addMessage(text, sender = 'user') {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    
    if (sender === 'user') {
        messageDiv.classList.add('user-message');
        messageDiv.textContent = text;
    } else if (sender === 'ai') {
        messageDiv.classList.add('ai-message');
        messageDiv.innerHTML = text; // Allow HTML for links
    } else {
        messageDiv.classList.add('system-message');
        messageDiv.textContent = text;
    }
    
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Check API status
function checkApiStatus() {
    if (config.deepseekKey) {
        statusIndicator.classList.add('connected');
        statusText.textContent = 'Connected to DeepSeek';
    } else {
        statusIndicator.classList.remove('connected');
        statusText.textContent = 'API not configured';
    }
}

// Send message to DeepSeek API
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    userInput.value = '';
    
    // Show loading state
    const sendBtnOriginal = sendBtn.innerHTML;
    sendBtn.innerHTML = '<div class="loading"></div>';
    sendBtn.disabled = true;
    userInput.disabled = true;
    
    try {
        if (!config.deepseekKey) {
            throw new Error('Please configure your DeepSeek API key first');
        }
        
        // Send request to our serverless function
        const response = await fetch('/api/assistant', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                command: message
            })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.error) {
            throw new Error(result.error);
        }
        
        // Add AI response to chat
        addMessage(result.response, 'ai');
        
    } catch (error) {
        addMessage(`Error: ${error.message}`, 'ai');
    } finally {
        // Restore UI
        sendBtn.innerHTML = sendBtnOriginal;
        sendBtn.disabled = false;
        userInput.disabled = false;
        userInput.focus();
    }
}

// Initialize the app when the page loads
window.addEventListener('DOMContentLoaded', initApp);
