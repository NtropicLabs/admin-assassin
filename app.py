import streamlit as st
import json
import anthropic
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Admin Assassin — Clinical AI Scribe",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=DM+Mono:wght@400;500&family=Instrument+Serif:ital@0;1&display=swap');

:root {
    --bg: #090B10;
    --surface: #111318;
    --surface-2: #181B24;
    --border: #1E2130;
    --border-light: #272B3D;
    --text-primary: #EDF0F7;
    --text-secondary: #8892A4;
    --text-muted: #434860;
    --accent: #3B82F6;
    --accent-hover: #2563EB;
    --accent-dim: rgba(59,130,246,0.1);
    --accent-border: rgba(59,130,246,0.2);
    --gold: #C8A96E;
    --gold-dim: rgba(200,169,110,0.08);
    --gold-border: rgba(200,169,110,0.25);
    --green: #10B981;
    --green-dim: rgba(16,185,129,0.08);
    --red: #EF4444;
    --red-dim: rgba(239,68,68,0.06);
    --slate: #64748B;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: var(--bg) !important;
    color: var(--text-primary);
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0; }

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 0 8px 8px 0 !important;
}
[data-testid="stSidebarCollapseButton"] {
    display: flex !important;
    visibility: visible !important;
    color: var(--text-secondary) !important;
}

/* ── Sidebar ── */
.sidebar-brand {
    padding: 2.25rem 1.75rem 1.75rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.75rem;
}
.sidebar-brand h2 {
    font-family: 'Instrument Serif', serif;
    font-size: 1.4rem;
    font-weight: 400;
    color: var(--text-primary);
    letter-spacing: -0.01em;
    margin-bottom: 0.25rem;
}
.sidebar-brand span { color: var(--accent); }
.sidebar-brand p {
    font-size: 0.72rem;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 500;
}
.sidebar-section-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0 1.75rem;
    margin-bottom: 0.6rem;
}
.privacy-box {
    margin: 1.5rem 1.25rem;
    padding: 1.1rem 1.25rem;
    background: rgba(59,130,246,0.04);
    border: 1px solid var(--accent-border);
    border-radius: 10px;
    font-size: 0.76rem;
    color: var(--text-secondary);
    line-height: 1.7;
}
.privacy-box strong {
    display: block;
    font-size: 0.67rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}
.version-tag {
    font-size: 0.67rem;
    color: var(--text-muted);
    padding: 1.5rem 1.75rem;
    font-family: 'DM Mono', monospace;
}

/* ── Main header ── */
.clinical-header {
    padding: 3rem 0 2.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2.5rem;
    display: flex;
    align-items: center;
    gap: 2rem;
}
.pixel-art-container {
    background: var(--surface);
    border: 1px solid var(--border-light);
    border-radius: 14px;
    padding: 14px;
    display: inline-block;
    flex-shrink: 0;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}
.pixel-grid {
    display: grid;
    grid-template-columns: repeat(11, 10px);
    grid-template-rows: repeat(11, 10px);
    gap: 2px;
}
.px { width: 10px; height: 10px; border-radius: 2px; }
.px-on { background: var(--accent); box-shadow: 0 0 5px rgba(59,130,246,0.5); }
.px-off { background: transparent; }

.header-text { flex: 1; }
.header-text h1 {
    font-family: 'Instrument Serif', serif;
    font-size: 2.4rem;
    font-weight: 400;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 0.5rem;
}
.header-text h1 em { color: var(--accent); font-style: italic; }
.header-text p {
    font-size: 0.88rem;
    color: var(--text-secondary);
    font-weight: 400;
    margin-bottom: 1rem;
    letter-spacing: 0;
}
.header-chips { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.chip {
    font-size: 0.67rem;
    font-weight: 500;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    letter-spacing: 0.04em;
    font-family: 'DM Sans', sans-serif;
}
.chip-blue { background: var(--accent-dim); color: #93C5FD; border: 1px solid var(--accent-border); }
.chip-slate { background: rgba(100,116,139,0.1); color: var(--slate); border: 1px solid rgba(100,116,139,0.2); }
.chip-grey { background: rgba(74,82,104,0.12); color: var(--text-muted); border: 1px solid var(--border-light); }

/* ── Transcript workspace ── */
.workspace-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 0.6rem;
}
.workspace-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-secondary);
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.workspace-hint {
    font-size: 0.72rem;
    color: var(--text-muted);
    font-style: italic;
}

