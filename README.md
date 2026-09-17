
<p align="center">
  <img src="https://img.shields.io/badge/LangGraph-Agent-blueviolet?style=for-the-badge&logo=chainlink&logoColor=white"/>
  <img src="https://img.shields.io/badge/Groq-Llama%203.3%2070B-orange?style=for-the-badge&logo=meta&logoColor=white"/>
  <img src="https://img.shields.io/badge/Google%20Drive-API-4285F4?style=for-the-badge&logo=googledrive&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
</p>

<h1 align="center">🗂️ TailorTalk Drive Agent</h1>

<p align="center">
  <b>A conversational AI agent that turns natural language into Google Drive file searches.</b><br/>
  Ask it anything about your Drive — it finds, filters, and surfaces exactly what you need.
</p>

---

## ✨ What It Does

**TailorTalk Drive Agent** is an agentic AI assistant that connects to a Google Drive folder and lets you search for files using plain English. Powered by a **LangGraph ReAct agent** and **Groq's Llama 3.3 70B**, it understands your intent and intelligently picks the right Drive API query — no regex, no manual filtering needed.

### Example queries you can ask:
```
"Find all PDFs in the drive"
"Show spreadsheets modified last week"
"Find documents about marketing budget"
"Invoice files from January 2024"
"What types of files are in the drive?"
"Find files containing the word 'salary'"
```

---

## 🏗️ Architecture

```
User (Streamlit UI)
        │
        ▼
  FastAPI Backend
        │
        ▼
  LangGraph Agent (ReAct loop)
        │
        ├── 🔍 search_drive_files   → Search by name, type, content, date
        ├── 📋 get_file_details     → Get deep metadata for a specific file
        └── 📊 list_drive_summary   → Show all file types & counts
        │
        ▼
  Google Drive API (Service Account)
```

The agent uses a **ReAct (Reason + Act)** loop — it reasons about the user's query, picks the right tool with the right parameters, gets the Drive results, and returns a formatted response with clickable links.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Groq — Llama 3.3 70B Versatile |
| **Agent Framework** | LangGraph (StateGraph + ToolNode) |
| **Backend** | FastAPI + Uvicorn |
| **Frontend** | Streamlit |
| **Drive Integration** | Google Drive API v3 (Service Account) |
| **LLM Client** | LangChain + langchain-groq |

---

## 📂 Project Structure

```
tailortalk-drive-agent/
├── backend/
│   ├── main.py                  # FastAPI app — /chat, /health endpoints
│   ├── config.py                # Pydantic settings (env vars)
│   ├── requirements.txt
│   ├── agent/
│   │   ├── graph.py             # LangGraph StateGraph definition
│   │   ├── nodes.py             # Agent node + tool binding (Llama 3.3 70B)
│   │   ├── prompts.py           # System prompt with intent-to-tool mapping
│   │   └── state.py             # AgentState TypedDict
│   ├── tools/
│   │   ├── drive_search.py      # search_drive_files tool
│   │   ├── drive_metadata.py    # get_file_details tool
│   │   └── drive_list_types.py  # list_drive_summary tool
│   ├── services/
│   │   ├── drive_client.py      # Google Drive API service builder
│   │   └── query_builder.py     # Drive query string constructor
│   └── models/
│       └── schemas.py           # ChatRequest / ChatResponse Pydantic models
└── frontend/
    ├── app.py                   # Streamlit entry point
    ├── components/
    │   ├── chat.py              # Chat UI component
    │   └── sidebar.py          # Sidebar (backend URL, Drive info)
    └── utils/
        └── api_client.py        # HTTP client to call FastAPI backend
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A Google Cloud project with the **Drive API** enabled
- A **Service Account** with access to your Drive folder
- A **Groq API key** (free at [console.groq.com](https://console.groq.com))

### 1. Clone the repository
```bash
git clone https://github.com/anshumanvatsa/Tailor-talk-drive-agent.git
cd Tailor-talk-drive-agent
```

### 2. Google Drive Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → Enable **Google Drive API**
3. Create a **Service Account** → Download the JSON key as `service_account.json` in the project root
4. Share your Drive folder with the service account email
5. Copy your Drive folder ID from the URL:  
   `https://drive.google.com/drive/folders/`**`<YOUR_FOLDER_ID>`**

### 3. Environment Variables
```bash
cp .env.example .env
```

Fill in your `.env`:
```env
GROQ_API_KEY=your_groq_api_key
DRIVE_FOLDER_ID=your_google_drive_folder_id
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}
BACKEND_URL=http://localhost:8000
```

### 4. Run the Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs available at: `http://localhost:8000/docs`

### 5. Run the Frontend
```bash
cd frontend
pip install streamlit python-dotenv requests
streamlit run app.py
```

---

## 🌐 Deployment

| Service | Config |
|---------|--------|
| **Backend** | Railway / Render — set env vars, run `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Frontend** | Streamlit Community Cloud — set `BACKEND_URL` to your deployed backend URL |

---

## 🔌 API Reference

### `POST /chat`
Send a message and conversation history to the agent.

```json
{
  "message": "Find all invoices from last month",
  "history": [
    { "role": "user", "content": "Hi" },
    { "role": "assistant", "content": "Hello! What are you looking for?" }
  ]
}
```

**Response:**
```json
{
  "response": "**Found 3 file(s):**\n📄 **[Invoice_Dec.pdf](...)** ...",
  "tools_used": ["search_drive_files"]
}
```

### `GET /health`
```json
{ "status": "ok", "agent": "tailortalk-drive-agent-v1", "model": "llama-3.3-70b-versatile" }
```

---

## 🧠 How the Agent Thinks

The agent uses a **LangGraph ReAct loop**:

1. **User sends a query** → e.g. "Find Excel files modified this week"
2. **LLM reasons** → decides to call `search_drive_files` with `file_type="sheet"`, `modified_after="this week"`
3. **Tool executes** → builds a Drive API query, fetches results
4. **LLM formats** → returns clickable file links with names, dates, sizes
5. **Agent invites refinement** → "Want me to filter further?"

---

## 📝 License

MIT License — feel free to use, modify, and build upon this.

---

<p align="center">Built by <a href="https://github.com/anshumanvatsa">@anshumanvatsa</a> &nbsp;|&nbsp; LangGraph + Groq + Google Drive API</p>