# Multi-Agent Orchestrator Architecture

> Documentation as load-bearing infrastructure, not reference material.

Companion document: [Context Engineering Principles](context_engineering_principles.md),
which explains *why* this architecture is shaped the way it is.

---

## The core principle

One transcript in. Multiple specialist agents activated. One unified clinical
package out.

The orchestrator never generates clinical content. It reads, classifies, routes,
and merges. The clinical intelligence lives entirely in the specialist agents and
their loaded nodes. The orchestrator is a receptionist, not a clinician.

---

## System flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        TRANSCRIPT IN                            │
│            (raw session audio → text via transcription)         │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    ORCHESTRATOR (Tier 1)                        │
│                    Always loaded. ~500 lines.                   │
│                                                                 │
│    ┌──────────────────────────────────────────────────────┐     │
│    │              TRIGGER TABLE                           │     │
│    │                                                      │     │
│    │  1. Safety scan        (FIRST — before all else)     │     │
│    │  2. Measure detection  (what scores are present?)    │     │
│    │  3. Condition routing  (what disorder is primary?)   │     │
│    │  4. Contextual flags   (session number, meds, etc)   │     │
│    │  5. Output assembly    (which outputs requested?)    │     │
│    └──────────────────────────────────────────────────────┘     │
│                                                                 │
│    Outputs: List of agents to invoke + loading order            │
│                                                                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                 SPECIALIST AGENTS (Tier 2)                      │
│            Invoked on demand. 3-6 active per session.           │
│                                                                 │
│    Each agent loads its own subset of skill graph nodes         │
│    Each agent processes the transcript independently            │
│    Each agent returns structured output in its domain           │
│                                                                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                 VERIFICATION GATE (Tier 3)                      │
│              Loaded LAST = freshest in memory.                  │
│                                                                 │
│    Checks merged output against non-negotiable rules            │
│    Uses DIFFERENT evaluation criteria than generation           │
│    Statistically independent verification layer                 │
│                                                                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     UNIFIED OUTPUT                              │
│                                                                 │
│    ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────────┐     │
│    │ SOAP Note│  │Formulation│  │GP Letter │  │Risk Triage│     │
│    └──────────┘  └───────────┘  └──────────┘  └───────────┘     │
│                                                                 │
│              Badge: "Awaiting Therapist Review"                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## The trigger table (detailed)

The trigger table is a **deterministic clinical decision tree** encoded as
routing logic. It is not probabilistic. It does not ask the model to decide. It
pattern-matches against the transcript and activates agents based on explicit
rules.

### Execution order matters

The trigger table processes in strict sequence. Safety first. Always.

---

### Step 1: Safety scan (priority override — runs first, every time)

**Agent:** Risk Agent
**Status:** Override — can interrupt any other agent's processing
**Nodes loaded:** `risk_assessment.md`, `dissociation_screening.md`

| Trigger pattern | Action | Override level |
|----------------|--------|----------------|
| Any mention of self-harm, suicide, suicidal ideation | INVOKE IMMEDIATELY | **CRITICAL** — halts normal flow |
| PHQ-9 Q9 score > 0 (any value) | INVOKE IMMEDIATELY | **CRITICAL** — regardless of total score |
| Harm to others, homicidal ideation | INVOKE IMMEDIATELY | **CRITICAL** |
| Client reports feeling "nothing," emotional numbness, detachment | INVOKE + flag dissociation screen | **HIGH** |
| Significant life event (bereavement, job loss, relationship breakdown) within last 4 weeks | INVOKE as precautionary | **MODERATE** |
| Sudden unexplained mood improvement after prolonged depression | INVOKE — possible resolution OR possible decision made | **HIGH** |
| Client cancelling multiple sessions, disengaging from treatment | INVOKE — possible withdrawal from help | **MODERATE** |

**Critical design rule:** the Risk Agent is the ONLY agent that can override all
others. If risk is detected at any point — even mid-processing by another agent —
the Risk Agent activates and its output takes priority position in the final
package.

**Why the last two triggers matter clinically:** a therapist would recognise
these as indirect risk indicators; generic AI would not. A sudden mood lift in a
chronically depressed client isn't always good news — it can indicate the
psychological relief of having made a decision to end their life. This is where
clinical training directly becomes system architecture.

---

### Step 2: Measurement detection (what scores are present?)

**Agent:** Measurement Agent
**Nodes loaded:** whichever scoring nodes match detected measures

