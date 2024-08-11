document.addEventListener("DOMContentLoaded", function() {
    function openChatbot(service) {
        document.getElementById('chatbotTitle').innerText = service + ' Chatbot';
        document.getElementById('chatbotModal').style.display = 'block';
        document.getElementById('chatbotBody').innerHTML = ''; // Clear previous messages
    }

    function closeChatbot() {
        document.getElementById('chatbotModal').style.display = 'none';
    }

    function sendMessage() {
        const input = document.getElementById('chatbotInput');
        const message = input.value.trim();
        if (message !== '') {
            addMessageToChatbot('User', message);
            input.value = '';
            fetch('/get', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({ msg: message }),
            })
            .then(response => response.json())
            .then(data => {
                addMessageToChatbot('Bot', data.response);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    }

    function addMessageToChatbot(sender, message) {
        const chatbotBody = document.getElementById('chatbotBody');
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message';
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatbotBody.appendChild(messageElement);
        chatbotBody.scrollTop = chatbotBody.scrollHeight; // Scroll to the bottom
    }

    document.getElementById('chatbotInput').addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
});
