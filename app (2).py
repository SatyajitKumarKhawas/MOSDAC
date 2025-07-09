import streamlit as st
import requests
import re
import spacy
import networkx as nx
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from io import StringIO
from collections import defaultdict
from matplotlib import rcParams
import matplotlib.colors as mcolors
from dotenv import load_dotenv
import os
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.firecrawl import FirecrawlTools

# Load environment variables
load_dotenv()
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Space Theme Configuration
st.set_page_config(
    page_title="🚀 MOSDAC Space Knowledge Explorer", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Space Theme
st.markdown("""
<style>
    /* Main background */
    .main {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
        color: #ffffff;
    }
    
    /* Sidebar space theme */
    .css-1d391kg {
        background: linear-gradient(180deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Title styling */
    .main-title {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(45deg, #00d4ff, #ff00ff, #ffff00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
        margin-bottom: 2rem;
    }
    
    /* Subtitle styling */
    .subtitle {
        text-align: center;
        color: #b0b0b0;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        color: white;
        border: none;
        border-radius: 25px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.5);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 15px;
        padding: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        margin: 5px;
        color: #ffffff;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #00d4ff, #ff00ff);
        color: white;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(0, 212, 255, 0.3);
        border-radius: 15px;
        color: white;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00d4ff;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 15px;
        border: 1px solid rgba(0, 212, 255, 0.2);
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        border: 2px dashed rgba(0, 212, 255, 0.3);
    }
    
    /* Success/Info messages */
    .stAlert {
        background: rgba(0, 212, 255, 0.1);
        border-radius: 15px;
        border-left: 4px solid #00d4ff;
    }
    
    /* Spinner styling */
    .stSpinner {
        color: #00d4ff;
    }
    
    /* Metric styling */
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(0, 212, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    
    /* Chat message styling */
    .chat-message {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #00d4ff;
        backdrop-filter: blur(10px);
    }
    
    .user-message {
        background: rgba(0, 212, 255, 0.1);
        border-left: 4px solid #00d4ff;
    }
    
    .bot-message {
        background: rgba(255, 0, 255, 0.1);
        border-left: 4px solid #ff00ff;
    }
    
    .url-message {
        background: rgba(0, 255, 0, 0.1);
        border-left: 4px solid #00ff00;
    }
    
    /* Floating particles animation */
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    .particle {
        position: fixed;
        width: 4px;
        height: 4px;
        background: #00d4ff;
        border-radius: 50%;
        animation: float 6s ease-in-out infinite;
        opacity: 0.6;
        z-index: -1;
    }
</style>
""", unsafe_allow_html=True)

# Add floating particles
particles_html = """
<div class="particle" style="top: 10%; left: 20%; animation-delay: 0s;"></div>
<div class="particle" style="top: 30%; left: 80%; animation-delay: 1s;"></div>
<div class="particle" style="top: 70%; left: 10%; animation-delay: 2s;"></div>
<div class="particle" style="top: 50%; left: 50%; animation-delay: 3s;"></div>
<div class="particle" style="top: 80%; left: 70%; animation-delay: 4s;"></div>
<div class="particle" style="top: 20%; left: 60%; animation-delay: 5s;"></div>
"""
st.markdown(particles_html, unsafe_allow_html=True)

# Main title with space theme
st.markdown('<h1 class="main-title">🚀 MOSDAC Space Knowledge Explorer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">🌌 Navigate through the cosmos of knowledge • Extract relationships from the data universe</p>', unsafe_allow_html=True)

# --------- Functions --------- #
def clean_text(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-zA-Z0-9.,:;\-\s]", "", text)
    return text

def extract_entities_relations(text):
    doc = nlp(text)
    entity_pairs = []
    triples = []
    for sent in doc.sents:
        ent_text = [ent.text.strip() for ent in sent.ents if ent.label_ in ("ORG", "PERSON", "GPE", "LOC", "PRODUCT", "EVENT")]
        for i in range(len(ent_text)):
            for j in range(i+1, len(ent_text)):
                entity_pairs.append((ent_text[i], ent_text[j]))

        root = [t for t in sent if t.dep_ == "ROOT"]
        if root:
            verb = root[0]
            subj = [w.text for w in verb.lefts if w.dep_ in ("nsubj", "nsubjpass")]
            obj = [w.text for w in verb.rights if w.dep_ in ("dobj", "pobj", "attr")]
            if subj and obj:
                triples.append((subj[0], verb.lemma_, obj[0]))

    return list(set(entity_pairs)), list(set(triples))

def build_graph(entity_pairs, triples):
    G = nx.DiGraph()
    for a, b in entity_pairs:
        G.add_node(a)
        G.add_node(b)
        G.add_edge(a, b, label="related")
    for a, rel, b in triples:
        G.add_node(a)
        G.add_node(b)
        G.add_edge(a, b, label=rel)
    return G

def draw_space_graph(G):
    # Professional dashboard-style graph visualization
    plt.style.use('default')
    rcParams["figure.figsize"] = 16, 10
    
    fig, ax = plt.subplots(facecolor='#f8f9fa')
    ax.set_facecolor('#f8f9fa')
    
    # Use a more spread out layout
    pos = nx.spring_layout(G, k=2, iterations=100, seed=42)
    edge_labels = nx.get_edge_attributes(G, 'label')
    
    # Professional color palette similar to the dashboard
    entity_colors = {
        'SATELLITE': '#4A90E2',    # Blue for satellites
        'LOCATION': '#F5A623',     # Orange for locations  
        'OCEAN': '#7ED321',        # Green for ocean-related
        'WEATHER': '#BD10E0',      # Purple for weather
        'TEMPERATURE': '#FF6B6B',  # Red for temperature
        'DEFAULT': '#50E3C2'       # Teal for others
    }
    
    # Categorize nodes based on keywords
    def get_node_color(node_name):
        node_lower = node_name.lower()
        if any(word in node_lower for word in ['satellite', 'insat', 'scatsat', 'oceansat']):
            return entity_colors['SATELLITE']
        elif any(word in node_lower for word in ['ocean', 'sea', 'bay', 'arabian']):
            return entity_colors['OCEAN']
        elif any(word in node_lower for word in ['temperature', 'data']):
            return entity_colors['TEMPERATURE']
        elif any(word in node_lower for word in ['weather', 'wind', 'forecast']):
            return entity_colors['WEATHER']
        elif any(word in node_lower for word in ['bengal', 'indian', 'coast']):
            return entity_colors['LOCATION']
        else:
            return entity_colors['DEFAULT']
    
    # Create node colors
    node_colors = [get_node_color(node) for node in G.nodes()]
    
    # Draw nodes with professional styling
    nx.draw_networkx_nodes(G, pos, 
                          node_color=node_colors,
                          node_size=1500, 
                          alpha=0.9, 
                          linewidths=2,
                          edgecolors='white',
                          ax=ax)
    
    # Add subtle glow effect
    nx.draw_networkx_nodes(G, pos, 
                          node_color=node_colors,
                          node_size=1800, 
                          alpha=0.3, 
                          ax=ax)
    
    # Draw labels with better positioning
    labels = {}
    for node in G.nodes():
        # Truncate long labels
        if len(node) > 15:
            labels[node] = node[:12] + "..."
        else:
            labels[node] = node
    
    nx.draw_networkx_labels(G, pos, 
                           labels=labels,
                           font_size=9, 
                           font_color="#2c3e50", 
                           font_weight="bold",
                           ax=ax)
    
    # Draw edges with professional styling
    nx.draw_networkx_edges(G, pos, 
                          edge_color="#bdc3c7", 
                          width=1.5, 
                          alpha=0.6,
                          ax=ax)
    
    # Draw edge labels with better styling
    if edge_labels:
        # Filter out generic labels
        filtered_labels = {k: v for k, v in edge_labels.items() if v not in ['related', 'be', 'have']}
        if filtered_labels:
            nx.draw_networkx_edge_labels(G, pos, 
                                       edge_labels=filtered_labels, 
                                       font_color="#34495e", 
                                       font_size=7,
                                       bbox=dict(boxstyle="round,pad=0.2", 
                                               facecolor="white", 
                                               edgecolor="#bdc3c7", 
                                               alpha=0.8),
                                       ax=ax)
    
    # Add title and clean up
    ax.set_title("🌌 Knowledge Graph - Entity Relationships", 
                color="#2c3e50", fontsize=14, fontweight="bold", pad=20)
    ax.axis('off')
    
    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', 
                  markerfacecolor=entity_colors['SATELLITE'], markersize=10, 
                  label='Satellites'),
        plt.Line2D([0], [0], marker='o', color='w', 
                  markerfacecolor=entity_colors['OCEAN'], markersize=10, 
                  label='Ocean/Sea'),
        plt.Line2D([0], [0], marker='o', color='w', 
                  markerfacecolor=entity_colors['LOCATION'], markersize=10, 
                  label='Locations'),
        plt.Line2D([0], [0], marker='o', color='w', 
                  markerfacecolor=entity_colors['WEATHER'], markersize=10, 
                  label='Weather'),
        plt.Line2D([0], [0], marker='o', color='w', 
                  markerfacecolor=entity_colors['TEMPERATURE'], markersize=10, 
                  label='Temperature/Data'),
        plt.Line2D([0], [0], marker='o', color='w', 
                  markerfacecolor=entity_colors['DEFAULT'], markersize=10, 
                  label='Other')
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', 
             bbox_to_anchor=(1.0, 1.0), frameon=True, 
             fancybox=True, shadow=True, ncol=1)
    
    plt.tight_layout()
    st.pyplot(fig)

