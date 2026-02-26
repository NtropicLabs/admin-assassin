import streamlit as st
import json
import html as html_lib
import anthropic
from datetime import datetime

# ── System Prompt ─────────────────────────────────────────────────────────────

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
KEY CONCEPT — PREDICTION ERROR: The gap between predicted and actual rating is the clinical data. A prediction of 0/10 with an actual of 2/10 is proof the depression lied. Flag this explicitly. If BA homework was reviewed: extract prediction vs actual, calculate prediction error, note clinical significance.

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
IMPORTANT DISTINCTIONS: Mind Reading + Fortune Telling together suggest Performance=Safety intermediate belief. Mental Filter = omission. Disqualifying the Positive = active rejection. Different interventions required. Brief CBT boundary: If same distortions appear across 3+ sessions without shift, flag for supervisor — may indicate deeper core belief work needed beyond Brief CBT scope.

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
1. DISCONFIRMATORY EVIDENCE: Actual exceeds predicted. Flag explicitly.
2. TASK CALIBRATION REVIEW: Actual matches predicted (low). Not failure — information.
3. INTERVENING FACTOR: Actual below predicted. Something disrupted. Explore next session.
THE HAPPY BIAS ERROR: Evaluating BA success on Pleasure alone. Validate Mastery first — always.

--- THOUGHT RECORDS ---
FIVE-COLUMN RECORD (Sessions 2-4): Situation | Mood (0-100%) | Automatic Thought + belief rating | Evidence For | Evidence Against. Detective Before Judge — do NOT add balanced thought too early.
SEVEN-COLUMN RECORD (Sessions 4+): Adds Column 6 (Balanced Thought + belief rating) and Column 7 (Mood Re-Rating).
COLUMN 7 — EMOTIONAL DELTA: The ONLY column proving whether cognitive work landed.
- Significant drop (>20 points): Genuine cognitive shift.
- Minimal drop (<10 points): HEAD-HEART DISCREPANCY — intellectual insight without emotional change.
- No drop: Wrong thought targeted, or intermediate belief regenerating.
HOT THOUGHT: First thought named is often not the hot thought. Signal: belief rating below 70%, minimal delta. Probe: "Was there something even more distressing going through your mind?"

--- COGNITIVE RESTRUCTURING ---
THREE-PHASE STRUCTURE:
PHASE 1 — VALIDATION: Validate before examining. Without this, Socratic questioning feels like interrogation. Flag absence as fidelity gap.
PHASE 2 — SOCRATIC QUESTIONING: Evidence retrieval, not leading questions.
- Leading (wrong): "But you did a good job, didn't you?"
- Socratic (correct): "If your closest friend had this thought, what would you tell them?"
PHASE 3 — SYNTHESIS: Balanced thought from both sides of evidence. Must acknowledge kernel of truth. Check belief rating — if low, return to Phase 2.
EMOTIONAL DELTA: Calculate and classify. Head-Heart Discrepancy causes: wrong thought, insufficient evidence, intermediate belief regenerating.

--- INTERMEDIATE BELIEFS ---
Cross-session pattern detection. Same core theme across 3+ different situations = probable intermediate belief.
IF-THEN STRUCTURE: "If [condition] → Then [feared consequence]"
FOUR THEMES:
1. PERFORMANCE = SAFETY: "I must be competent at all times to have value."
2. VULNERABILITY = REJECTION: "Showing need will cause others to abandon me."
3. RESPONSIBILITY = WORTH: "If I cannot manage independently, I am a failure."
4. EFFORT = IDENTITY: "My value is determined by what I produce."
RUNNING CODE FRAMING: Externalise as a rule the brain executes — not a character defect.
BRIEF CBT BOUNDARY: 8 sessions can loosen, not dismantle. Schema work requires longer-term therapy.

=== OUTPUT INSTRUCTIONS ===
Return ONLY raw JSON — no markdown, no backticks, no preamble:
{
  "risk_detected": true or false,
  "risk_content": "exact quoted phrase from transcript if risk detected, else null",
  "hot_thought": "the primary automatic thought identified, labelled with its distortion type",
  "maintenance_cycle": "which specific permission-giving cognitions are present and how they function in this client's cycle",
  "safety_behaviours": "specific safety behaviours and avoidance patterns identified, else 'None identified'",
  "soap_note": {
    "subjective": "client's reported experience in their own words, including PHQ-9 verbal statements and language around mood, activity, motivation",
    "objective": "PHQ-9 score with assessment delta, session delta, RCI status. Any Q9 score. BA homework completion. Observable clinical data.",
    "assessment": "full CBT formulation — maintenance cycle mechanisms named, distortions labelled, trajectory interpretation, intermediate belief patterns, BA prediction error data",
    "plan": "interventions used, BA task set with prediction recorded, next session targets, risk management actions, unaddressed cognitive targets flagged"
  },
  "gp_letter": "full NHS Talking Therapies style GP letter — include risk disclosure if present, PHQ-9 trajectory, clinical formulation summary, recommended actions",
  "risk_summary": "clinical risk documentation — Q9 status, ideation content quoted, safety plan status, risk level, recommended actions"
}"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def safe(text):
    """Escape HTML entities in AI-generated text to prevent XSS."""
    if text is None:
        return "—"
    return html_lib.escape(str(text))


