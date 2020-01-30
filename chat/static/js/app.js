// Connect to web socket.
const hostname = `${window.location.protocol}//${document.domain}:${window.location.port}`;
const socket = io.connect(hostname);

// DOM elements.
const $sendMessage = document.getElementById('send-message') || undefined;
const $sendMessageInput = $sendMessage && document.querySelector('input');
const $sendMessageButton = $sendMessage && $sendMessage.querySelector('button');
const $messages = document.getElementById('messages') || undefined;

// Helper functions.

/*
* Position messages at the end of the messages area only if user
* is not seeing previous messages.
* @param {boolean} pageLoad - If set to true scroll to the the most recent message.
*/
const autoscroll = (pageLoad = false) => {
    // On page load, autoscroll to the last message.
    if (pageLoad) {
        $messages.scrollTop = $messages.scrollHeight;
        return;
    }

    const $newMessage = $messages.lastElementChild;
    if (!$newMessage) return;

    // Height of the new message.
    const newMessageHeight = $newMessage.offsetHeight;

    // Visible height of messages area.
    const visibleHeight = $messages.offsetHeight;

    // Real height of messages area.
    const containerHeight = $messages.scrollHeight;

    const scrollOffset = $messages.scrollTop + visibleHeight;

    if ((containerHeight - scrollOffset) <= newMessageHeight) {
        $messages.scrollTop = containerHeight;
    }
};

/*
* Render an individual message on the page.
* @param {Object} message - Message to be rendered.
*/
const renderMessage = (message) => {
    // Message template.
    const messageTemplate = document.getElementById('message-template').innerHTML || undefined;

    const html = Mustache.render(messageTemplate, message);

    $messages.insertAdjacentHTML('beforeend', html);
    autoscroll();
};

/*
* Send a message to the chat.
* @param {string} message - Message to be sent.
*/
const sendMessage = (message) => {
    // Disable send button while sending the message.
    $sendMessageButton.setAttribute('disabled', 'disabled');

    socket.emit('message', message, () => {
        // Enable send button.
        $sendMessageButton.removeAttribute('disabled');
    });
};

/*
* Send stock message to bot.
* @param {string} message - Stock code.
*/
const sendStockMessage = (message) => {
    socket.emit('stock message', message);
};

// Listeners.
if ($sendMessage !== undefined) {
    $sendMessage.addEventListener('submit', (e) => {
        e.preventDefault();

        const message = e.target.elements.message.value;
        if (!message) {
            $sendMessageInput.focus();
            return;
        };

        // Stock message regex.
        const stockRegex = /^(\/)([a-z]+)(=)?(.*)?$/;
        const match = message.match(stockRegex);
        if (match) {
            const command = match[2];
            if (command !== undefined && command === 'stock') {
                const stockCode = match[4];
                if (stockCode != undefined) {
                    sendStockMessage(stockCode);
                }
            }
        } else {
            sendMessage(message);
        }

        // Clear send message input.
        $sendMessageInput.value = '';
        $sendMessageInput.focus();
    });

    // Go to the last message in history.
    autoscroll(true);
}

// WebSocket events.
socket.on('message received', (message) => {
    renderMessage({ ...message, 'timestamp': moment.utc(message.timestamp).local().calendar() });
});