| Trigger pattern | Nodes loaded |
|----------------|-------------|
| PHQ-9 score mentioned or scoreable | `PHQ9_scoring.md` |
| GAD-7 score mentioned or scoreable | `GAD7_scoring.md` |
| Y-BOCS score mentioned | `YBOCS_scoring.md` |
| PCL-5 score mentioned | `PCL5_scoring.md` |
| ISI / sleep diary data present | `ISI_scoring.md` + `sleep_diary.md` |
| PDSS score mentioned | `PDSS_scoring.md` |
| SPIN score mentioned | `SPIN_scoring.md` |
| RSES score mentioned | `RSES_scoring.md` |
| Any outcome measure trajectory (2+ sessions of data) | `outcome_monitoring.md` |

**Design note:** the Measurement Agent runs in parallel with condition routing.
Scores inform but don't determine condition routing — a client might have a GAD-7
score in a session primarily about depression if comorbidity is present.

---

### Step 3: Condition routing (what disorder is primary?)

The most complex routing step. A session may involve multiple conditions. The
orchestrator identifies the **primary** condition (drives the session's main
focus) and any **secondary** conditions (present but not the session's central
work).

**Agent:** condition-specific specialist agent(s)

| Trigger patterns — Depression | Agent | Nodes loaded |
|------------------------------|-------|-------------|
| PHQ-9 as primary measure | Depression Agent | All 8 depression nodes |
| Low mood, withdrawal, anhedonia, loss of interest | Depression Agent | All 8 depression nodes |
| Behavioural activation discussed, activity scheduling | Depression Agent | `behavioural_activation.md`, `pleasure_mastery_ratings.md` |
| Thought records focused on depressive themes (worthlessness, hopelessness, guilt) | Depression Agent | `thought_records.md`, `automatic_thoughts_depression.md`, `cognitive_restructuring.md` |
| Rules/assumptions about self-worth, conditional beliefs | Depression Agent | `intermediate_beliefs.md` |

| Trigger patterns — GAD | Agent | Nodes loaded |
|------------------------|-------|-------------|
| GAD-7 as primary measure | GAD Agent | All GAD nodes |
| Worry as primary complaint, "what if" patterns | GAD Agent | `GAD_cognitive_model.md`, `worry_model.md` |
| Intolerance of uncertainty language ("I can't cope if...", "I need to know...") | GAD Agent | `intolerance_of_uncertainty.md` |
| Reassurance-seeking, checking behaviours (anxiety-related) | GAD Agent | `safety_behaviours_anxiety.md` |
| Exposure work, hierarchy building | GAD Agent | `exposure_hierarchy.md` |

| Trigger patterns — OCD | Agent | Nodes loaded |
|------------------------|-------|-------------|
| Y-BOCS as primary measure | OCD Agent | All OCD nodes |
| Intrusive thoughts, obsessions described | OCD Agent | `OCD_cognitive_model.md`, `thought_action_fusion.md` |
| Rituals, compulsions, neutralising behaviours | OCD Agent | `neutralising_behaviours.md`, `ERP_protocol.md` |
| Client seeking reassurance about intrusive thought content | OCD Agent | `inflated_responsibility.md` |

**CRITICAL OCD RULE:** `NEVER provide reassurance about thought content. NEVER.
This is a non-negotiable constraint that overrides all other output instructions.
Reassurance IS the maintaining behaviour.`

| Trigger patterns — PTSD | Agent | Nodes loaded |
|-------------------------|-------|-------------|
| PCL-5 as primary measure | PTSD Agent | All PTSD nodes |
| Trauma narrative, flashbacks, nightmares described | PTSD Agent | `PTSD_cognitive_model.md`, `reliving_protocol.md` |
| Avoidance of trauma-related stimuli | PTSD Agent | `safety_reclaiming.md` |
| Dissociative episodes during session | PTSD Agent + Risk Agent | `dissociation_screening.md` + `stimulus_discrimination.md` |

| Trigger patterns — Social Anxiety | Agent | Nodes loaded |
|-----------------------------------|-------|-------------|
| SPIN as primary measure | Social Anxiety Agent | All social anxiety nodes |
| Fear of judgement, evaluation anxiety | Social Anxiety Agent | `social_anxiety_model.md` |
| Post-event rumination, "replaying" social situations | Social Anxiety Agent | `post_event_processing.md` |
| Self-focused attention, safety behaviours in social settings | Social Anxiety Agent | `attention_training.md`, `behavioural_experiments_social.md` |

