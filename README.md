# MOSDAC
# 🚀 MOSDAC Space Knowledge Explorer

**Explore the cosmos of data. Extract hidden relationships. Visualize space knowledge like never before.**  
Built with 🛰️ NLP + 🌌 Graphs + 🤖 Agentic AI (Groq + Firecrawl).

![Space Theme Banner](https://img.shields.io/badge/Streamlit-1.33.0-red?style=for-the-badge) ![spaCy](https://img.shields.io/badge/spaCy-NLP-blueviolet?style=for-the-badge) ![NetworkX](https://img.shields.io/badge/Graph%20viz-NetworkX-orange?style=for-the-badge) ![Groq AI](https://img.shields.io/badge/Agentic%20AI-Groq-green?style=for-the-badge)  

---

## 🌠 About the Project

**MOSDAC Space Knowledge Explorer** is a visual AI-powered tool that lets you:
- 🧠 Extract entities and relationships from space-related documents or MOSDAC web pages
- 🌐 Use **Firecrawl** + **Groq LLM** for deep web analysis
- 🌌 Visualize entity relationships as beautiful **space-themed graphs**
- 💬 Ask questions about your extracted knowledge or live web content

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **NLP**: spaCy (`en_core_web_sm`)
- **Graph Visuals**: NetworkX + Matplotlib
- **Agentic AI**: [Agno Framework](https://github.com/agnos-ai/agno)
- **Web Intelligence**: Firecrawl Tools + Groq's LLaMA3

---

## ⚙️ Installation

1. **Clone the repo**
```bash
git clone https://github.com/yourusername/mosdac-space-explorer.git
cd mosdac-space-explorer
Create a virtual environment

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Download spaCy model

bash
Copy
Edit
python -m spacy download en_core_web_sm
Configure .env

bash
Copy
Edit
# .env file
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
Run the Streamlit app

bash
Copy
Edit
streamlit run app.py
