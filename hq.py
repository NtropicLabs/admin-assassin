import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import pandas as pd

# ==========================================
# 1. UI OVERHAUL (Custom CSS Injection)
# ==========================================
st.set_page_config(page_title="Neural Forge", page_icon="⬛", layout="wide")

# Injecting 'Inter' font and modern minimal styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Global Typography */
    html, body, [class*="css"], .stMarkdown, .stText {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Clean up Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Typography Classes */
    .title-text {
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.05em;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .subtitle-text {
        font-size: 1rem;
        font-weight: 400;
        color: #666666;
        letter-spacing: 0.02em;
        margin-top: 0px;
        margin-bottom: 2rem;
    }
    .meta-text {
        font-size: 0.8rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #888888;
    }
    .bounty-title {
        font-size: 1.25rem;
        font-weight: 600;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }
    
    /* Sleek Metrics */
    [data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.03em;
    }
    [data-testid="stMetricLabel"] {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #888888;
    }

    /* Minimalist Button Override */
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        letter-spacing: 0.02em;
        transition: all 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATABASE SETUP
# ==========================================
conn = sqlite3.connect('neural_forge.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS bounties 
             (id INTEGER PRIMARY KEY, title TEXT, category TEXT, true_deadline TEXT, panic_deadline TEXT, xp INTEGER, status TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS user_stats 
             (id INTEGER PRIMARY KEY, xp INTEGER, hp INTEGER)''')

c.execute("SELECT * FROM user_stats WHERE id=1")
if not c.fetchone():
    c.execute("INSERT INTO user_stats (id, xp, hp) VALUES (1, 0, 10)")
    conn.commit()

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def get_stats():
    c.execute("SELECT xp, hp FROM user_stats WHERE id=1")
    return c.fetchone()

def update_stats(xp_gain, hp_change):
    current_xp, current_hp = get_stats()
    new_xp = current_xp + xp_gain
    new_hp = max(0, min(10, current_hp + hp_change))
    c.execute("UPDATE user_stats SET xp=?, hp=? WHERE id=1", (new_xp, new_hp))
    conn.commit()

def calculate_level(xp):
    levels = {0: "Trainee", 500: "Coder", 1500: "Architect", 3000: "Assassin"}
    current_level = "Trainee"
    for threshold, title in levels.items():
        if xp >= threshold:
            current_level = title
    return current_level

# ==========================================
# 4. DASHBOARD UI
# ==========================================

current_xp, current_hp = get_stats()
current_level = calculate_level(current_xp)

# --- HEADER ---
st.markdown('<p class="title-text">NEURAL FORGE</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Admin Assassin // Development & Training Interface</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="System Rank", value=current_level)
with col2:
    st.metric(label="Earned XP", value=f"{current_xp}")
with col3:
    # Minimalist HP display
    hp_display = "▰" * current_hp + "▱" * (10 - current_hp)
    st.metric(label="Cognitive Load (HP)", value=hp_display)

st.write("") # Clean spacer
st.write("") 

# --- SIDEBAR: FORGE ---
with st.sidebar:
    st.markdown('<p class="bounty-title">Initialize Protocol</p>', unsafe_allow_html=True)
    st.markdown('<p class="meta-text" style="margin-bottom: 1.5rem;">Log new nodes and extraction tasks.</p>', unsafe_allow_html=True)
    
    with st.form("bounty_form", border=False, clear_on_submit=True):
        b_title = st.text_input("Protocol Designation (Title)")
        b_cat = st.selectbox("System Area", ["Skill Graph Node", "Coursework Extraction", "Platform Architecture"])
        b_true_date = st.date_input("Actual Deadline")
        b_xp = st.slider("Complexity (XP)", 50, 500, 100, step=50)
        
        st.write("")
        submitted = st.form_submit_button("Deploy to Queue", use_container_width=True)
        
        if submitted and b_title:
            panic_date = b_true_date - timedelta(days=5)
            c.execute("INSERT INTO bounties (title, category, true_deadline, panic_deadline, xp, status) VALUES (?, ?, ?, ?, ?, ?)",
                      (b_title, b_cat, str(b_true_date), str(panic_date), b_xp, 'Active'))
            conn.commit()
            st.rerun()

# --- MAIN: ACTIVE BOUNTIES ---
st.markdown('<p class="meta-text">Active Queue // Rule of 3</p>', unsafe_allow_html=True)

c.execute("SELECT id, title, category, panic_deadline, xp FROM bounties WHERE status='Active' ORDER BY panic_deadline ASC LIMIT 3")
active_bounties = c.fetchall()

if not active_bounties:
    st.info("Queue is empty. System idle.")
else:
    for bounty in active_bounties:
        b_id, b_title, b_cat, b_panic, b_xp = bounty
        
        # Native Streamlit Card Container
        with st.container(border=True):
            colA, colB, colC = st.columns([3, 1, 1], gap="medium")
            
            with colA:
                st.markdown(f'<p class="meta-text">{b_cat} • {b_xp} XP</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="bounty-title">{b_title}</p>', unsafe_allow_html=True)
                
            with colB:
                days_left = (datetime.strptime(b_panic, "%Y-%m-%d").date() - datetime.today().date()).days
                # Sleek deadline coloring
                if days_left <= 0:
                    status_color = "#ff4b4b" # Streamlit Red
                    status_text = "CRITICAL"
                elif days_left <= 2:
                    status_color = "#ffa421" # Streamlit Orange
                    status_text = "WARNING"
                else:
                    status_color = "#21c354" # Streamlit Green
                    status_text = "OPTIMAL"

                st.markdown(f'<p class="meta-text">Panic Deadline</p>', unsafe_allow_html=True)
                st.markdown(f'<p style="font-weight: 700; color: {status_color}; margin: 0;">{b_panic}</p>', unsafe_allow_html=True)
                st.markdown(f'<p style="font-size: 0.75rem; color: {status_color}; margin: 0;">{status_text} ({days_left}d left)</p>', unsafe_allow_html=True)
                
            with colC:
                st.write("") # Vertical alignment spacer
                if st.button("Resolve", key=f"comp_{b_id}", use_container_width=True):
                    c.execute("UPDATE bounties SET status='Completed' WHERE id=?", (b_id,))
                    update_stats(b_xp, 0)
                    st.rerun()

st.write("")
st.write("")

# --- FOOTER: ARCHIVE ---
with st.expander("System Archive // Backlog & Resolved", expanded=False):
    tab1, tab2 = st.tabs(["Queue (Hidden)", "Resolved Protocols"])
    
    with tab1:
        c.execute("SELECT title, category, panic_deadline, xp FROM bounties WHERE status='Active' ORDER BY panic_deadline ASC LIMIT 100 OFFSET 3")
        on_deck = c.fetchall()
        if on_deck:
            df_deck = pd.DataFrame(on_deck, columns=["Title", "Category", "Panic Deadline", "XP"])
            st.dataframe(df_deck, use_container_width=True, hide_index=True)
        else:
            st.markdown('<p class="subtitle-text">No pending protocols.</p>', unsafe_allow_html=True)
            
    with tab2:
        c.execute("SELECT title, category, xp FROM bounties WHERE status='Completed' ORDER BY id DESC")
        completed = c.fetchall()
        if completed:
            df_comp = pd.DataFrame(completed, columns=["Title", "Category", "XP Earned"])
            st.dataframe(df_comp, use_container_width=True, hide_index=True)
        else:
            st.markdown('<p class="subtitle-text">Awaiting data.</p>', unsafe_allow_html=True)