def firecrawl_web_search(query, url=None):
    """Simple Firecrawl-powered web search and analysis"""
    try:
        if not FIRECRAWL_API_KEY:
            return "🚨 Firecrawl API key not configured. Please set FIRECRAWL_API_KEY in your environment."
        
        firecrawl_agent = Agent(
            name="CosmicFirecrawlAgent",
            model=Groq("llama3-8b-8192"),
            tools=[FirecrawlTools(api_key=FIRECRAWL_API_KEY)]
        )
        
        if url:
            firecrawl_query = f"Extract and analyze information from {url} related to: {query}"
        else:
            firecrawl_query = f"Search the web and analyze information about: {query}"
        
        output = firecrawl_agent.run(firecrawl_query)
        return output.content
    except Exception as e:
        return f"🚨 Deep space probe encountered an anomaly: {str(e)}"

# --------- Streamlit UI --------- #
st.markdown("### 🛸 Mission Control Panel")
st.markdown("*Launch your exploration by uploading cosmic data or entering a stellar URL*")

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_triples' not in st.session_state:
    st.session_state.current_triples = []

tabs = st.tabs(["🌌 Knowledge Constellation", "💬 Cosmic Chat & Firecrawl"])

with tabs[0]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        option = st.radio("🛰️ Select Data Source:", ["📡 Upload Cosmic Data", "🌐 Stellar URL Probe"], horizontal=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>🌟 Mission Status</h4>
            <p>Ready for Knowledge Discovery</p>
        </div>
        """, unsafe_allow_html=True)

    raw_text = ""

    if option == "📡 Upload Cosmic Data":
        st.markdown("### 🛸 Data Upload Bay")
        file = st.file_uploader("Drop your cosmic data files here", type=["txt", "html"], help="Upload HTML or text files from MOSDAC")
        if file:
            stringio = StringIO(file.getvalue().decode("utf-8"))
            raw_text = stringio.read()
            st.success("🎯 Cosmic data successfully captured!")

    elif option == "🌐 Stellar URL Probe":
        st.markdown("### 🔭 Deep Space URL Scanner")
        url = st.text_input("🌍 Enter cosmic coordinates (URL)", "https://www.mosdac.gov.in", help="Enter a MOSDAC URL to explore")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            fetch_clicked = st.button("🚀 Launch Probe", use_container_width=True)

        if url and fetch_clicked:
            try:
                with st.spinner("🛰️ Probe scanning deep space..."):
                    headers = {"User-Agent": "Mozilla/5.0 (Space-Explorer/1.0)"}
                    response = requests.get(url, headers=headers, timeout=10)
                    
                if response.status_code == 200:
                    raw_text = clean_text(response.text)

                    st.markdown("### 🔍 Cosmic Data Intercepted")
                    with st.expander("📊 View Raw Cosmic Data (First 500 words)", expanded=False):
                        st.markdown(f"""
                        <div class="chat-message">
                        {" ".join(raw_text.split()[:500])}...
                        </div>
                        """, unsafe_allow_html=True)

                    with st.spinner("🧬 Analyzing cosmic patterns and relationships..."):
                        pairs, triples = extract_entities_relations(raw_text)
                        st.session_state.current_triples = triples
                        
                        # Display metrics in space theme
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3>🌟 {len(pairs)}</h3>
                                <p>Entity Pairs Discovered</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3>🔗 {len(triples)}</h3>
                                <p>Relationship Triples</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3>📡 {len(set([s for s, r, o in triples] + [o for s, r, o in triples]))}</h3>
                                <p>Unique Entities</p>
                            </div>
                            """, unsafe_allow_html=True)

                        if pairs or triples:
                            st.markdown("### 🌌 Knowledge Constellation Visualization")
                            G = build_graph(pairs, triples)
                            draw_space_graph(G)

                        if triples:
                            st.markdown("### 🔮 Cosmic Relationship Patterns")
                            with st.expander("🌟 Explore Discovered Relationships", expanded=True):
                                for i, (s, r, o) in enumerate(triples[:10]):
                                    st.markdown(f"""
                                    <div class="chat-message">
                                        <strong>🌠 {s}</strong> — <em style="color: #00d4ff;">{r}</em> → <strong>🌟 {o}</strong>
                                    </div>
                                    """, unsafe_allow_html=True)
                else:
                    st.error("🚨 Probe failed to establish connection with target coordinates")
            except Exception as e:
                st.error(f"🚨 Space-time anomaly detected: {str(e)}")

    # File upload processing
    if option == "📡 Upload Cosmic Data" and raw_text:
        cleaned_text = clean_text(raw_text)
        st.markdown("### 🔍 Cosmic Data Analysis")
        
        with st.expander("📊 View Processed Cosmic Data", expanded=False):
            st.markdown(f"""
            <div class="chat-message">
            {" ".join(cleaned_text.split()[:500])}...
            </div>
            """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🧬 Analyze Cosmic Patterns", use_container_width=True):
                with st.spinner("🔬 Scanning for cosmic relationships..."):
                    pairs, triples = extract_entities_relations(cleaned_text)
                    st.session_state.current_triples = triples
                    
                    # Display metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>🌟 {len(pairs)}</h3>
                            <p>Entity Pairs</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>🔗 {len(triples)}</h3>
                            <p>Relationships</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>📡 {len(set([s for s, r, o in triples] + [o for s, r, o in triples]))}</h3>
                            <p>Unique Entities</p>
                        </div>
                        """, unsafe_allow_html=True)

                    if pairs or triples:
                        st.markdown("### 🌌 Knowledge Constellation Map")
                        G = build_graph(pairs, triples)
                        draw_space_graph(G)

                    if triples:
                        st.markdown("### 🔮 Discovered Relationships")
                        for s, r, o in triples[:10]:
                            st.markdown(f"""
                            <div class="chat-message">
                                <strong>🌠 {s}</strong> — <em style="color: #00d4ff;">{r}</em> → <strong>🌟 {o}</strong>
                            </div>
                            """, unsafe_allow_html=True)

# --------- Enhanced Cosmic Chat Tab with Firecrawl --------- #
with tabs[1]:
    st.markdown("### 💬 Cosmic Knowledge Assistant & Firecrawl Probe")
    st.markdown("*Ask questions about your explored cosmic data or search the web with Firecrawl*")
    
    # Chat mode selection
    col1, col2 = st.columns([3, 1])
    with col1:
        chat_mode = st.radio("🔮 Choose Chat Mode:", 
                           ["🧠 Knowledge Base Chat", "🚀 Firecrawl Web Search", "🌐 Firecrawl URL Analysis"], 
                           horizontal=True)
    
    with col2:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    # URL input for Firecrawl URL Analysis mode
    firecrawl_url = ""
    if chat_mode == "🌐 Firecrawl URL Analysis":
        firecrawl_url = st.text_input("🌍 Enter URL to analyze:", value="https://www.mosdac.gov.in")
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 📚 Cosmic Conversation Log")
        for i, (role, message, msg_type) in enumerate(st.session_state.chat_history):
            if role == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>🧑‍🚀 You:</strong> {message}
                </div>
                """, unsafe_allow_html=True)
            elif msg_type == "url":
                st.markdown(f"""
                <div class="chat-message url-message">
                    <strong>🌐 Firecrawl Analysis:</strong> {message}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>🤖 Cosmic AI:</strong> {message}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    if chat_mode == "🧠 Knowledge Base Chat":
        placeholder_text = "e.g., What satellites are mentioned? How are they related to ISRO?"
    elif chat_mode == "🚀 Firecrawl Web Search":
        placeholder_text = "e.g., Latest ISRO missions, Ocean satellite data analysis"
    else:
        placeholder_text = "e.g., What information is available on this website?"
    
    user_query = st.text_input("🗣️ Ask the cosmic knowledge assistant:", 
                              placeholder=placeholder_text)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🚀 Send Message", use_container_width=True):
            if user_query:
                # Add user message to chat history
                st.session_state.chat_history.append(("user", user_query, "user"))
                
                if chat_mode == "🧠 Knowledge Base Chat":
                    # Original knowledge base functionality
                    if st.session_state.current_triples:
                        with st.spinner("🔍 Scanning cosmic knowledge database..."):
                            answers = []
                            for s, r, o in st.session_state.current_triples:
                                q = user_query.lower()
                                if s.lower() in q or o.lower() in q or r.lower() in q:
                                    answers.append(f"🌠 **{s}** — *{r}* → **{o}**")

                            if answers:
                                response = f"🧠 Found {len(answers)} cosmic connections:\n\n" + "\n".join(answers[:5])
                                if len(answers) > 5:
                                    response += f"\n\n*...and {len(answers) - 5} more connections in the cosmic database*"
                            else:
                                response = "🌌 No direct matches found in the current cosmic knowledge base. Try exploring different cosmic coordinates or rephrasing your query."
                            
                            st.session_state.chat_history.append(("bot", response, "bot"))
                    else:
                        response = "🚨 Please first explore some cosmic data in the Knowledge Constellation tab!"
                        st.session_state.chat_history.append(("bot", response, "bot"))
                
                elif chat_mode == "🚀 Firecrawl Web Search":
                    # Firecrawl web search
                    with st.spinner("🛰️ Firecrawl probe searching the cosmic web..."):
                        response = firecrawl_web_search(user_query)
                        st.session_state.chat_history.append(("bot", response, "url"))
                
                elif chat_mode == "🌐 Firecrawl URL Analysis":
                    # Firecrawl URL analysis
                    if firecrawl_url:
                        with st.spinner("🔍 Firecrawl probe analyzing cosmic coordinates..."):
                            response = firecrawl_web_search(user_query, firecrawl_url)
                            st.session_state.chat_history.append(("bot", response, "url"))
                    else:
                        response = "🚨 Please enter a URL to analyze!"
                        st.session_state.chat_history.append(("bot", response, "bot"))
                
                # Rerun to show new messages