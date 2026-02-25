import streamlit as st
import json
import anthropic
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Admin Assassin | Clinical Intelligence",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS (Linear/Vercel Aesthetic) ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Force Inter font everywhere */
html, body, [class*="css"], .stMarkdown, .stText {
    font-family: 'Inter', sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* Hide Streamlit Clutter */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stToolbar"] {display: none;}

/* Typography Classes */
.brand-title {
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.04em;
    margin-bottom: 0px;
}
.brand-subtitle {
    font-size: 0.85rem;
    font-weight: 400;
    color: #888888;
    letter-spacing: 0.02em;
    margin-bottom: 2rem;
}
.section-header {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #666666;
    margin-bottom: 1rem;
    border-bottom: 1px solid #333333;
    padding-bottom: 0.5rem;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #0E1117 !important;
    border-right: 1px solid #222222 !important;
}

/* Input Areas */
[data-testid="stTextArea"] textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    line-height: 1.6 !important;
    border-radius: 8px !important;
    border: 1px solid #333333 !important;
    background-color: #111111 !important;
    padding: 1rem !important;
    transition: all 0.2s ease;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 1px #3B82F6 !important;
}

/* Buttons */
.stButton>button {
    border-radius: 6px !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
    border: 1px solid #333333 !important;
    background-color: #1A1A1A !important;
    transition: all 0.2s ease;
}
.stButton>button:hover {
    border-color: #888888 !important;
    background-color: #222222 !important;
}
/* Primary Button Override */
.stButton>button[kind="primary"] {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: none !important;
    font-weight: 600 !important;
}
.stButton>button[kind="primary"]:hover {
    background-color: #E5E5E5 !important;
}

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 2rem;
    border-bottom: 1px solid #333333;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #888888 !important;
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    border-bottom: 2px solid transparent !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: #FFFFFF !important;
    border-bottom: 2px solid #FFFFFF !important;
}

/* Risk Banner */
.risk-alert {
    background-color: rgba(220, 38, 38, 0.1);
    border-left: 4px solid #DC2626;
    padding: 1rem 1.5rem;
    border-radius: 0 6px 6px 0;
    margin-bottom: 2rem;
}
.risk-alert-title {
    color: #EF4444;
    font-weight: 700;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.25rem;
}
.risk-alert-text {
    color: #FCA5A5;
    font-size: 0.9rem;
    font-family: 'JetBrains Mono', monospace;
}

/* Document Display Content */
.doc-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #666666;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 1.5rem;
    margin-bottom: 0.25rem;
}
.doc-content {
    font-size: 0.95rem;
    line-height: 1.6;
    color: #E2E8F0;
    white-space: pre-wrap;
    background: #111111;
    padding: 1rem;
    border: 1px solid #222222;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="brand-title">Admin Assassin</p>', unsafe_allow_html=True)
    st.markdown('<p class="brand-subtitle">Clinical Infrastructure v1.0</p>', unsafe_allow_html=True)

    _key_input = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...", value=st.session_state.api_key)
    if _key_input:
        st.session_state.api_key = _key_input
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown('<p class="section-header">Recent Sessions</p>', unsafe_allow_html=True)
    if st.session_state.history:
        for i, session in enumerate(reversed(st.session_state.history[-5:])):
            if st.button(f"Session {session['time']}", key=f"hist_{i}", use_container_width=True):
                st.session_state.last_result = session["result"]
    else:
        st.caption("No recent sessions.")

# ── Main panel ────────────────────────────────────────────────────────────────
st.markdown('<p class="brand-title" style="font-size: 2.25rem;">Clinical Intelligence Scribe</p>', unsafe_allow_html=True)
st.markdown('<p class="brand-subtitle" style="font-size: 1rem;">Generate supervision-quality CBT documentation from anonymised session transcripts.</p>', unsafe_allow_html=True)

# ── Input Area ────────────────────────────────────────────────────────────────
transcript = st.text_area(
    label="Transcript Input",
    height=300,
    placeholder="Paste session transcript here. Use initials only. Ensure full dialogue for accurate behavioural activation tracking...",
    label_visibility="collapsed"
)

_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    generate_btn = st.button("Generate Clinical Artifacts", type="primary", use_container_width=True)

# ── System prompt (UNCHANGED - MASTERCLASS CLINICAL LOGIC) ───────────────────
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
    if not st.session_state.api_key:
        st.error("Authentication Error: Missing Anthropic API Key.")
    elif not transcript.strip():
        st.error("Validation Error: Transcript input is empty.")
    else:
        with st.spinner("Executing Clinical Skill Graph Analysis..."):
            try:
                client = anthropic.Anthropic(api_key=st.session_state.api_key)
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022", # UPDATED TO CORRECT MODEL
                    max_tokens=8192,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": transcript}]
                )
                raw = response.content[0].text.strip()
                if raw.startswith("```"):
                    raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
                
                result = json.loads(raw)
                st.session_state.last_result = result
                st.session_state.history.append({
                    "time": datetime.now().strftime("%H:%M"),
                    "result": result
                })
            except json.JSONDecodeError:
                st.error("Processing Error: LLM returned invalid JSON structure.")
            except Exception as e:
                st.error(f"System Error: {str(e)}")

# ── Output rendering ──────────────────────────────────────────────────────────
if st.session_state.last_result:
    r = st.session_state.last_result
    st.markdown("<br><hr style='border-color: #333333;'><br>", unsafe_allow_html=True)

    # Risk Banner (Full width, top priority)
    if r.get("risk_detected"):
        st.markdown(f"""
        <div class="risk-alert">
            <div class="risk-alert-title">Critical Risk Detected</div>
            <div class="risk-alert-text">"{r.get('risk_content', 'Review transcript immediately.')}"</div>
        </div>
        """, unsafe_allow_html=True)

    # Clean Tabbed Interface
    tab_soap, tab_gp, tab_form, tab_risk = st.tabs([
        "📄 SOAP Note", 
        "🏥 GP Letter", 
        "🧠 CBT Formulation", 
        "🛡️ Risk Triage"
    ])

    with tab_soap:
        soap = r.get("soap_note", {})
        
        st.markdown('<div class="doc-label">Subjective</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="doc-content">{soap.get("subjective", "—")}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="doc-label">Objective</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="doc-content">{soap.get("objective", "—")}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="doc-label">Assessment</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="doc-content">{soap.get("assessment", "—")}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="doc-label">Plan</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="doc-content">{soap.get("plan", "—")}</div>', unsafe_allow_html=True)

    with tab_gp:
        st.markdown('<div class="doc-label">Generated Communication</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="doc-content">{r.get("gp_letter", "—")}</div>', unsafe_allow_html=True)

    with tab_form:
        st.markdown('<div class="doc-label">Primary Target</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="doc-content">{r.get("hot_thought", "—")}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="doc-label">Maintenance Cycle</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="doc-content">{r.get("maintenance_cycle", "—")}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="doc-label">Avoidance / Safety Behaviours</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="doc-content">{r.get("safety_behaviours", "—")}</div>', unsafe_allow_html=True)

    with tab_risk:
        status = "⚠️ Active Risk Documented" if r.get("risk_detected") else "✓ No Clinical Risk Identified"
        st.markdown(f'<div class="doc-label">Risk Status: {status}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="doc-content">{r.get("risk_summary", "—")}</div>', unsafe_allow_html=True)