/* ── Inputs ── */
[data-testid="stTextArea"] textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.925rem !important;
    line-height: 1.8 !important;
    padding: 1.25rem 1.5rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
[data-testid="stTextArea"] textarea::placeholder { color: var(--text-muted) !important; }
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.08) !important;
    outline: none !important;
}
[data-testid="stTextInput"] input {
    background: var(--surface) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
    padding: 0.6rem 0.9rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.08) !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--surface);
    border-radius: 8px;
    padding: 3px;
    gap: 2px;
    border: 1px solid var(--border);
    width: fit-content;
    margin-bottom: 1.5rem;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
    padding: 0.4rem 1.1rem !important;
    border: none !important;
    transition: all 0.15s !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: var(--accent) !important;
    color: #FFFFFF !important;
}

/* ── Buttons ── */
[data-testid="stButton"] > button[kind="primary"] {
    background: var(--accent) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    padding: 0.7rem 1.5rem !important;
    width: 100% !important;
    letter-spacing: 0.01em !important;
    transition: background 0.15s ease, box-shadow 0.15s ease !important;
    margin-top: 0.75rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.4) !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    background: var(--accent-hover) !important;
    box-shadow: 0 4px 20px rgba(59,130,246,0.3) !important;
    transform: none !important;
}
[data-testid="stButton"] > button[kind="secondary"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    padding: 0.3rem 0.8rem !important;
    transition: all 0.15s !important;
}
[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: var(--accent-dim) !important;
}

/* ── Risk banner ── */
.risk-banner {
    background: var(--red-dim);
    border: none;
    border-left: 3px solid var(--red);
    border-radius: 0 10px 10px 0;
    padding: 1.25rem 1.5rem;
    margin-bottom: 2rem;
    animation: pulse-red 4s ease-in-out infinite;
}
@keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.1); }
    50% { box-shadow: 0 0 0 4px rgba(239,68,68,0); }
}
.risk-banner h3 {
    color: var(--red);
    font-family: 'DM Sans', sans-serif;
    font-size: 0.88rem;
    font-weight: 600;
    margin-bottom: 0.35rem;
    letter-spacing: 0.01em;
}
.risk-banner p {
    color: #FCA5A5;
    font-size: 0.83rem;
    margin-bottom: 0.85rem;
    font-weight: 400;
}
.risk-quote {
    background: rgba(239,68,68,0.08);
    border-left: 2px solid rgba(239,68,68,0.5);
    border-radius: 0 4px 4px 0;
    padding: 0.65rem 1rem;
    font-style: italic;
    font-size: 0.85rem;
    color: #FCA5A5;
    line-height: 1.6;
}

/* ── Output section ── */
.output-section-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1.25rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border);
}

/* ── Cards ── */
.output-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 2rem 2.25rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 2px 16px rgba(0,0,0,0.25);
}
.output-card:hover {
    border-color: var(--border-light);
    box-shadow: 0 4px 28px rgba(0,0,0,0.35);
}
.output-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 12px 12px 0 0;
}
.card-soap::before { background: var(--accent); }
.card-gp::before { background: #8B5CF6; }
.card-formulation::before { background: var(--green); }
.card-risk::before { background: var(--red); }

.output-card h3 {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-secondary);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.output-card .content {
    font-size: 0.875rem;
    line-height: 1.9;
    color: var(--text-secondary);
    white-space: pre-wrap;
}

/* ── SOAP sections ── */
.soap-label {
    font-size: 0.67rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 1.5rem 0 0.5rem;
}
.soap-label:first-of-type { margin-top: 0; }
.soap-content {
    font-size: 0.875rem;
    line-height: 1.85;
    color: var(--text-secondary);
    padding: 0.85rem 1.1rem;
    background: rgba(255,255,255,0.02);
    border-left: 3px solid var(--border-light);
    border-radius: 0 6px 6px 0;
}

/* ── Badges ── */
.badge-safe {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--green-dim);
    border: 1px solid rgba(16,185,129,0.2);
    color: var(--green);
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 1rem;
    letter-spacing: 0.02em;
}
.badge-risk {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--red-dim);
    border: 1px solid rgba(239,68,68,0.2);
    color: var(--red);
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 1rem;
    letter-spacing: 0.02em;
}