def inject_css():
    """Inject all custom CSS into the Streamlit app."""
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main,
.block-container {
    background-color: #0E1117 !important;
    color: #E2E8F0;
    font-family: 'Inter', sans-serif;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Sidebar toggle must stay visible ── */
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #0D1117 !important;
    border-right: 1px solid #21262D;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}

/* ── Sidebar brand ── */
.sidebar-brand {
    padding: 0 1rem 1.5rem 1rem;
    border-bottom: 1px solid #21262D;
    margin-bottom: 1.5rem;
}
.sidebar-brand h2 {
    font-family: 'Inter', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #E2E8F0;
    margin: 0 0 0.2rem 0;
    letter-spacing: -0.01em;
}
.sidebar-brand p {
    font-size: 0.72rem;
    color: #484F58;
    margin: 0;
    font-family: 'Inter', sans-serif;
}

/* ── Sidebar section labels ── */
.sidebar-section-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    font-weight: 600;
    color: #8B949E;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 0 0 0.6rem 0;
    padding: 0 0.25rem;
}

/* ── Privacy box ── */
.privacy-box {
    background: #0D1117;
    border: 1px solid rgba(88, 166, 255, 0.2);
    border-radius: 6px;
    padding: 0.75rem;
    margin: 1.5rem 0 1rem 0;
    font-size: 0.72rem;
    color: #8B949E;
    line-height: 1.6;
    font-family: 'Inter', sans-serif;
}

/* ── Version tag ── */
.version-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #484F58;
    padding: 1rem;
}

/* ── Page header ── */
.page-header {
    padding: 2.5rem 0 2rem 0;
    border-bottom: 1px solid #21262D;
    margin-bottom: 2rem;
}
.page-header h1 {
    font-family: 'Inter', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #E2E8F0;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.03em;
}
.page-header p {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    font-weight: 400;
    color: #8B949E;
    margin: 0 0 1.25rem 0;
    line-height: 1.5;
}
.badge-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.chip {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 500;
    color: #8B949E;
    background: #0D1117;
    border: 1px solid #21262D;
    border-radius: 4px;
    padding: 0.2rem 0.6rem;
    letter-spacing: 0.01em;
}

/* ── Inputs ── */
[data-testid="stTextArea"] textarea {
    background: #0D1117 !important;
    border: 1px solid #21262D !important;
    border-radius: 6px !important;
    color: #E2E8F0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    line-height: 1.6 !important;
    padding: 1rem !important;
}
[data-testid="stTextArea"] textarea::placeholder {
    color: #484F58 !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #30363D !important;
    outline: none !important;
    box-shadow: none !important;
}
[data-testid="stTextInput"] input {
    background: #0D1117 !important;
    border: 1px solid #21262D !important;
    border-radius: 6px !important;
    color: #E2E8F0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
}
[data-testid="stTextInput"] input::placeholder {
    color: #484F58 !important;
}

/* ── Tabs — underline only, no background ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #21262D;
    gap: 0;
    padding: 0;
    margin-bottom: 1.5rem;
}
[data-baseweb="tab-highlight"] { display: none !important; }
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: #8B949E !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    border-radius: 0 !important;
    padding: 0.6rem 1rem !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    transition: color 0.15s ease !important;
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: #E2E8F0 !important;
    background: transparent !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: transparent !important;
    color: #FFFFFF !important;
    border-bottom: 2px solid #FFFFFF !important;
}

/* ── Primary button — white bg, black text ── */
[data-testid="stButton"] > button[kind="primary"] {
    background: #FFFFFF !important;
    color: #0D1117 !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    padding: 0.65rem 1.5rem !important;
    width: 100% !important;
    letter-spacing: -0.01em !important;
    transition: background 0.15s ease !important;
    box-shadow: none !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #F0F0F0 !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Secondary (copy) buttons ── */
[data-testid="stButton"] > button[kind="secondary"] {
    background: #0D1117 !important;
    color: #8B949E !important;
    border: 1px solid #21262D !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 0.35rem 0.85rem !important;
    transition: border-color 0.15s, color 0.15s !important;
}
[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: #30363D !important;
    color: #E2E8F0 !important;
}

/* ── Risk banner ── */
.risk-banner {
    background: rgba(239, 68, 68, 0.06);
    border-left: 4px solid #EF4444;
    border-radius: 0 6px 6px 0;
    padding: 1rem 1.25rem;
    margin-bottom: 1.5rem;
}
.risk-banner-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.82rem;
    font-weight: 600;
    color: #EF4444;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin: 0 0 0.5rem 0;
}
.risk-banner-phrase {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: #FCA5A5;
    margin: 0;
    line-height: 1.5;
}

