import streamlit as st
import json
import html as html_lib
import anthropic
from datetime import datetime

# ── Constants ────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a senior CBT clinical supervisor with 20 years experience in NHS IAPT
and Talking Therapies settings. Analyse the following therapy session transcript.

Return your analysis in this exact JSON structure (no markdown, no backticks, raw JSON only):
{
  "risk_detected": true/false,
  "risk_content": "exact quoted phrase if risk detected, else null",
  "hot_thought": "the primary automatic thought identified",
  "maintenance_cycle": "brief description of the CBT maintenance loop present",
  "safety_behaviours": "any safety behaviours identified, else 'None identified'",
  "soap_note": {
    "subjective": "patient's reported experience in their own words",
    "objective": "observable clinical data, measures, therapist observations",
    "assessment": "clinical formulation, CBT model, maintenance mechanisms",
    "plan": "intervention used, homework set, next session focus"
  },
  "gp_letter": "full NHS-style GP letter draft",
  "risk_summary": "brief clinical risk summary for documentation"
}

Risk detection: flag if transcript contains ANY reference to suicidal ideation,
self-harm, harm to others, or expressions of hopelessness about the future.
Flag conservatively — when in doubt, flag."""

BRAIN_MAP = [
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


# ── Helpers ──────────────────────────────────────────────────────────────────

def safe(text):
    """Escape HTML entities in AI-generated text to prevent XSS."""
    if text is None:
        return "—"
    return html_lib.escape(str(text))


def render_pixel_brain():
    """Generate the pixel art brain HTML grid."""
    cells = "".join(
        f'<div class="px {"px-on" if cell else "px-off"}"></div>'
        for row in BRAIN_MAP for cell in row
    )
    return f"""
    <div class="pixel-art-container">
        <div class="pixel-grid">{cells}</div>
    </div>"""


def inject_css():
    """Inject all custom CSS into the Streamlit app."""
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&family=Space+Mono:wght@400;700&family=Syne:wght@700;800&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0F1117 !important;
    color: #FFFFFF;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] {
    background: #1A1D24 !important;
    border-right: 1px solid #2D3141;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Sidebar branding ── */
.sidebar-logo {
    padding: 0 1rem 1.5rem 1rem;
    border-bottom: 1px solid #2D3141;
    margin-bottom: 1.5rem;
}
.sidebar-logo h1 {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    color: #4A9EFF;
    margin: 0 0 0.2rem 0;
    letter-spacing: -0.02em;
}
.sidebar-logo p {
    font-size: 0.72rem;
    color: #8B9CB6;
    margin: 0;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── Privacy disclaimer ── */
.privacy-box {
    background: #12151E;
    border: 1px solid #2D3141;
    border-radius: 8px;
    padding: 0.75rem;
    margin: 1.5rem 0 1rem 0;
    font-size: 0.72rem;
    color: #8B9CB6;
    line-height: 1.5;
}
.privacy-box strong {
    color: #4A9EFF;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── Version tag ── */
.version-tag {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #3D4560;
    padding: 1rem;
    margin-top: auto;
}

/* ── Pixel art logo ── */
.pixel-art-container {
    background: #0a0d14;
    border: 1px solid rgba(74,158,255,0.25);
    border-radius: 12px;
    padding: 12px;
    display: inline-block;
    box-shadow: 0 0 24px rgba(74,158,255,0.12), inset 0 0 20px rgba(0,0,0,0.4);
}
.pixel-grid {
    display: grid;
    grid-template-columns: repeat(11, 10px);
    grid-template-rows: repeat(11, 10px);
    gap: 2px;
}
.px {
    width: 10px;
    height: 10px;
    border-radius: 2px;
}
.px-on {
    background: #4A9EFF;
    box-shadow: 0 0 6px rgba(74,158,255,0.7);
}
.px-off { background: transparent; }
.terminal-header {
    padding: 2.5rem 0 2rem 0;
    border-bottom: 1px solid #2D3141;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    gap: 2rem;
}
.terminal-logo {
    flex-shrink: 0;
}
.pixel-brain {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    line-height: 1.2;
    color: #4A9EFF;
    letter-spacing: 0.05em;
    background: rgba(74, 158, 255, 0.06);
    border: 1px solid rgba(74, 158, 255, 0.2);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    display: inline-block;
    white-space: pre;
    text-shadow: 0 0 12px rgba(74, 158, 255, 0.5);
}
.terminal-title {
    flex: 1;
}
.terminal-title h1 {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.02em;
}
.terminal-title h1 span {
    color: #4A9EFF;
}
.terminal-title p {
    color: #8B9CB6;
    font-size: 0.85rem;
    margin: 0 0 0.75rem 0;
    font-family: 'DM Mono', monospace;
}
.terminal-badges {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.t-badge {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.t-badge-blue { background: rgba(74,158,255,0.12); color: #4A9EFF; border: 1px solid rgba(74,158,255,0.25); }
.t-badge-green { background: rgba(0,196,140,0.1); color: #00C48C; border: 1px solid rgba(0,196,140,0.25); }
.t-badge-grey { background: rgba(139,156,182,0.1); color: #8B9CB6; border: 1px solid rgba(139,156,182,0.2); }

/* ── Inputs ── */
[data-testid="stTextArea"] textarea {
    background: #1E2130 !important;
    border: 1px solid #2D3141 !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    line-height: 1.6 !important;
    padding: 1rem !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #4A9EFF !important;
    box-shadow: 0 0 0 2px rgba(74, 158, 255, 0.15) !important;
}
[data-testid="stTextInput"] input {
    background: #1E2130 !important;
    border: 1px solid #2D3141 !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #1A1D24;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #2D3141;
    width: fit-content;
    margin-bottom: 1.25rem;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: #8B9CB6 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
    padding: 0.4rem 1rem !important;
    border: none !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: #4A9EFF !important;
    color: #FFFFFF !important;
}

/* ── Primary button ── */
[data-testid="stButton"] > button[kind="primary"] {
    background: #4A9EFF !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    padding: 0.75rem 2rem !important;
    width: 100% !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s ease !important;
    margin-top: 0.75rem !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #6AB2FF !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(74, 158, 255, 0.3) !important;
}

/* ── Secondary (copy) buttons ── */
[data-testid="stButton"] > button[kind="secondary"] {
    background: #1E2130 !important;
    color: #8B9CB6 !important;
    border: 1px solid #2D3141 !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    padding: 0.3rem 0.75rem !important;
}
[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: #4A9EFF !important;
    color: #4A9EFF !important;
}

/* ── Risk banner ── */
.risk-banner {
    background: rgba(255, 68, 68, 0.08);
    border: 2px solid #FF4444;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
    animation: pulse-border 2s ease-in-out infinite;
}
@keyframes pulse-border {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255, 68, 68, 0.2); }
    50% { box-shadow: 0 0 0 8px rgba(255, 68, 68, 0); }
}
.risk-banner h3 {
    color: #FF4444;
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    margin: 0 0 0.4rem 0;
    letter-spacing: 0.02em;
}
.risk-banner p {
    color: #FFB3B3;
    font-size: 0.85rem;
    margin: 0 0 0.75rem 0;
}
.risk-quote {
    background: rgba(255, 68, 68, 0.12);
    border-left: 3px solid #FF4444;
    border-radius: 4px;
    padding: 0.6rem 0.75rem;
    font-style: italic;
    font-size: 0.85rem;
    color: #FFD0D0;
}

/* ── Output cards ── */
.output-card {
    background: linear-gradient(145deg, #1E2130, #191C28);
    border: 1px solid #2D3141;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    height: 100%;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.output-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #4A9EFF, transparent);
    border-radius: 16px 16px 0 0;
}
.output-card:hover {
    border-color: rgba(74, 158, 255, 0.3);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3), 0 0 0 1px rgba(74,158,255,0.08);
}
.output-card h3 {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    color: #4A9EFF;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin: 0 0 1.25rem 0;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #2D3141;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.output-card .content {
    font-size: 0.88rem;
    line-height: 1.75;
    color: #C8D4E8;
    white-space: pre-wrap;
}
.soap-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    color: #4A9EFF;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 1rem 0 0.35rem 0;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.soap-label::before {
    content: '';
    display: inline-block;
    width: 6px;
    height: 6px;
    background: #4A9EFF;
    border-radius: 50%;
    opacity: 0.6;
}
.soap-content {
    font-size: 0.87rem;
    line-height: 1.75;
    color: #C8D4E8;
    margin-bottom: 0.25rem;
    padding: 0.6rem 0.85rem;
    background: rgba(255,255,255,0.03);
    border-left: 2px solid rgba(74,158,255,0.3);
    border-radius: 0 6px 6px 0;
}

/* ── Risk badge ── */
.badge-safe {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(0, 196, 140, 0.12);
    border: 1px solid #00C48C;
    color: #00C48C;
    border-radius: 20px;
    padding: 0.3rem 0.75rem;
    font-size: 0.78rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
}
.badge-risk {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(255, 68, 68, 0.12);
    border: 1px solid #FF4444;
    color: #FF4444;
    border-radius: 20px;
    padding: 0.3rem 0.75rem;
    font-size: 0.78rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
}

/* ── Session history ── */
.session-item {
    background: #12151E;
    border: 1px solid #2D3141;
    border-radius: 8px;
    padding: 0.6rem 0.75rem;
    margin-bottom: 0.5rem;
    cursor: pointer;
    font-size: 0.78rem;
    color: #8B9CB6;
    transition: all 0.15s;
}
.session-item:hover {
    border-color: #4A9EFF;
    color: #FFFFFF;
}
.session-time {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #3D4560;
}

/* ── Coming soon tab ── */
.coming-soon {
    background: #1A1D24;
    border: 1px dashed #2D3141;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    color: #3D4560;
    font-size: 0.85rem;
}
.coming-soon span {
    display: block;
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

/* ── Spinner override ── */
[data-testid="stSpinner"] { color: #4A9EFF !important; }

/* ── Selectbox / labels ── */
label, [data-testid="stWidgetLabel"] {
    color: #8B9CB6 !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}

/* ── Divider ── */
hr { border-color: #2D3141 !important; }

/* ── Expander (for copy sections) ── */
[data-testid="stExpander"] {
    border: 1px solid #2D3141 !important;
    border-radius: 8px !important;
    background: #12151E !important;
}
[data-testid="stExpander"] summary {
    color: #8B9CB6 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
}
</style>
""", unsafe_allow_html=True)


# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Admin Assassin — Clinical AI Scribe",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_css()

# ── Session state init ────────────────────────────────────────────────────────

if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h1>⚕ Admin Assassin</h1>
        <p>Clinical AI Scribe</p>
    </div>
    """, unsafe_allow_html=True)

    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")

    st.markdown("---")

    # New session button
    if st.session_state.last_result is not None:
        if st.button("+ New Session", use_container_width=True):
            st.session_state.last_result = None
            st.rerun()

    # Session history
    st.markdown(
        '<p style="font-size:0.72rem;color:#8B9CB6;letter-spacing:0.1em;'
        'text-transform:uppercase;margin-bottom:0.75rem;">Recent Sessions</p>',
        unsafe_allow_html=True,
    )

    if st.session_state.history:
        for i, session in enumerate(reversed(st.session_state.history[-5:])):
            if st.button(f"📋 Session {session['time']}", key=f"hist_{i}", use_container_width=True):
                st.session_state.last_result = session["result"]
    else:
        st.markdown(
            '<p style="font-size:0.78rem;color:#3D4560;font-style:italic;">No sessions yet</p>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    st.markdown("""
    <div class="privacy-box">
        <strong>🔒 Privacy Notice</strong><br><br>
        This tool processes anonymised transcripts only.
        All AI output requires clinician review before use.
        No patient data is stored or retained.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="version-tag">v1.0 — Beta</div>', unsafe_allow_html=True)

