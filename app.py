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

/* ── Keep sidebar toggle visible ── */
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    background: #1A1D24 !important;
    border: 1px solid #2D3141 !important;
    border-radius: 0 8px 8px 0 !important;
    color: #4A9EFF !important;
}
[data-testid="stSidebarCollapseButton"] {
    display: flex !important;
    visibility: visible !important;
    color: #8B9CB6 !important;
}

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
    <div class="sidebar-logo">
        <h1>⚕ Admin Assassin</h1>
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
        <strong>🔒 Privacy Notice</strong><br><br>
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
<div class="terminal-header">
    <div class="terminal-logo">
        <div class="pixel-art-container">
            <div class="pixel-grid">
                {brain_html}
            </div>
        </div>
    </div>
    <div class="terminal-title">
        <h1><span>Admin</span> Assassin</h1>
        <p>// privacy-first clinical scribe for CBT therapists</p>
        <div class="terminal-badges">
            <span class="t-badge t-badge-blue">Claude Sonnet</span>
            <span class="t-badge t-badge-green">CBT Clinical AI</span>
            <span class="t-badge t-badge-grey">v1.0 Beta</span>
        </div>
""", unsafe_allow_html=True)

# ── Input tabs ────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📝  Paste Transcript", "🎙  Upload Audio  (Coming in V2)"])

with tab1:
    transcript = st.text_area(
        label="Session Transcript",
        height=280,
        placeholder="Paste your session transcript here.\n\nFor best results, include the full session dialogue.\nPatient name is not required — use initials or remove entirely.",
        label_visibility="collapsed"
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
        st.error("⚠️ Please enter your OpenAI API key in the sidebar.")
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

    # Top row — SOAP + GP Letter
    col1, col2 = st.columns(2)

    with col1:
        soap = r.get("soap_note", {})
        soap_text = f"S: {soap.get('subjective','')}\nO: {soap.get('objective','')}\nA: {soap.get('assessment','')}\nP: {soap.get('plan','')}"
        st.markdown(f"""
        <div class="output-card">
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
        <div class="output-card">
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
        <div class="output-card">
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
        <div class="output-card">
            <h3>🛡 Risk Summary</h3>
            {risk_badge}
            <div class="content">{risk_text}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Copy Risk Summary", key="copy_risk"):
            st.code(risk_text, language=None)
