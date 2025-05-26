// ui.js

// ==============================
// FUNCTION SETTING VIEW HEIGHT ?
// ==============================
export function setVh() {
  const vh = window.innerHeight * 0.01;
  document.documentElement.style.setProperty('--vh', `${vh}px`);
}


export function scrollToBottom() {
  const chatbox = document.getElementById('chat-messages');
  if (chatbox) chatbox.scrollTop = chatbox.scrollHeight;
}

export function toggleInput(state) {
  const inputField = document.getElementById('chat-input');
  const sendButton = document.getElementById('send-button');
  inputField.disabled = !state;
  sendButton.disabled = !state;
  if (state) inputField.focus();
}

export function createLoadingBubble() {
  const loading = document.createElement('div');
  loading.className = "typing-indicator message-animate";
  loading.innerHTML = `
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>`;
  return loading;
}

export function appendUserMessage(msg) {
  const chatbox = document.getElementById('chat-messages');
  const bubble = document.createElement('div');
  bubble.className = "chat-bubble user message-animate";
  bubble.innerText = msg;
  chatbox.appendChild(bubble);
  scrollToBottom();
}

export function appendBotMessage(markdownText) {
  const chatbox = document.getElementById('chat-messages');
  const blocks = markdownText.trim().split(/\n{2,}/);

  blocks.forEach(block => {
    const botMessage = document.createElement("div");
    botMessage.className = "bot-message text-left my-2 p-4 rounded-lg bg-gray-100 max-w-none";

    const html = marked.parse(block);
    const wrapper = document.createElement("div");
    wrapper.className = "prose prose-sm max-w-none";
    wrapper.innerHTML = html;

    botMessage.appendChild(wrapper);
    chatbox.appendChild(botMessage);
  });

  scrollToBottom();
}

export function appendBotMessageHTML(htmlContent) {
  const chatbox = document.getElementById('chat-messages');
  const bubble = document.createElement('div');
  bubble.className = "chat-bubble bot message-animate";
  bubble.innerHTML = htmlContent;
  chatbox.appendChild(bubble);
  scrollToBottom();
}

export function appendErrorMessage(msg) {
  const chatbox = document.getElementById('chat-messages');
  const bubble = document.createElement('div');
  bubble.className = "chat-bubble bot bg-red-50 text-red-600 border border-red-200 message-animate";
  bubble.innerText = msg;
  chatbox.appendChild(bubble);
  scrollToBottom();
}