/* ── Session history ── */
.session-item {
    background: transparent;
    border: 1px solid var(--border);
    border-radius: 7px;
    padding: 0.55rem 0.85rem;
    margin-bottom: 0.4rem;
    font-size: 0.78rem;
    color: var(--text-secondary);
    transition: all 0.15s;
    cursor: pointer;
}
.session-item:hover {
    border-color: var(--accent);
    color: var(--text-primary);
    background: var(--accent-dim);
}

/* ── Coming soon ── */
.coming-soon {
    background: var(--surface);
    border: 1px dashed var(--border-light);
    border-radius: 10px;
    padding: 2.5rem;
    text-align: center;
    color: var(--text-muted);
    font-size: 0.85rem;
}
.coming-soon span { display: block; font-size: 1.5rem; margin-bottom: 0.6rem; }

/* ── Footer ── */
.clinical-footer {
    margin-top: 3rem;
    padding: 1.25rem 0;
    border-top: 1px solid var(--border);
    text-align: center;
    font-size: 0.72rem;
    color: var(--text-muted);
    line-height: 1.6;
}

/* ── Labels ── */
label, [data-testid="stWidgetLabel"] {
    color: var(--text-secondary) !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
}

hr { border-color: var(--border) !important; }
[data-testid="stSpinner"] { color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "copied" not in st.session_state:
    st.session_state.copied = {}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2><span>Admin</span> Assassin</h2>
        <p>Clinical AI Scribe</p>
    </div>
    """, unsafe_allow_html=True)

    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")

    st.markdown("---")

    # Session history
    st.markdown('<p style="font-size:0.72rem;color:#8B9CB6;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.75rem;">Recent Sessions</p>', unsafe_allow_html=True)

    if st.session_state.history:
        for i, session in enumerate(reversed(st.session_state.history[-5:])):
            if st.button(f"📋 Session {session['time']}", key=f"hist_{i}", use_container_width=True):
                st.session_state.last_result = session["result"]
    else:
        st.markdown('<p style="font-size:0.78rem;color:#3D4560;font-style:italic;">No sessions yet</p>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div class="privacy-box">
        <strong>🔒 Privacy Notice</strong>
        This tool processes anonymised transcripts only.
        All AI output requires clinician review before use.
        No patient data is stored or retained.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="version-tag">v1.0 — Beta</div>', unsafe_allow_html=True)

# ── Generate pixel brain ──────────────────────────────────────────────────────
brain_map = [
    [0,0,1,1,0,0,0,1,1,0,0],
    [0,1,1,1,1,0,1,1,1,1,0],
    [1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,0,1,1,1,0,1,1,1],
    [0,1,1,1,1,1,1,1,1,1,0],
    [0,0,1,1,1,1,1,1,1,0,0],
    [0,0,0,1,1,1,1,1,0,0,0],
    [0,0,0,1,0,1,0,1,0,0,0],
    [0,0,0,1,1,1,1,1,0,0,0],
    [0,0,0,0,1,1,1,0,0,0,0],
]
brain_html = "".join(
    f'<div class="px {"px-on" if cell else "px-off"}"></div>'
    for row in brain_map for cell in row
)

# ── Main panel ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="clinical-header">
    <div class="terminal-logo">
        <div class="pixel-art-container">
            <div class="pixel-grid">
                {brain_html}
            </div>
        </div>
    </div>
    <div class="header-text">
        <h1>Admin <em>Assassin</em></h1>
        <p>Privacy-first clinical scribe for CBT therapists</p>
        <div class="header-chips">
            <span class="chip chip-blue">Claude Sonnet</span>
            <span class="chip chip-slate">CBT Clinical AI</span>
            <span class="chip chip-grey">v1.0 Beta</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input tabs ────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📝  Paste Transcript", "🎙  Upload Audio  (Coming in V2)"])

with tab1:
    st.markdown("""
    <div class="workspace-header">
        <span class="workspace-label">Session Transcript</span>
        <span class="workspace-hint">Use initials — anonymised transcripts only</span>
    </div>
    """, unsafe_allow_html=True)

    transcript = st.text_area(
        label="Session Transcript",
        height=280,
        placeholder="Paste your session transcript here.\n\nFor best results, include the full session dialogue.\nPatient name is not required — use initials or remove entirely.",
        label_visibility="collapsed"
    )

    _, btn_col = st.columns([2, 1])
    with btn_col:
        generate_btn = st.button("Generate Documentation", type="primary")

with tab2:
    st.markdown("""
    <div class="coming-soon">
        <span>🎙</span>
        Audio upload + Whisper transcription coming in V2.<br>
        Record directly in the therapy room — no laptop needed.
    </div>
    """, unsafe_allow_html=True)

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a senior CBT clinical supervisor with 20 years experience in NHS IAPT and Talking Therapies settings. You must analyse the session transcript using the specific clinical framework below. This is not general CBT knowledge — this is the exact framework you must apply.

=== CLINICAL KNOWLEDGE FRAMEWORK ===

--- DEPRESSION MAINTENANCE CYCLE ---
The cycle is: Trigger → Behavioural Withdrawal → Loss of Reinforcement (pleasure/mastery) → Deepening Mood → repeat. It is recursive and accelerating. The cognitive layer functions as a PERMISSION STRUCTURE for withdrawal. You must identify which of these five permission-giving cognitions are present:
1. MOOD-FIRST FALLACY: Client believes feeling better must precede action. Signals: "I'll wait until I have energy", "I'll do it when I feel more like myself."
2. MINIMISATION OF MICRO-STEP: Devalues the graded task. Signals: "How is a short walk going to fix my problems?", "That doesn't count as doing something."
3. PREDICTIVE APATHY (Anticipatory Anhedonia): Treats negative prediction as fact before activity occurs. Signals: "I know I'll just be miserable", "I won't get anything out of it."
4. IDENTITY ANCHORING: Compares current capacity to pre-depression baseline. Signals: "I used to run 5k — this is pathetic", "I've turned into a lazy person."
5. FALSE BINARY: All-or-nothing effort rule. Signals: "If I can't do the whole house, I'm not touching any of it."
CLINICAL ERROR TO AVOID — THE GYM TRAP: Never anchor activity goals to the client's pre-depression baseline. Activity must be unhitched from identity and past self entirely.

--- BEHAVIOURAL ACTIVATION ---
BA is not activity scheduling. It is a structured behavioural experiment testing the depression's predictions against reality. A complete BA intervention requires ALL FOUR components:
1. RATIONALE: Was the frame explained? (Action before motivation, testing predictions, not arguing with them)
2. COLLABORATIVE TASK SELECTION: Was a specific, graded, binary-proof task chosen? If client says "I'll try" — task is too big. Must be small enough they can say "I will."
3. EXPLICIT BASELINE PREDICTION: Were Pleasure (0-10) and Mastery (0-10) predictions recorded BEFORE the activity? Without this, there is no experiment. This is the most commonly skipped step.
4. DUAL-METRIC TRACKING: Were both Pleasure AND Mastery rated AFTER completion? Never collapse into single mood rating. Pleasure tests "you won't enjoy anything." Mastery tests "you're useless and incapable." They lie differently.
KEY CONCEPT — PREDICTION ERROR: The gap between predicted and actual rating is the clinical data. A prediction of 0/10 with an actual of 2/10 is proof the depression lied. Flag this explicitly.
If BA homework was reviewed: extract prediction vs actual, calculate prediction error, note clinical significance.

--- AUTOMATIC THOUGHTS ---
Automatic thoughts are the primary intervention target in Brief CBT. Identify and label each using this taxonomy:
1. ALL-OR-NOTHING THINKING: Binary categories, no middle ground. "If I don't get it perfect, I've failed."
2. OVERGENERALISATION: Single event → universal pattern. Listen for: always, never, everyone, no one.
3. MENTAL FILTER: Focuses on single negative, ignores broader context. (Omission — positive data not perceived)
4. DISQUALIFYING THE POSITIVE: Positive perceived but actively neutralised. "They only said that to be nice." (Active rejection — distinguish from Mental Filter)
5. MIND READING: Assuming others' negative thoughts. "My manager thinks I'm incompetent."
6. FORTUNE TELLING: Predicting negative outcome as fact. "There's no point trying, I'll fail."
7. CATASTROPHISING: Escalating to worst conceivable conclusion.
8. EMOTIONAL REASONING: Feelings as evidence of reality. "I feel like a burden so I must be one."
9. SHOULD STATEMENTS: Rigid internal rules. Listen for: should, must, ought, shouldn't.
10. LABELLING: Identity fusion. "I'm a failure" vs "I failed at this." Flag as possible core belief activation.
11. PERSONALISATION: Attributing external events to self as primary cause.
IMPORTANT DISTINCTIONS: Mind Reading + Fortune Telling together suggest Performance=Safety intermediate belief. Mental Filter = omission. Disqualifying the Positive = active rejection. Different interventions required.
Brief CBT boundary: If same distortions appear across 3+ sessions without shift, flag for supervisor — may indicate deeper core belief work needed beyond Brief CBT scope.

--- PHQ-9 SCORING AND INTERPRETATION ---
Scale: 0-4 None, 5-9 Mild, 10-14 Moderate (treatment threshold), 15-19 Moderately Severe, 20-27 Severe.
CRITICAL RULE — THE TRAJECTORY IS THE DIAGNOSTIC: NEVER report a PHQ-9 score in isolation. Always calculate:
1. ASSESSMENT DELTA: Assessment baseline score minus current score. Positive = improvement.
2. SESSION DELTA: Previous session score minus current score. Positive = improvement this session.
RELIABLE CHANGE INDEX (RCI): A change of less than 5-6 points is within measurement error and is NOT reliable change. Document whether RCI threshold is met.
QUESTION 9 OVERRIDE: Q9 (thoughts of being better off dead or self-harm) operates on COMPLETELY SEPARATE logic. A PHQ-9 of 5 with Q9=1 is more urgent than PHQ-9 of 18 with Q9=0. If Q9 > 0: flag immediately in bold, conduct full risk documentation, override all other priorities.
THE SNAPSHOT ERROR: A score of 12 coming down from 19 = success signal. A score of 12 going up from 8 = warning signal requiring formulation review and pivot.

--- RISK DETECTION ---
Flag conservatively. Any reference to: suicidal ideation, self-harm, harm to others, hopelessness about the future, feeling a burden, "better off without me", disappearing ideation. When in doubt, flag.

--- PLEASURE AND MASTERY RATINGS ---
Dual-metric system (0-10) for tracking BA activity outcomes. NEVER collapse into single mood rating — depression lies differently about pleasure and mastery.
PLEASURE (P): Enjoyment, sensory satisfaction. Often near zero in moderate-severe depression due to anhedonia — this is expected, not treatment failure.
MASTERY (M): Sense of accomplishment, competence, effectiveness — independent of enjoyment. Paying a bill = 0 pleasure, high mastery.
MASTERY FIRST RECOVERY PATTERN: Mastery typically recovers before Pleasure. P:0, M:3 is the engine restarting — early recovery, not failure. Never evaluate BA success on Pleasure alone.
PREDICTION AS CLINICAL SIGNAL: Record prediction BEFORE activity. Prediction of P:0/M:0 = full Predictive Apathy. Prediction of P:0/M:2 = belief "I am completely useless" already fracturing — document this explicitly.
THREE OUTCOME SCENARIOS:
1. DISCONFIRMATORY EVIDENCE: Actual exceeds predicted. Flag explicitly — "You predicted 2, you got 6. What do you make of that gap?" This is a therapeutic moment.
2. TASK CALIBRATION REVIEW: Actual matches predicted (low). Not failure — information. Review task structure.
3. INTERVENING FACTOR: Actual below predicted. Something disrupted between prediction and activity. Explore in next session.
THE HAPPY BIAS ERROR: Evaluating BA success on Pleasure alone. A client reporting P:0/M:5 has had a productive session. Validate Mastery first — always.

--- THOUGHT RECORDS ---
Thought records externalise the internal dialogue so the client can examine it from outside. Two formats used at different treatment stages.
FIVE-COLUMN RECORD (Sessions 2-4): Situation | Mood (0-100%) | Automatic Thought + belief rating | Evidence For | Evidence Against. The Detective Before the Judge — observation and investigation only. Do NOT add balanced thought too early.
SEVEN-COLUMN RECORD (Sessions 4+): Adds Column 6 (Balanced Thought + belief rating) and Column 7 (Mood Re-Rating). Only introduce once client can reliably generate Evidence Against without prompting.
COLUMN 6 — BALANCED THOUGHT: Not positive thinking. Not the opposite of the automatic thought. The most accurate statement given ALL evidence — should feel slightly uncomfortable to generate. Check belief rating — if below 50%, evidence gathering was insufficient.
COLUMN 7 — EMOTIONAL DELTA: The ONLY column that proves whether cognitive work actually landed.
- Significant drop (>20 points): Genuine cognitive shift. Intervention worked.
- Minimal drop (<10 points): HEAD-HEART DISCREPANCY — intellectual insight without emotional change. "I know it's not rational but I still feel it." Causes: wrong thought targeted, insufficient evidence, or intermediate belief active.
- No drop or increase: Wrong thought targeted entirely, or intermediate belief regenerating faster than restructuring can address.
HOT THOUGHT IDENTIFICATION: The first thought a client names is often not the hot thought. Signal: belief rating below 70%, minimal emotional delta after full record. Probe deeper: "Was there something even more distressing going through your mind?"
FORCED POSITIVITY SIGNAL: Client generates balanced thought easily and pleasantly — it's probably reassurance, not accuracy. Return to Column 5.

--- COGNITIVE RESTRUCTURING ---
The systematic examination of evidence the depression has been filtering out. Not positive thinking. Not reassurance. Not arguing.
THREE-PHASE STRUCTURE — all phases required:
PHASE 1 — VALIDATION (non-negotiable precondition): Validate the emotional reality of the thought BEFORE any examination. Without this, Socratic questioning feels like interrogation. If transcript shows therapist moving directly to questioning without validation — flag as fidelity gap.
PHASE 2 — SOCRATIC QUESTIONING (guided discovery): Evidence retrieval operations, not leading questions.
LEADING (wrong): "But you did a good job on the report, didn't you?" — seeks compliance.
SOCRATIC (correct): "If your closest friend described doing exactly what you did, what would you say to them?" — seeks data the client owns.
KEY SOCRATIC QUESTIONS: "What facts support this — not feelings, facts?" / "What facts don't fit, even small ones?" / "If a close friend had this thought, what would you tell them?" / "You said always — can you find one exception?" / "What's the difference between feeling like a failure and being a failure?"
PHASE 3 — SYNTHESIS: Balanced thought generated from both sides of evidence. Must acknowledge kernel of truth in original thought. Belief rating checked immediately — if low, return to Phase 2.
EMOTIONAL DELTA: Calculate and classify. Head-Heart Discrepancy causes: (1) wrong thought targeted, (2) insufficient evidence, (3) intermediate belief active and regenerating.
CLINICAL ERRORS TO FLAG: Reassurance giving (therapist doing the work instead of client) / Moving to balanced thought too quickly / Accepting feelings as evidence / Working on surface thought not hot thought.

--- INTERMEDIATE BELIEFS ---
Rules, assumptions, and attitudes that generate automatic thoughts across different situations by applying the same underlying rule. Not targeted directly in Brief CBT — surface through pattern recognition across sessions.
THE CLINICAL MOVE: From micro-analysis to pattern recognition. Stop examining individual thoughts. Start examining what connects them across situations.
THREE FORMS: Rules ("I must always perform at the highest level") / Assumptions ("If I ask for help, people will think I'm weak") / Attitudes ("Needing support is a sign of failure")
CROSS-SESSION DETECTION RULE: Same core theme in automatic thoughts across 3+ different situational contexts = probable intermediate belief active.
THE IF-THEN STRUCTURE: Most intermediate beliefs follow: If [condition that feels dangerous] → Then [feared consequence]. Making this explicit immediately raises the testable question: "Has showing weakness always led to rejection? Always?"
FOUR COMMON THEMES IN DEPRESSION:
1. PERFORMANCE = SAFETY: "I must be competent and successful at all times to have value." Generates: Mind Reading, Fortune Telling, Identity Anchoring, Should Statements.
2. VULNERABILITY = REJECTION: "Showing need will cause others to abandon me." Generates: social withdrawal, burden cognitions, self-reliance as safety behaviour.
3. RESPONSIBILITY = WORTH: "If I cannot manage independently, I am a failure." Generates: help-avoidance, Should Statements, all-or-nothing effort evaluation.
4. EFFORT = IDENTITY: "My value is determined by what I produce." Generates: Identity Anchoring, Minimisation of Micro-Step, catastrophising around productivity.
NAMING WITHOUT TRIGGERING DEFENSIVENESS: Show the pattern, don't name pathology. "We've done three thought records — work, the party, the call with your mum. Look at the automatic thought column. Your brain is running the exact same rule in all three places. Does that sound right?" Then: "I'm curious where that came from. And I'm wondering whether it's still serving you." USE THE RUNNING CODE FRAMING — externalise as a rule the brain executes, not a character defect.
BRIEF CBT BOUNDARY: Can loosen the belief's authority in 8 sessions. Cannot dismantle at roots — that's schema work requiring longer-term therapy. If belief-level work produces minimal shift — flag as possible treatment boundary.

=== OUTPUT INSTRUCTIONS ===
Return ONLY raw JSON — no markdown, no backticks, no preamble:
{
  "risk_detected": true or false,
  "risk_content": "exact quoted phrase from transcript if risk detected, else null",
  "hot_thought": "the primary automatic thought identified, labelled with its distortion type",
  "maintenance_cycle": "which specific permission-giving cognitions are present and how they function in this client's cycle",
  "safety_behaviours": "specific safety behaviours and avoidance patterns identified, else 'None identified'",
  "soap_note": {
    "subjective": "client's reported experience in their own words, including any PHQ-9 verbal statements and their language around mood, activity, and motivation",
    "objective": "PHQ-9 score with assessment delta, session delta, and RCI status. Any Q9 score. BA homework completion status. Observable clinical data.",
    "assessment": "full CBT formulation — maintenance cycle mechanisms identified by name, automatic thought distortions labelled, trajectory interpretation, any intermediate belief patterns, BA prediction error data if present",
    "plan": "interventions used, BA task set with prediction recorded, next session clinical targets, any risk management actions, any unaddressed cognitive targets flagged for next session"
  },
  "gp_letter": "full NHS Talking Therapies style GP letter — include risk disclosure clearly if present, PHQ-9 trajectory, clinical formulation summary, and any recommended actions",
  "risk_summary": "clinical risk documentation — Q9 status, any ideation content quoted, safety plan status, risk level assessment, recommended actions"
}"""

# ── Generation logic ──────────────────────────────────────────────────────────
if generate_btn:
    if not api_key:
        st.error("⚠️ Please enter your Anthropic API key in the sidebar.")
    elif not transcript.strip():
        st.error("⚠️ Please paste a session transcript before generating.")
    else:
        with st.spinner("Analysing transcript..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=8192,
                    system=SYSTEM_PROMPT,
                    messages=[
                        {"role": "user", "content": transcript}
                    ]
                )
                raw = response.content[0].text
                # Strip markdown fences if present
                raw = raw.strip()
                if raw.startswith("```"):
                    raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
                result = json.loads(raw)
                st.session_state.last_result = result
                st.session_state.history.append({
                    "time": datetime.now().strftime("%H:%M"),
                    "result": result
                })
            except json.JSONDecodeError:
                st.error("⚠️ The AI returned an unexpected format. Please try again.")
            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")

# ── Output rendering ──────────────────────────────────────────────────────────
if st.session_state.last_result:
    r = st.session_state.last_result

    # Risk banner
    if r.get("risk_detected"):
        st.markdown(f"""
        <div class="risk-banner">
            <h3>⚠️ CLINICAL RISK DETECTED — Review Required</h3>
            <p>The following content has been flagged. This requires immediate clinical review before proceeding.</p>
            <div class="risk-quote">"{r.get('risk_content', 'Risk phrase not extracted')}"</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="output-section-label">Clinical Documentation</div>', unsafe_allow_html=True)

    # Top row — SOAP + GP Letter
    col1, col2 = st.columns(2)

    with col1:
        soap = r.get("soap_note", {})
        soap_text = f"S: {soap.get('subjective','')}\nO: {soap.get('objective','')}\nA: {soap.get('assessment','')}\nP: {soap.get('plan','')}"
        st.markdown(f"""
        <div class="output-card card-soap">
            <h3>📋 SOAP Note</h3>
            <div class="soap-label">S — Subjective</div>
            <div class="soap-content">{soap.get('subjective', '—')}</div>
            <div class="soap-label">O — Objective</div>
            <div class="soap-content">{soap.get('objective', '—')}</div>
            <div class="soap-label">A — Assessment</div>
            <div class="soap-content">{soap.get('assessment', '—')}</div>
            <div class="soap-label">P — Plan</div>
            <div class="soap-content">{soap.get('plan', '—')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Copy SOAP Note", key="copy_soap"):
            st.code(soap_text, language=None)

    with col2:
        gp_letter = r.get("gp_letter", "")
        st.markdown(f"""
        <div class="output-card card-gp">
            <h3>✉️ GP Letter</h3>
            <div class="content">{gp_letter}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Copy GP Letter", key="copy_gp"):
            st.code(gp_letter, language=None)

    # Bottom row — CBT Formulation + Risk Summary
    col3, col4 = st.columns(2)

    with col3:
        formulation_text = f"Hot Thought: {r.get('hot_thought','')}\n\nMaintenance Cycle: {r.get('maintenance_cycle','')}\n\nSafety Behaviours: {r.get('safety_behaviours','')}"
        st.markdown(f"""
        <div class="output-card card-formulation">
            <h3>🧠 CBT Formulation</h3>
            <div class="soap-label">Hot Thought</div>
            <div class="soap-content">{r.get('hot_thought', '—')}</div>
            <div class="soap-label">Maintenance Cycle</div>
            <div class="soap-content">{r.get('maintenance_cycle', '—')}</div>
            <div class="soap-label">Safety Behaviours</div>
            <div class="soap-content">{r.get('safety_behaviours', '—')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Copy Formulation", key="copy_form"):
            st.code(formulation_text, language=None)

    with col4:
        risk_badge = '<div class="badge-risk">⚠ Risk Detected</div>' if r.get("risk_detected") else '<div class="badge-safe">✓ No Risk Identified</div>'
        risk_text = r.get('risk_summary', '—')
        st.markdown(f"""
        <div class="output-card card-risk">
            <h3>🛡 Risk Summary</h3>
            {risk_badge}
            <div class="content">{risk_text}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Copy Risk Summary", key="copy_risk"):
            st.code(risk_text, language=None)

    st.markdown("""
    <div class="clinical-footer">
        All output requires clinician review before use. Admin Assassin does not store patient data.
    </div>
    """, unsafe_allow_html=True)