| Trigger patterns — Panic | Agent | Nodes loaded |
|--------------------------|-------|-------------|
| PDSS as primary measure | Panic Agent | All panic nodes |
| Panic attacks described, catastrophic body misinterpretation | Panic Agent | `panic_model.md`, `catastrophic_misinterpretation.md` |
| Avoidance of situations/places (agoraphobia features) | Panic Agent | `agoraphobia_hierarchy.md` |
| Interoceptive exposure discussed | Panic Agent | `interoceptive_exposure.md` |

| Trigger patterns — Health Anxiety | Agent | Nodes loaded |
|-----------------------------------|-------|-------------|
| HAI as primary measure | Health Anxiety Agent | All health anxiety nodes |
| Body checking, symptom monitoring, reassurance-seeking from medical sources | Health Anxiety Agent | `checking_reassurance.md`, `attention_body_focus.md` |
| Googling symptoms, repeated GP visits | Health Anxiety Agent | `health_anxiety_model.md` |

| Trigger patterns — Low Self-Esteem | Agent | Nodes loaded |
|------------------------------------|-------|-------------|
| RSES as primary measure | Self-Esteem Agent | All self-esteem nodes |
| Core beliefs about self (worthless, unlovable, defective) | Self-Esteem Agent | `core_beliefs.md`, `low_self_esteem_model.md` |
| Rigid "rules for living" (if/then conditional assumptions) | Self-Esteem Agent | `rules_for_living.md` |
| Positive data logging, behavioural experiments for self-view | Self-Esteem Agent | `positive_data_log.md` |

| Trigger patterns — Insomnia/CBT-I | Agent | Nodes loaded |
|-----------------------------------|-------|-------------|
| ISI as primary measure | CBT-I Agent | All insomnia nodes |
| Sleep complaints as primary presenting problem | CBT-I Agent | `insomnia_model.md`, `sleep_restriction.md` |
| Sleep diary data present | CBT-I Agent | `sleep_diary.md`, `stimulus_control.md` |

---

### Step 4: Contextual flags (session-level metadata)

These agents load based on session context, not clinical content.

| Trigger | Agent/node loaded | Rationale |
|---------|-------------------|-----------|
| Session number known | Session Structure Agent (`session_structure_by_number.md`) | Session 1 priorities ≠ Session 8 priorities. Temporal awareness drives intervention relevance. |
| Any mention of medication (starting, stopping, changing, side effects) | Medication Awareness flag → loads `medication_awareness.md` | Not a full agent — a supplementary node loaded into whichever condition agent is primary. |
| Final session / discharge discussed | Ending Treatment Agent (`ending_treatment.md`) | Relapse prevention, blueprint, ending well. |
| Client from different cultural background flagged | Cultural Adaptation overlay (`cultural_adaptation.md`) | Supplementary node, not standalone agent. |
| Comorbidity detected (primary + secondary condition) | Comorbidity Router (`comorbidity_routing.md`) | Determines which condition takes priority and how agents coordinate. |
| Homework reviewed or set | Homework node loaded (`homework_design.md`) | Supplements primary condition agent. |

---

### Step 5: Output assembly

The orchestrator collects outputs from all active agents and assembles them into
the unified clinical package.

