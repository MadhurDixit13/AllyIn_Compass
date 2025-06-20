# 🧭 My Compass

**My Compass** is a full-stack, multi-tool AI assistant that answers enterprise queries by intelligently retrieving from structured databases, unstructured documents, and graph-based knowledge using Retrieval-Augmented Generation (RAG) and LangChain agents.

---

## 🚀 Features

- 🔍 **Tool-Routing Agent**: LangChain agent dynamically selects between SQL, Vector DB (Qdrant), and Graph DB (Neo4j)
- 📄 **Document Ingestion**: Supports CSV, PDF, and `.eml` email files via DuckDB and PyMuPDF
- 🧠 **RAG Pipeline**: Powered by Groq-hosted LLaMA3 for fast, grounded generation
- 🧪 **Simulated Fine-Tuning**: LoRA + PEFT applied to feedback data for adaptive learning
- 🖥️ **Streamlit UI**: Domain filters, confidence sliders, and answer visualization
- 📊 **Observability Dashboard**: Tracks query volumes, tool usage, and response times
- 🔐 **Compliance & PII Guardrails**: Email, SSN, phone detection + keyword flagging
- 👍 **Feedback Loop**: Thumbs up/down rating logs user sentiment

---

## 🧱 Tech Stack

- **LangChain**, **Qdrant**, **DuckDB**, **Neo4j**
- **Groq LLaMA3**, **SentenceTransformers**
- **Streamlit**, **PEFT**, **LoRA**
- **Python 3.10+**, **Docker**, **Postman**

---

## ⚙️ Setup Instructions

### 1. Clone the Repo
```bash
git clone https://github.com/MadhurDixit13/AllyIn_Compass.git
cd allyin-compass
```

### 2. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file:
```env
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=your_neo4j_database
GROQ_API_KEY=your_groq_api_key
```

---

## ▶️ Run the App

### Start Qdrant (in another terminal)
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Run the UI
```bash
streamlit run ui/app.py
```

---

## 📄 Example Queries

- **Orders**: “Which customers placed orders over $500?” (SQL)
- **Meetings**: “What time is the meeting?” (Vector)
- **Movies**: “Recommend me movies of Tom Hanks?” (Graph)

---

## 📽 Demo & Deck

- 🎥 [Demo Video](demo_assets/videos/demo.mp4)
<!-- - 📑 [Slide Deck](demo_assets/slide_deck.pdf) -->
- 📸 Screenshots: See `demo_assets/images/*.png`

---

## 🧠 Project Highlights

- Embedded over **100+ documents**
- Integrated **3 retrieval methods** (SQL, vector, graph)
- Logged **PII detection + feedback** for fine-tuning simulation
- Simulated adapter tuning with **PEFT + LoRA**

---

## 📜 License

MIT License

---

## 🙌 Acknowledgments

- Inspired by LangChain, Groq, HuggingFace, and the open-source AI community.
- Built as part of a 15-day development sprint to explore agentic RAG systems.

---

## 👤 Author

**Madhur Dixit**  
Connect on [LinkedIn](https://www.linkedin.com/in/madixit/) | GitHub: [@MadhurDixit13](https://github.com/MadhurDixit13)