/* ── Doc card wrapper ── */
.doc-card {
    background: #0D1117;
    border: 1px solid #21262D;
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
}

/* ── Doc label ── */
.doc-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.67rem;
    font-weight: 600;
    color: #8B949E;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0 0 0.5rem 0;
}

/* ── Doc content ── */
.doc-content {
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    font-weight: 400;
    line-height: 1.75;
    color: #E2E8F0;
    white-space: pre-wrap;
    margin: 0;
}

/* ── Coming soon ── */
.coming-soon {
    background: #0D1117;
    border: 1px dashed #21262D;
    border-radius: 8px;
    padding: 3rem 2rem;
    text-align: center;
    color: #484F58;
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
}
.coming-soon-icon {
    font-size: 1.5rem;
    display: block;
    margin-bottom: 0.75rem;
}

/* ── Divider ── */
hr { border-color: #21262D !important; }

/* ── Streamlit labels ── */
label, [data-testid="stWidgetLabel"] {
    color: #8B949E !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

/* ── Clinical footer ── */
.clinical-footer {
    margin-top: 3rem;
    padding: 1.25rem 0 2rem 0;
    border-top: 1px solid #21262D;
    text-align: center;
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    color: #484F58;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)


# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Admin Assassin — Clinical AI Scribe",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ── Session state init ────────────────────────────────────────────────────────

if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "show_copy" not in st.session_state:
    st.session_state.show_copy = {}

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>Admin Assassin</h2>
        <p>Clinical Infrastructure v1.0</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="sidebar-section-label">API Configuration</p>', unsafe_allow_html=True)
    api_key_input = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        value=st.session_state.api_key,
        label_visibility="collapsed",
    )
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="sidebar-section-label">Recent Sessions</p>', unsafe_allow_html=True)

    if st.session_state.history:
        for i, session in enumerate(reversed(st.session_state.history[-5:])):
            if st.button(f"Session · {session['time']}", key=f"hist_{i}", use_container_width=True):
                st.session_state.last_result = session["result"]
                st.rerun()
    else:
        st.markdown(
            '<p style="font-size:0.8rem;color:#484F58;font-style:italic;padding:0 0.25rem;">No recent sessions.</p>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="privacy-box">
        This tool processes anonymised transcripts only.
        All AI output requires clinician review before use.
        No patient data is stored or retained.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="version-tag">v1.0 — Beta</div>', unsafe_allow_html=True)

# ── Main panel header ─────────────────────────────────────────────────────────

st.markdown("""
<div class="page-header">
    <h1>Clinical Intelligence Scribe</h1>
    <p>Generate supervision-quality CBT documentation from anonymised session transcripts in under 30 seconds.</p>
    <div class="badge-row">
        <span class="chip">Claude Sonnet</span>
        <span class="chip">CBT Formulation Engine</span>
        <span class="chip">8-Node Skill Graph</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input tabs ────────────────────────────────────────────────────────────────

tab_input1, tab_input2 = st.tabs(["Text Transcript", "Audio Upload (V2)"])

with tab_input1:
    transcript = st.text_area(
        label="Session Transcript",
        height=320,
        placeholder="Paste your anonymised session transcript here. Use initials only — no full patient names.",
        label_visibility="collapsed",
    )

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        generate_btn = st.button("Generate Clinical Artifacts", type="primary", use_container_width=True)

with tab_input2:
    st.markdown("""
    <div class="coming-soon">
        <span class="coming-soon-icon">🎙</span>
        Audio upload + Whisper transcription coming in V2.<br>
        Record directly in the therapy room — no laptop needed.
    </div>
    """, unsafe_allow_html=True)

# ── Generation logic ──────────────────────────────────────────────────────────

if generate_btn:
    if not st.session_state.api_key:
        st.error("Authentication Error: Missing Anthropic API Key.")
    elif not transcript.strip():
        st.error("Validation Error: Transcript input is empty.")
    else:
        with st.spinner("Executing Clinical Skill Graph Analysis..."):
            try:
                client = anthropic.Anthropic(api_key=st.session_state.api_key)
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=8192,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": transcript}],
                )
                raw = response.content[0].text.strip()
                if raw.startswith("```"):
                    raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
                result = json.loads(raw)
                st.session_state.last_result = result
                st.session_state.history.append({
                    "time": datetime.now().strftime("%H:%M"),
                    "result": result,
                })
                st.session_state.show_copy = {}
            except json.JSONDecodeError:
                st.error("Processing Error: The model returned an unexpected format. Please try again.")
            except Exception as e:
                st.error(f"System Error: {str(e)}")

# ── Output rendering ──────────────────────────────────────────────────────────

if st.session_state.last_result:
    r = st.session_state.last_result

    st.markdown("<hr>", unsafe_allow_html=True)

    # Risk banner
    if r.get("risk_detected"):
        risk_phrase = safe(r.get("risk_content", "Risk phrase not extracted"))
        st.markdown(f"""
        <div class="risk-banner">
            <p class="risk-banner-title">⚠ Clinical Risk Detected — Immediate Review Required</p>
            <p class="risk-banner-phrase">"{risk_phrase}"</p>
        </div>
        """, unsafe_allow_html=True)

    # 4 output tabs
    tab_soap, tab_gp, tab_cbt, tab_risk = st.tabs(["SOAP Note", "GP Letter", "CBT Formulation", "Risk Triage"])

    with tab_soap:
        soap = r.get("soap_note", {})
        soap_text = (
            f"S: {soap.get('subjective', '')}\n\n"
            f"O: {soap.get('objective', '')}\n\n"
            f"A: {soap.get('assessment', '')}\n\n"
            f"P: {soap.get('plan', '')}"
        )
        st.markdown(f"""
        <div class="doc-card">
            <p class="doc-label">S — Subjective</p>
            <p class="doc-content">{safe(soap.get('subjective'))}</p>
        </div>
        <div class="doc-card">
            <p class="doc-label">O — Objective</p>
            <p class="doc-content">{safe(soap.get('objective'))}</p>
        </div>
        <div class="doc-card">
            <p class="doc-label">A — Assessment</p>
            <p class="doc-content">{safe(soap.get('assessment'))}</p>
        </div>
        <div class="doc-card">
            <p class="doc-label">P — Plan</p>
            <p class="doc-content">{safe(soap.get('plan'))}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Copy SOAP Note", key="copy_soap"):
            st.code(soap_text, language=None)

    with tab_gp:
        gp_letter = r.get("gp_letter", "")
        st.markdown(f"""
        <div class="doc-card">
            <p class="doc-label">GP Correspondence Draft</p>
            <p class="doc-content">{safe(gp_letter)}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Copy GP Letter", key="copy_gp"):
            st.code(gp_letter, language=None)

    with tab_cbt:
        st.markdown(f"""
        <div class="doc-card">
            <p class="doc-label">Hot Thought</p>
            <p class="doc-content">{safe(r.get('hot_thought'))}</p>
        </div>
        <div class="doc-card">
            <p class="doc-label">Maintenance Cycle</p>
            <p class="doc-content">{safe(r.get('maintenance_cycle'))}</p>
        </div>
        <div class="doc-card">
            <p class="doc-label">Safety Behaviours</p>
            <p class="doc-content">{safe(r.get('safety_behaviours'))}</p>
        </div>
        """, unsafe_allow_html=True)
        formulation_text = (
            f"Hot Thought: {r.get('hot_thought', '')}\n\n"
            f"Maintenance Cycle: {r.get('maintenance_cycle', '')}\n\n"
            f"Safety Behaviours: {r.get('safety_behaviours', '')}"
        )
        if st.button("Copy Formulation", key="copy_cbt"):
            st.code(formulation_text, language=None)

    with tab_risk:
        risk_status = "⚠ Risk Detected" if r.get("risk_detected") else "✓ No Risk Identified"
        risk_colour = "#EF4444" if r.get("risk_detected") else "#10B981"
        risk_text = r.get("risk_summary", "—")
        st.markdown(f"""
        <div class="doc-card">
            <p class="doc-label">Risk Status</p>
            <p class="doc-content" style="color:{risk_colour};font-weight:600;">{risk_status}</p>
        </div>
        <div class="doc-card">
            <p class="doc-label">Risk Summary</p>
            <p class="doc-content">{safe(risk_text)}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Copy Risk Summary", key="copy_risk"):
            st.code(risk_text, language=None)

st.markdown("""
<div class="clinical-footer">
    All output requires clinician review before use. Admin Assassin does not store patient data.
</div>
""", unsafe_allow_html=True)