```
┌─────────────────────────────────────────────────────┐
│               OUTPUT ASSEMBLY RULES                 │
│                                                     │
│  1. Risk Triage section: ALWAYS first, ALWAYS       │
│     present (even if "No risk indicators detected") │
│                                                     │
│  2. SOAP Note: Primary condition agent generates    │
│     Subjective/Objective/Assessment/Plan.           │
│     Secondary condition agent contributes to        │
│     Assessment section only.                        │
│                                                     │
│  3. Formulation: Primary condition agent generates. │
│     Cross-references measurement trajectory.        │
│                                                     │
│  4. GP Letter: Documentation Agent generates using  │
│     SOAP + formulation as input. Uses consortium-   │
│     specific templates.                             │
│                                                     │
│  5. Session Fidelity (Layer 2 — if active):         │
│     Fidelity Agent evaluates transcript against     │
│     CTS-R criteria INDEPENDENTLY of clinical output.│
│                                                     │
│  6. Measurement Summary: Measurement Agent provides │
│     score, trajectory, RCI, clinical thresholds.    │
│                                                     │
│  FINAL: Badge — "Awaiting Therapist Review"         │
│  NOTHING is finalised without human approval.       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Agent inventory (current and planned)

| Agent | Nodes loaded | Status | Max context load |
|-------|-------------|--------|-----------------|
| **Risk Agent** | 2 nodes | Planned (Tier 1 priority) | ~200 lines |
| **Measurement Agent** | Up to 11 scoring nodes (loaded selectively) | Planned | ~150-400 lines depending on measures present |
| **Depression Agent** | 8 nodes | READY (Grade A) | ~800 lines |
| **GAD Agent** | 8 nodes | In development | ~800 lines est. |
| **OCD Agent** | 6 nodes | Planned | ~600 lines est. |
| **PTSD Agent** | 7 nodes | Planned | ~700 lines est. |
| **Social Anxiety Agent** | 5 nodes | Planned | ~500 lines est. |
| **Panic Agent** | 5 nodes | Planned | ~500 lines est. |
| **Health Anxiety Agent** | 4 nodes | Planned | ~400 lines est. |
| **Self-Esteem Agent** | 5 nodes | Planned | ~500 lines est. |
| **CBT-I Agent** | 6 nodes | Planned | ~600 lines est. |
| **Session Structure Agent** | 1 node | Planned | ~100 lines |
| **Documentation Agent** | 3 nodes (SOAP, GP letter, formulation) | Planned | ~300 lines |
| **Fidelity Agent (Socratic Mirror)** | CTS-R framework + supervision nodes | Planned (Layer 2) | ~400 lines |
| **Ending Treatment Agent** | 1 node | Planned | ~100 lines |

**Typical session load:** orchestrator (~500 lines) + 3-5 specialist agents
(~1,500-2,500 lines total) + verification gate (~300 lines) =
**~2,300-3,300 lines of context per session.**

Compare to: loading all 68 nodes simultaneously = **~6,800+ lines** crammed into
one context window with guaranteed attention degradation.

The multi-agent architecture keeps each agent's context window lean and focused.
No agent ever holds more than ~800 lines of clinical knowledge. Every agent
operates within the zone where attention mechanisms work reliably.

---

## Comorbidity handling

Real clients rarely present with a single clean diagnosis. The orchestrator must
handle overlap.

**Rule 1: primary condition drives session structure.** If a client has
depression AND GAD, and this session focused primarily on worry management, the
GAD Agent is primary and the Depression Agent is secondary.

**Rule 2: secondary agents contribute to Assessment only.** They don't generate
their own SOAP note. They add relevant observations to the primary agent's
Assessment section. ("Client also reports persistent low mood — PHQ-9 trajectory
suggests depression maintenance cycle remains active alongside GAD work.")

**Rule 3: comorbidity routing resolves conflicts.** If the Depression Agent and
GAD Agent produce contradictory formulation elements, the Comorbidity Router
applies clinical logic: which condition is maintaining which? Is the worry
driving the low mood, or is the low mood generating the worry?

**Rule 4: Risk Agent always supersedes.** If risk signals emerge from ANY
condition agent's processing, the Risk Agent activates regardless of what else is
happening.

---

## What this architecture enables

**Immediate:** one transcript → orchestrator routes → 2-3 agents process →
unified output in three tabs (SOAP, fidelity summary, patient mockup). Live demo,
~30 seconds processing.

**Medium term:** every real session processed refines the trigger table — each
case where routing was slightly wrong becomes a configuration fix.

**Production:** the multi-agent architecture scales to 68 nodes without
degradation. New conditions are added by creating new specialist agents with
their own nodes; the orchestrator just gets a new entry in the trigger table. No
existing agents need modification. Modular, extensible, clinically governed.

---

## Design questions and resolutions

Questions originally left open in this draft, now resolved by the
[Context Engineering Principles](context_engineering_principles.md):

1. **Agent communication:** agents never communicate directly. Cross-domain
   observations go into the `unresolved_items` block of the clinical handover
   XML, and the orchestrator routes accordingly.
2. **Multi-session awareness:** a per-client context file (~200-300 tokens) holds
   the current formulation, trajectory deltas, measurement series, and active
   flags. Updated as a contract-enforced requirement of every specialist agent.
3. **Stale documentation:** contract verification (`client_context_updated` +
   `update_delta`) prevents specification drift — an agent cannot complete
   without confirming memory sync.

Still open for future development:

4. **Confidence thresholds:** should the trigger table have confidence levels?
   ("Definite depression" vs "possible depression features" → different loading
   strategies.)
5. **Learning from corrections:** when a therapist overrides the system's output,
   how does that feedback improve the trigger table over time?
6. **Transcript quality:** how robust are trigger patterns against poor
   transcription quality? (Ambient recording in therapy rooms isn't studio
   quality.)
