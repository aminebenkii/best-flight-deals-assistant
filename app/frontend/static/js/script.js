// script.js

import { translations, initLanguageSettings, initLanguageButtons, displayIntroMessage } from './lang.js';
import {
  setVh,
  scrollToBottom,
  toggleInput,
  createLoadingBubble,
  appendUserMessage,
  appendBotMessage,
  appendBotMessageHTML
} from './ui.js';

function displayWelcomeContent() {
  const lang = localStorage.getItem('chatLang') || 'en';
  const welcomeText = translations[lang].welcome;
  const chatbox = document.getElementById('chat-messages');

  const exists = Array.from(chatbox.getElementsByClassName('chat-bubble'))
    .some(bubble => bubble.classList.contains('bot') && bubble.innerText.trim() === welcomeText);

  if (!exists) {
    appendBotMessageHTML(`<p>${welcomeText.replace(/\n/g, "<br>")}</p>`);
  }
}

function handleSuggestion(category) {
  const lang = localStorage.getItem('chatLang') || 'en';
  const t = translations[lang];
  const chatbox = document.getElementById('chat-messages');

  const userMessage = t.buttons[category];
  const assistantLines = t.responses[category];

  appendUserMessage(userMessage);

  const loadingBubble = createLoadingBubble();
  chatbox.appendChild(loadingBubble);
  scrollToBottom();

  setTimeout(() => {
    chatbox.removeChild(loadingBubble);

    let html = "<div>";
    assistantLines.forEach(line => {
      if (line.startsWith("•")) {
        html += `<p style="margin-left: 1em">• ${line.slice(1).trim()}</p>`;
      } else {
        html += `<p>${line}</p>`;
    }
    });
    html += "</div>";

    appendBotMessageHTML(html);
  }, 1000);
}

// Attach quick suggestion buttons
[
  ['quick-btn-1', 'oneway'],
  ['quick-btn-2', 'roundtrip'],
  ['quick-btn-help', 'help']
].forEach(([id, category]) => {
  const btn = document.getElementById(id);
  if (btn) {
    btn.addEventListener('click', () => handleSuggestion(category));
  }
});

// Main screen flow
window.addEventListener('DOMContentLoaded', () => {
  setVh();
  window.addEventListener('resize', setVh);
  window.addEventListener('orientationchange', setVh);

  const langButtons = {
    en: document.getElementById('choose-en'),
    fr: document.getElementById('choose-fr')
  };

  langButtons.en?.addEventListener('click', () => {
    localStorage.setItem('chatLang', 'en');
    showIntroScreen();
  });

  langButtons.fr?.addEventListener('click', () => {
    localStorage.setItem('chatLang', 'fr');
    showIntroScreen();
  });

  document.getElementById('start-chat')?.addEventListener('click', () => {
    document.getElementById('intro-screen').classList.add('hidden');
    document.getElementById('chatbot-screen').classList.remove('hidden');

    initLanguageSettings();
    initLanguageButtons();
    displayWelcomeContent();
    toggleInput(true);
  });
});

function showIntroScreen() {
  const lang = localStorage.getItem('chatLang') || 'en';

  document.getElementById('language-screen').classList.add('hidden');
  document.getElementById('intro-screen').classList.remove('hidden');

  displayIntroMessage(lang);
}
