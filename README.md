# ✈️ Flight Sniper – AI-Powered Flight Deals Chatbot

<p align="center">
  <img src="./storage/snapshot.png" alt="Flight Sniper Demo" width="600" style="margin-top: 30px; margin-bottom: 30px;" />
</p>



Welcome to **Flight Sniper** — a conversational AI assistant that helps users find the cheapest flights based on their destination, travel dates, and budget.  
It’s powered by GPT-4, understands natural language, and performs real-time flight searches using structured scraping logic.

---

## 🧠 What It Does

- ✅ Conversational interface (natural language queries)
- ✅ Step-by-step intent extraction (destination, dates, trip type, etc.)
- ✅ Smart support for flexible or fixed dates
- ✅ Flight price formatting with Markdown & emojis ✨
- ✅ Built-in session handling (Firestore or local)
- ✅ Fully dockerized and deployable

---

## 🖼️ Demo Use Cases

```
"Find me a cheap round trip from Paris to Tokyo in August"
"I'm on vacation between June 10 and 20, leaving from Madrid. Any good return flights to Lisbon?"
"Show me one-way flights to Barcelona in early July for under €100"
```
<p align="center">
  <img src="./storage/snapshot2.png" alt="Flight Sniper Demo" width="400" style="margin-top: 30px; margin-bottom: 30px;" />
</p>

---

## 🤔 Why I Built This

I wanted to build a real-world, production-quality AI assistant that combines LLMs with live data retrieval, intent orchestration, and a usable frontend. This project reflects my skills in NLP, APIs, UX, and deployment.
It is also very useful for people that are not very good with going all around skyscanner or google flights to find the best combinations of flights. So it has real value to many users in the world.

---

## 🧱 Project Structure

```
[plaintext]


app/
│
├── backend/
│   ├── main.py                         # Starts FastAPI app, serves static files, registers routes
│   ├── config.json                     # Global settings (LLM model, system prompt, feature flags)
│
│   ├── api/
│   │   └── chat_api.py                 # Entry point: receives user query, returns LLM response
│
│   ├── core/
│   │   ├── config.py                   # get_config_value(), constants
│   │   ├── llm_client.py               # LLM API client: payload builders + completion
│   │   ├── llm_parser.py               # Handles [change] + [Do_Search] extraction from LLM response
│   │   └── flight_engine.py            # Chooses which flight search method to use based on intent
│
│   ├── flights/
│   │   ├── search_functions.py         # Actual scraping logic: get_one_way(), get_round_trip(), etc.
│   │   └── formatters.py               # Formats search results as nice LLM text

│
│   ├── services/
│   │   ├── local_session_service.py    # Load/save session with intent_state, chat history
│   │   └── intent_service.py           # update_intent_object(), normalize intent fields
│
│   ├── utils/
│   │   ├── logger.py                   # Logging setup
│   │   └── utils.py                    # Generic helpers (e.g. load/save JSON, date utilities)
│
├── frontend/
│   ├── index.html                      # Chat interface
│   └── static/
│       ├── fonts/
│       ├── icons/
│       └── js/
│
├── data/                               # Preprocessed data or static assets
├── storage/                            # Session JSONs, maybe cached search results
│   └── sessions/
│
├── Dockerfile
├── .dockerignore
├── .gitignore
├── CLI_test.py                         # CLI interface for testing flows
├── DevNotes.md                         # Architecture decisions and planning notes
├── readme.md
└── requirements.txt


```
---

## ⚙️ How It Works

1. User sends a message via the frontend  
2. Message is added to session history  
3. GPT-4 is called to guide the conversation and decide whether to search  
4. If user confirms, `[Do_Search]` is detected → flight scraper is triggered  
5. Results are beautified via LLM and returned to the user in Markdown  

---

## 🔧 Run It Locally

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/flight-sniper.git
cd flight-sniper

# 2. Install Python packages
pip install -r requirements.txt

# 3. Set your OpenAI key
echo "OPENAI_API_KEY=sk-..." > .env

# 4. Choose Between SpotFire session storage or Local 
from app.backend.services.firestore_session_service import load_or_create_session, save_session
or from app.backend.services.local_session_service import load_or_create_session, save_session

# 5. Run FastAPI server
uvicorn app.backend.main:app --reload
```

Then open `localhost:8000` to chat.

---

## 🐳 Docker Setup

```bash
docker build -t flight-sniper .
docker run -p 8000:8000 flight-sniper
```

---

## ☁️ Deployment Tips

- 🔐 Restrict CORS origins in production  
- 🔄 Use Firestore for persistent sessions  
- 🌍 Host frontend + backend via Azure, AWS or GCP ..   

---

## 📌 Tech Stack

- **FastAPI** – API backend  
- **OpenAI GPT-4.0 / 4.1** – LLM engine  
- **Firestore / JSON** – Session memory  
- **fast_flights** – Flight scraping logic  
- **Docker** – Deployment-ready containerization  

---

## 📣 Author

Made with ❤️ by [Amine Benkirane](https://www.linkedin.com/in/aminebenkirane-ml)  
<sub>PS: The emoji formatting is intentional. Yes, I take cheap flights seriously.</sub>

---

## 🚀 Next Ideas

- Destination suggestions if user is flexible  
- Add hotel or visa info scraping  
- Chat history viewer for admins  