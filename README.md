# 🤖 TRIAGE.AI: Multi-Domain Support Triage Agent
### Created by **Viswas**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain)](https://www.langchain.com/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google-gemini&logoColor=white)](https://deepmind.google/technologies/gemini/)

**TRIAGE.AI** is a high-performance, agentic support system designed to automate ticket classification, information retrieval, and escalation across multiple domains. Built with a state-of-the-art tech stack including **LangGraph** for stateful workflows and **Google Gemini** for reasoning.

---

## ✨ Features

- 🎯 **Intelligent Triage**: Automatically classifies requests into domains (**HackerRank**, **Claude**, **Visa**) and categories (**Billing**, **Technical**, **Fraud**, etc.).
- 🧠 **Context-Aware Responses**: Uses **RAG (Retrieval-Augmented Generation)** with ChromaDB to provide accurate answers based on internal documentation.
- 🚀 **Automated Escalation**: High-risk issues or unknown queries are automatically logged into a structured CSV database with unique Ticket IDs.
- 🎙️ **Voice Integration**: Built-in voice input support using the Web Speech API for a seamless hands-free experience.
- 💎 **Premium UI**: A stunning, responsive glassmorphism interface with real-time feedback and smooth animations.
- 💾 **Persistent Memory**: Maintains conversation context and chat history across page refreshes using `localStorage` and server-side state tracking.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI
- **Orchestration**: LangGraph (Stateful Multi-step Workflows)
- **LLM**: Google Gemini (via `langchain-google-genai`)
- **Vector Store**: ChromaDB
- **Data Handling**: Pandas

### Frontend
- **Logic**: Vanilla JavaScript
- **Styling**: Vanilla CSS (Premium Glassmorphism Design)
- **Icons**: FontAwesome 6.4.0

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- A Google Gemini API Key ([Get one here](https://aistudio.google.com/))

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/viswaskasi/TRIAGE.AI.git
   cd TRIAGE.AI
   ```

2. **Set up the backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the `backend/` directory:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   PORT=8001
   ```

4. **Build the Vector Database (Optional but recommended):**
   ```bash
   python build_vector_db.py
   ```

### Running the App

1. **Start the server:**
   ```bash
   python -m uvicorn main:app --port 8001 --reload
   ```

2. **Access the UI:**
   Open your browser and navigate to `http://localhost:8001`

---

## 📂 Project Structure

```text
TRIAGE.AI/
├── backend/
│   ├── main.py            # FastAPI Application
│   ├── triage_engine.py   # LangGraph Logic & Agent Nodes
│   ├── tools.py           # Ticket Escalation Tools
│   └── .env               # Environment Config (ignored by git)
├── frontend/
│   ├── index.html         # Main UI
│   ├── style.css          # Premium Styling
│   └── script.js          # Client-side Logic
├── data/
│   └── chroma_db/         # Vector Database Storage
├── support_tickets/       # Logged Escalations (CSV)
└── README.md              # Project Documentation
```

---

## 📜 License
This project is for educational purposes. Feel free to use and modify it for your own needs.

---
*Built with ❤️ by **Viswas***
