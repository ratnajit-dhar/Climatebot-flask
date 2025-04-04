// Global variables
let isProcessing = false;

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Scroll chat to bottom
    scrollToBottom();
    
    // Add enter key listener to input
    const input = document.getElementById('user-input');
    if (input) {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !isProcessing) {
                sendMessage();
            }
        });
    }
});

// Send message function
async function sendMessage() {
    if (isProcessing) return;

    const input = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const question = input.value.trim();

    if (!question) return;

    try {
        isProcessing = true;
        input.disabled = true;
        
        appendMessage('user', question);
        input.value = '';
        
        const loadingId = showLoading();

        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question }),
        });

        hideLoading(loadingId);

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Server error');
        }

        appendMessage('assistant', data.response);

    } catch (error) {
        console.error('Error:', error);
        appendMessage('assistant', `Error: ${error.message}`);
    } finally {
        isProcessing = false;
        input.disabled = false;
        input.focus();
        scrollToBottom();
    }
}

// Clear chat function
async function clearChat() {
    try {
        const response = await fetch('/clear-chat', {
            method: 'POST',
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        // Reload the page to show fresh chat
        window.location.reload();

    } catch (error) {
        console.error('Error:', error);
        alert('Failed to clear chat');
    }
}

// Helper function to append message to chat
function appendMessage(role, content) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role} fade-in`;
    
    // Create message content div
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Helper function to scroll chat to bottom
function scrollToBottom() {
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Show loading indicator
function showLoading() {
    const chatMessages = document.getElementById('chat-messages');
    const loadingDiv = document.createElement('div');
    const loadingId = 'loading-' + Date.now();
    loadingDiv.id = loadingId;
    loadingDiv.className = 'message assistant fade-in';
    loadingDiv.innerHTML = '<div class="spinner"></div>';
    chatMessages.appendChild(loadingDiv);
    scrollToBottom();
    return loadingId;
}

// Hide loading indicator
function hideLoading(loadingId) {
    const loadingDiv = document.getElementById(loadingId);
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

// File upload handling
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert('File uploaded successfully');
            // Reload documents list if on documents page
            if (window.location.pathname === '/documents') {
                window.location.reload();
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to upload file');
    });
}

// Document search functionality
function searchDocuments() {
    const searchInput = document.getElementById('document-search');
    const searchTerm = searchInput.value.toLowerCase();
    const documents = document.getElementsByClassName('document-section');

    Array.from(documents).forEach(doc => {
        const title = doc.querySelector('h2').textContent.toLowerCase();
        if (title.includes(searchTerm)) {
            doc.style.display = '';
        } else {
            doc.style.display = 'none';
        }
    });
}

// Error handling
window.onerror = function(msg, url, lineNo, columnNo, error) {
    console.error('Error: ', msg, '\nURL: ', url, '\nLine: ', lineNo, '\nColumn: ', columnNo, '\nError object: ', error);
    return false;
};

// Add smooth scrolling to all links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});