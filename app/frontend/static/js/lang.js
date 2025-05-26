// lang.js

// ==============================
// TRANSLATIONS DICT
// ==============================

export const translations = {
  en: {
    title: "Flight Sniper",
    subtitle: "Find the Cheapest Times to Fly",
    welcome: `Hey there! 👋\nWelcome to Flight Sniper.\nTell me where you're headed —\nand we’ll hunt down the best deal together. ✈️`,
    buttons: {
      oneway: "One Way Flight",
      roundtrip: "Return Flight",
      help: "Help"
    },
    responses: {
      oneway: [
        "Looking for cheap one-way flights on a specific day or within a date range?",
        "Start by telling me your <strong>origin</strong> and <strong>destination</strong> — let’s hunt down the best deals!"
      ],
      roundtrip: [
        "Looking for a cheap round trip? Got some flexibility on dates and stay duration?",
        "Just tell me your <strong>origin</strong> and <strong>destination</strong> — and let's find you the best combinations!"
      ],
      help: [
        "You can ask me things like:",
        "• One-way to Barcelona the first week of June",
        "• Round trip to Cagliari in July, stay 8 to 10 nights",
        "• Any cheap return flights from Madrid in August"
      ]
    }
  },

  fr: {
    title: "Flight Sniper",
    subtitle: "Trouvez les périodes les moins chères pour voyager",
    welcome: `Bonjour ! 👋\nBienvenue sur Flight Sniper.\nDites-moi où vous souhaitez partir  —\net on dénichera les meilleures offres ensemble. ✈️`,
    buttons: {
      oneway: "Aller Simple",
      roundtrip: "Aller-Retour",
      help: "Aide"
    },
    responses: {
      oneway: [
        "Vous cherchez un vol aller simple pas cher à une date précise ou sur une plage de dates ?",
        "Commencez par me donner votre <strong>ville de départ</strong> et votre <strong>destination</strong> — et on va dénicher les meilleures offres !"
      ],
      roundtrip: [
        "Vous cherchez un aller-retour pas cher ? Vous êtes un peu flexible sur les dates et la durée du séjour ?",
        "Dites-moi simplement votre <strong>ville de départ</strong> et votre <strong>destination</strong> — et on trouvera les meilleures combinaisons !"
      ],
      help: [
        "Vous pouvez me demander des choses comme :",
        "• 'Aller simple pour Barcelone la première semaine de juin'",
        "• 'Aller-retour pour Cagliari en juillet, séjour de 8 à 10 nuits'",
        "• 'Vols aller-retour pas chers depuis Madrid en août'"
      ]
    }
  }
};

// ==============================
// FUNCTION EDITINNG INNER HTML WITH INJECTIONS
// ==============================

export function initLanguageSettings() {
  const lang = localStorage.getItem('chatLang') || 'en';
  const t = translations[lang];

  document.querySelector('header h1').innerText = t.title;
  document.querySelector('header p').innerText = t.subtitle;

  const buttonMap = {
    'quick-btn-1': t.buttons.oneway,
    'quick-btn-2': t.buttons.roundtrip,
    'quick-btn-help': t.buttons.help
  };

  Object.entries(buttonMap).forEach(([id, text]) => {
    const btn = document.getElementById(id);
    if (btn) {
      const icon = btn.querySelector('i');
      btn.innerHTML = `${icon?.outerHTML || ''} ${text}`;
    }
  });
}


// ==============================
// FUNCTION FOR INTIAL LANGUAGE BUTTONS
// ==============================

export function initLanguageButtons() {
  const langButtons = {
    en: document.getElementById('lang-en'),
    fr: document.getElementById('lang-fr')
  };

  Object.entries(langButtons).forEach(([lang, btn]) => {
    if (btn) {
      btn.addEventListener('click', () => {
        localStorage.setItem('chatLang', lang);
        initLanguageSettings();
        displayWelcomeContent(); // make sure this is imported in main file
      });
    }
  });
}


// ==============================
// FUNCTION SHOWING INTO MESSAGE
// ==============================


export function displayIntroMessage(lang) {
  const msgEl = document.getElementById('intro-message');
  const titleEl = document.getElementById('intro-title');
  const buttonEl = document.getElementById('start-chat');

  const messages = {
    en: {
      title: 'Welcome to Flight Sniper',
      button: 'Start Chatting',
      body: `
        <p>✈️ <strong>How it works</strong></p>
        <p>Just chat with your AI assistant — describe your trip, and it finds the cheapest flights based on your flexibility.</p>
        <ul class="list-disc pl-5 space-y-1">
          <li>Search for the <strong>best one-way deals</strong> in a date range</li>
          <li>Find <strong>cheap round trips</strong> in a month or custom range, even with flexible stay durations</li>
        </ul>
        <p class="mt-2">The more flexible you are, the better the price.</p>
        <p class="mt-2"><em>Examples:</em><br>
        “One-way to Barcelona in the first week of June”<br>
        “Round trip to Cagliari in July, stay 8–10 nights”</p>`
    },

    fr: {
      title: 'Bienvenue sur Flight Sniper',
      button: 'Commencer la discussion',
      body: `
        <p>✈️ <strong>Comment ça marche</strong></p>
        <p>Parle simplement avec ton assistant — décris ton voyage, il trouve les vols les moins chers selon ta flexibilité.</p>
        <ul class="list-disc pl-5 space-y-1">
          <li>Cherche les <strong>meilleurs allers simples</strong> sur une plage de dates</li>
          <li>Trouve des <strong>allers-retours pas chers</strong> sur un mois ou une période, même avec durée de séjour flexible</li>
        </ul>
        <p class="mt-2">Plus tu es flexible, plus les prix seront bas.</p>
        <p class="mt-2"><em>Exemples :</em><br>
        « Aller simple pour Barcelone la première semaine de juin »<br>
        « Aller-retour pas cher pour Cagliari en juillet, séjour de 8 à 10 nuits »</p>`
    }
  };

  titleEl.textContent = messages[lang].title;
  buttonEl.textContent = messages[lang].button;
  msgEl.innerHTML = messages[lang].body;
}