# ── Main panel header ────────────────────────────────────────────────────────

brain_html = render_pixel_brain()

st.markdown(f"""
<div class="terminal-header">
    <div class="terminal-logo">
        {brain_html}
    </div>
    <div class="terminal-title">
        <h1><span>Admin</span> Assassin</h1>
        <p>// privacy-first clinical scribe for CBT therapists</p>
        <div class="terminal-badges">
            <span class="t-badge t-badge-blue">Claude Opus</span>
            <span class="t-badge t-badge-green">CBT Clinical AI</span>
            <span class="t-badge t-badge-grey">v1.0 Beta</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input tabs ────────────────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["📝  Paste Transcript", "🎙  Upload Audio  (Coming in V2)"])

with tab1:
    transcript = st.text_area(
        label="Session Transcript",
        height=280,
        placeholder=(
            "Paste your session transcript here.\n\n"
            "For best results, include the full session dialogue.\n"
            "Patient name is not required — use initials or remove entirely."
        ),
        label_visibility="collapsed",
    )

    generate_btn = st.button("Generate Clinical Documentation", type="primary")

with tab2:
    st.markdown("""
    <div class="coming-soon">
        <span>🎙</span>
        Audio upload + Whisper transcription coming in V2.<br>
        Record directly in the therapy room — no laptop needed.
    </div>
    """, unsafe_allow_html=True)

# ── Generation logic ──────────────────────────────────────────────────────────

if generate_btn:
    if not api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
    elif not transcript.strip():
        st.error("Please paste a session transcript before generating.")
    else:
        with st.spinner("Analysing transcript..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                response = client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=8192,
                    system=SYSTEM_PROMPT,
                    messages=[
                        {"role": "user", "content": transcript}
                    ],
                )
                raw = response.content[0].text.strip()
                # Strip markdown fences if present
                if raw.startswith("```"):
                    raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
                result = json.loads(raw)
                st.session_state.last_result = result
                st.session_state.history.append({
                    "time": datetime.now().strftime("%H:%M"),
                    "result": result,
                })
                st.toast("Clinical documentation generated successfully.")
            except json.JSONDecodeError:
                st.error("The AI returned an unexpected format. Please try again.")
            except Exception as e:
                st.error(f"Error: {e}")

# ── Output rendering ──────────────────────────────────────────────────────────

if st.session_state.last_result:
    r = st.session_state.last_result

    # Risk banner
    if r.get("risk_detected"):
        st.markdown(f"""
        <div class="risk-banner">
            <h3>⚠️ CLINICAL RISK DETECTED — Review Required</h3>
            <p>The following content has been flagged. This requires immediate clinical review before proceeding.</p>
            <div class="risk-quote">"{safe(r.get('risk_content', 'Risk phrase not extracted'))}"</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top row: SOAP + GP Letter ─────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        soap = r.get("soap_note", {})
        st.markdown(f"""
        <div class="output-card">
            <h3>📋 SOAP Note</h3>
            <div class="soap-label">S — Subjective</div>
            <div class="soap-content">{safe(soap.get('subjective'))}</div>
            <div class="soap-label">O — Objective</div>
            <div class="soap-content">{safe(soap.get('objective'))}</div>
            <div class="soap-label">A — Assessment</div>
            <div class="soap-content">{safe(soap.get('assessment'))}</div>
            <div class="soap-label">P — Plan</div>
            <div class="soap-content">{safe(soap.get('plan'))}</div>
        </div>
        """, unsafe_allow_html=True)
        soap_text = (
            f"S: {soap.get('subjective', '')}\n"
            f"O: {soap.get('objective', '')}\n"
            f"A: {soap.get('assessment', '')}\n"
            f"P: {soap.get('plan', '')}"
        )
        with st.expander("📋 Copy SOAP Note"):
            st.code(soap_text, language=None)

    with col2:
        gp_letter = r.get("gp_letter", "")
        st.markdown(f"""
        <div class="output-card">
            <h3>✉️ GP Letter</h3>
            <div class="content">{safe(gp_letter)}</div>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("📋 Copy GP Letter"):
            st.code(gp_letter, language=None)

    # ── Bottom row: CBT Formulation + Risk Summary ────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.markdown(f"""
        <div class="output-card">
            <h3>🧠 CBT Formulation</h3>
            <div class="soap-label">Hot Thought</div>
            <div class="soap-content">{safe(r.get('hot_thought'))}</div>
            <div class="soap-label">Maintenance Cycle</div>
            <div class="soap-content">{safe(r.get('maintenance_cycle'))}</div>
            <div class="soap-label">Safety Behaviours</div>
            <div class="soap-content">{safe(r.get('safety_behaviours'))}</div>
        </div>
        """, unsafe_allow_html=True)
        formulation_text = (
            f"Hot Thought: {r.get('hot_thought', '')}\n\n"
            f"Maintenance Cycle: {r.get('maintenance_cycle', '')}\n\n"
            f"Safety Behaviours: {r.get('safety_behaviours', '')}"
        )
        with st.expander("📋 Copy Formulation"):
            st.code(formulation_text, language=None)

    with col4:
        risk_badge = (
            '<div class="badge-risk">⚠ Risk Detected</div>'
            if r.get("risk_detected")
            else '<div class="badge-safe">✓ No Risk Identified</div>'
        )
        risk_text = r.get("risk_summary", "—")
        st.markdown(f"""
        <div class="output-card">
            <h3>🛡 Risk Summary</h3>
            {risk_badge}
            <div class="content">{safe(risk_text)}</div>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("📋 Copy Risk Summary"):
            st.code(risk_text, language=None)
