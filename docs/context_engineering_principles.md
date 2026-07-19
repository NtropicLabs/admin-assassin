# Context Engineering Principles for Clinical AI

Five architectural principles derived from Anthropic's guide to effective context
engineering, grounded in the mechanics of how LLMs process information, and applied
to Admin Assassin's multi-agent orchestrator architecture.

> **The governing insight:** context is a finite resource with diminishing marginal
> returns. Like a therapist's working memory, the model's attention budget is
> depleted by every token introduced. The entire Admin Assassin architecture — the
> orchestrator, the trigger table, the specialist agents, the verification gate —
> exists to ensure that budget is spent on clinical reasoning, not wasted on
> irrelevant information.

## Why context engineering defines clinical AI quality

Admin Assassin transforms a therapy session transcript into structured clinical
outputs: SOAP notes, GP letters, CBT formulations, and risk triage. The engine
powering this transformation is a hand-authored Clinical Skill Graph — markdown
nodes encoding supervision-quality CBT knowledge that guide AI models through
clinical reasoning.

The quality of every clinical output depends on one principle: **what the model
sees determines what it produces.** Context engineering is the discipline of
curating the optimal set of tokens during inference so that clinically correct
output becomes the most statistically likely result.

Each principle below addresses a specific failure mode with a specific engineering
response.

---

## Principle 1: Context Rot Mitigation

**The problem.** As the number of tokens in the context window increases, the
model's ability to accurately recall and follow instructions decreases — *context
rot*. Attention mechanisms do not treat all tokens equally: content at the
beginning and end of the context window receives disproportionate attention
weight, while content in the middle is progressively ignored (the "lost in the
middle" effect).

**The clinical risk.** Loading all 68 skill graph nodes simultaneously would
produce roughly 6,800 lines of context. At that volume, critical clinical
instructions positioned mid-context — such as "NEVER provide reassurance to OCD
clients" — would receive diminished attention weight. The model would not
deliberately ignore the instruction; it would statistically fail to attend to it.
The output would look syntactically correct but be clinically wrong.

### Mitigation strategies

**1.1 Multi-agent architecture as primary defence.** The orchestrator routes each
transcript to 3–6 specialist agents, each loading only the nodes relevant to the
clinical presentation. A typical session loads 2,300–3,300 lines of context across
all agents, versus 6,800+ if loaded simultaneously. No single agent ever holds
more than ~800 lines of clinical knowledge, keeping every agent within the zone
where attention mechanisms function reliably.

**1.2 Instruction positioning within specialist agents.** Content is ordered to
exploit the attention mechanism's bias:

- **Top of context:** safety constraints and completion contract — always attended
  to due to primacy bias.
- **Middle of context:** clinical nodes — reference material processed during
  chain-of-thought reasoning.
- **Bottom of context:** output format specification and NEVER/ALWAYS rules
  repeated — caught by recency bias.

Critical rules appear twice — beginning and end — sandwiching the clinical
knowledge.

**1.3 Tool result clearing.** After a specialist agent completes the Extract step
of its reasoning chain, the raw node content has been processed into extracted
data points. The full node text remaining in context consumes attention budget
without adding value, so it is compressed or cleared, keeping only the extracted
clinical signals. This reduces each agent's working context from ~800 lines to
300–400 lines during the reasoning-intensive Categorise, Contradict, and
Synthesise steps — roughly 40% less attention budget spent than without clearing.

**1.4 Deterministic trigger table.** The orchestrator's trigger table uses pattern
matching, not probabilistic model inference, to determine which agents to invoke.
This removes the most safety-critical routing decision from the context-sensitive
domain entirely. A missed trigger pattern is a configuration error that can be
fixed. A model failing to notice a risk signal due to context rot is a silent,
unpredictable clinical failure.

---

## Principle 2: Rules Versus Examples Decision Framework

**The problem.** Stuffing a laundry list of edge cases into a prompt degrades
under context load; curated canonical examples portray expected behaviour more
effectively. For clinical AI, however, some instructions are safety-critical and
cannot be softened into examples. The challenge is knowing which is which.

### The decision framework

| Feature | Keep as Rule (ALWAYS/NEVER) | Convert to Example (Few-Shot) |
| --- | --- | --- |
| Complexity | Simple, binary, imperative | Nuanced, multi-factor, descriptive |
| Risk profile | Safety-critical, non-negotiable | Quality-focused, optimisation |
| Failure mode | Prevents hallucinations and safety errors | Prevents generic or "vibe" output |
| Context position | Start and end of context (hot memory) | Within specialist nodes (warm memory) |

### Rules: the clinical constitution

Explicit ALWAYS/NEVER constraints live in the orchestrator's always-loaded
context, active regardless of which specialist agents are invoked:

- **Safety triggers:** "ALWAYS load `risk_assessment.md` when suicidal ideation is
  detected." Binary gate — no interpretation required.
- **System boundaries:** "NEVER provide a formal medical diagnosis."
- **Clinical non-negotiables:** "NEVER provide reassurance about intrusive thought
  content to OCD clients." Reassurance IS the maintaining behaviour.
- **Risk language:** "NEVER use softening language in risk assessments." A hedged
  risk flag is worse than no flag — it creates false confidence.

### Examples: Symptom-Cause-Fix tables

Complex clinical nuances are encoded as canonical examples embedded within
specialist agent nodes, serving as few-shot patterns that override the model's
training-data defaults:

| What the client says | Generic misinterpretation | Correct clinical reasoning |
| --- | --- | --- |
| "I'll do it when I feel more like myself" | Client is unmotivated | Mood-First Fallacy: client reversing cause and effect of motivation and action. BA rationale may need revisiting. |
| Patient stops doing homework | Patient is non-compliant | Signal of clinical plateau, low activation, or homework not graded to current ability level. |
| Rapid improvement in week 1 | Treatment is working | Possible placebo effect, honeymoon period, or therapeutic relationship effect. Monitor for sustainability. |
| "If I can't do it properly, I'm not touching it" | Client has high standards | False Binary: all-or-nothing permission structure maintaining avoidance. Graded task assignment indicated. |

### Verification gate: canonical good and canonical bad

The Tier 3 verification gate loads last in context (exploiting recency bias) and
contains both a "Canonical Good" and a "Canonical Bad" example output. The
Canonical Bad example is the more important one for clinical AI: it shows what a
superficially competent but clinically wrong output looks like — a SOAP note that
uses correct vocabulary but misses the maintenance cycle, a formulation that
reverses the causal direction. This zeros out the probability region where
generic-but-wrong outputs live.

---

## Principle 3: Specialist Agent Prompt Calibration

**The problem.** Prompt calibration spans a spectrum from "too specific" (brittle
if-else hardcoded prompts) to "too vague" (prompts that assume shared context).
The trigger table sits toward the specific end by design — deterministic routing
must be explicit. Specialist agent system prompts must occupy the "just right"
middle zone: concrete enough to guide clinical reasoning, flexible enough to
handle varied real-world transcripts.

### 3.1 Persona as thinking pattern, not job title

**Wrong:** "You are an expert in Major Depressive Disorder." A credential, not a
cognitive approach.

**Right:** "You analyse therapy transcripts through the lens of
cognitive-behavioural maintenance cycles. Your primary task is identifying which
behaviours provide short-term relief while maintaining the depressive cycle
long-term, and documenting these patterns in structured clinical output."

### 3.2 Pre-loaded nodes, not self-loading triggers

Specialist agents receive their clinical nodes pre-loaded by the orchestrator.
They never decide what to load. If a Depression Agent encounters potential OCD
patterns mid-transcript, it does not load OCD nodes — it flags the observation in
its unresolved items for the orchestrator to route.

> **Why this matters for patient safety.** If specialist agents could self-load
> nodes, a Depression Agent might fail to load `risk_assessment.md` when
> encountering a subtle indirect risk signal — precisely because the model's
> jagged intelligence makes such misses unpredictable. Deterministic loading via
> the trigger table removes this probabilistic failure point entirely.

### 3.3 Chain-of-thought as Extract → Categorise → Contradict → Synthesise

Each token is one forward pass through the network with a fixed computational
budget; complex clinical judgements cannot be compressed into a single forward
pass. The four-step decomposition structures each specialist agent's reasoning:

- **Extract:** surface raw data from the transcript into context as tokens. "List
  all behaviours the client described this session." This moves information from
  vague parametric recollection into high-fidelity working memory.
- **Categorise:** intermediate sorting. "Identify which behaviours provide
  short-term relief and which represent engagement or activation."
- **Contradict:** force disconfirming evidence into the token stream. "What
  evidence from this session suggests the maintenance cycle may NOT be operating
  as formulated?" This breaks confirmatory bias.
- **Synthesise:** integrate confirming and disconfirming evidence. "Given both,
  state the current status of the maintenance cycle and flag any formulation
  revisions needed."

The Contradict step is the architectural equivalent of a supervisor asking
"What's the evidence against your formulation?" Without it, sycophantic tendencies
cause each reasoning token to confirm earlier tokens, creating an echo chamber.

---

## Principle 4: Clinical Handover Output Format

**The problem.** Specialist agents perform extensive internal reasoning
(potentially tens of thousands of tokens) but must return only a condensed
summary to the orchestrator. If the orchestrator receives raw reasoning,
intermediate hypotheses, and full node content alongside the clinical
conclusions, its own context window suffers from the same rot the multi-agent
architecture was designed to prevent.

### The clinical handover XML structure

Each specialist agent returns a structured XML handover containing only
high-signal distilled output:

```xml
<clinical_handover>
  <specialist_id>Depression_Agent_V2</specialist_id>
  <formulation_summary>
    <!-- 1,000–2,000 tokens of clinical synthesis:
         current maintenance cycle, intervention status,
         measurement trajectory interpretation -->
  </formulation_summary>
  <risk_flags>
    <!-- Binary safety-critical signals:
         Q9 status, self-harm mentions, indirect indicators -->
  </risk_flags>
  <contract_verification>
    <maintenance_cycle_assessed>true</maintenance_cycle_assessed>
    <phq9_trajectory_noted>true</phq9_trajectory_noted>
    <behavioural_activation_status>documented</behavioural_activation_status>
    <never_constraints_passed>true</never_constraints_passed>
    <client_context_updated>true</client_context_updated>
    <update_delta>
      Formulation unchanged. PHQ-9 added: 12.
      Treatment goal 1 progress: 2x football this week.
    </update_delta>
  </contract_verification>
  <formulation_confidence>
    <evidence_base>strong — multiple transcript references</evidence_base>
    <contradict_outcome>disconfirming evidence considered,
      formulation held</contradict_outcome>
  </formulation_confidence>
  <unresolved_items>
    <!-- Cross-domain flags for orchestrator routing, e.g.
         "Detected possible intrusive thought pattern at
          minute 23 — may warrant OCD assessment" -->
  </unresolved_items>
</clinical_handover>
```

### Component functions

- **Formulation summary:** the distilled clinical product. What the Documentation
  Agent uses to generate SOAP notes and GP letters.
- **Risk flags:** binary safety signals the orchestrator and verification gate
  check immediately. Risk flags from any agent take priority in final assembly.
- **Contract verification:** self-attestation against the agent's completion
  contract. If any field is false, the orchestrator triggers a correction loop —
  re-invoking the agent with a specific prompt targeting the gap.
- **Client context updated:** structural requirement confirming the agent updated
  the cross-session memory file. Load-bearing, not optional — if stale, the next
  session's agents reason from wrong premises.
- **Formulation confidence:** indicates whether the Contradict step found genuine
  tension. A formulation that survived challenge is more trustworthy than one
  that went unchallenged.
- **Unresolved items:** cross-domain observations the agent cannot act on. Agents
  do not communicate directly — they flag observations in their handover and the
  orchestrator routes accordingly.

**What stays internal (never reaches the orchestrator):** raw node content after
processing, discarded exploratory hypotheses, intermediate Extract and Categorise
tokens, Symptom-Cause-Fix table iterations. The specialist's internal
chain-of-thought is working memory, not output.

---

## Principle 5: Cross-Session Memory Architecture

**The problem.** A single therapy session exists within a treatment arc of 6–20
sessions. The formulation evolves; measurement trajectories reveal patterns
invisible in any single score; treatment goals shift. Without cross-session
memory, each session is processed in clinical isolation — the AI equivalent of a
therapist who has never met this client before.

### The client context file

Each client receives a lean structured context file containing the current
clinical picture in ~200–300 tokens, loaded by the orchestrator alongside each
new transcript:

```xml
<client_context>
  <current_formulation>
    Maintenance cycle: low mood → withdrawal from social
    contact → reduced positive reinforcement → increased
    rumination → lower mood. Primary permission structure:
    Mood-First Fallacy.
  </current_formulation>
  <formulation_trajectory>
    Session 3: Added rumination loop (previously unidentified)
    Session 5: Permission structure shifted from Predictive
    Apathy to Mood-First Fallacy following BA rationale work
  </formulation_trajectory>
  <measurement>
    PHQ-9: 22→19→17→17→14 (RCI threshold met session 5)
    Q9: 0 across all sessions
  </measurement>
  <treatment_goals>
    1. Re-engage with weekly football (baseline: 0, current: 1x)
    2. Reduce rumination periods to &lt;30min (baseline: 2hr+)
  </treatment_goals>
  <active_flags>
    Plateau watch: two consecutive 17 scores before drop
    Medication: started sertraline 50mg session 2
  </active_flags>
</client_context>
```

### Design principles

**5.1 Trajectory, not history.** The agent does not need five previous
formulations — it needs the current formulation and a lean delta noting what
changed. This mirrors clinical practice: a therapist does not re-read every
previous session note before seeing a client; they hold the current formulation
and update it based on new information.

**5.2 Contract-enforced updates.** The client context file is updated as a
structural requirement of each specialist agent's completion contract, not a
separate maintenance process. The `contract_verification` block includes
`client_context_updated` and `update_delta` fields; if the specialist returns
false, the orchestrator triggers a correction loop. This prevents the "stale
specification" failure mode — documentation falling out of sync with reality,
leading agents into silent clinical errors.

**5.3 Three-tier memory architecture.**

| Memory tier | Content | Loading strategy | Purpose |
| --- | --- | --- | --- |
| Tier 1 (Hot) | Orchestrator + safety rules + client context file | Always loaded | Routing, safety, longitudinal awareness |
| Tier 2 (Warm) | Specialist nodes + previous session handover | Loaded per task via trigger table | Deep clinical reasoning |
| Tier 3 (Cold) | Full measurement history, formulation evolution log, historical handovers | Retrieved on demand | Queried when specific historical detail needed |

---

## Synthesis: how the five principles interconnect

- **Context rot mitigation** (1) creates the architectural requirement for
  specialist agents with lean context windows.
- **Rules versus examples** (2) determines what goes into the orchestrator's
  always-loaded constitution versus specialist nodes as few-shot patterns.
- **Prompt calibration** (3) defines how specialist agents reason through
  clinical material via Extract → Categorise → Contradict → Synthesise.
- **Clinical handover format** (4) ensures deep reasoning is distilled before
  reaching the orchestrator, preventing cross-agent context contamination.
- **Cross-session memory** (5) provides longitudinal clinical awareness without
  loading historical transcripts that would cause context rot.

> **The complete pipeline.** Transcript arrives → orchestrator loads client
> context file (200–300 tokens) → trigger table routes deterministically →
> specialist agents reason through Extract/Categorise/Contradict/Synthesise with
> pre-loaded nodes and Symptom-Cause-Fix tables → each agent returns distilled
> clinical handover XML with contract verification → orchestrator assembles
> unified clinical package → verification gate checks against Canonical Bad
> examples and NEVER constraints → "Awaiting Therapist Review" badge applied.

## Open questions closed

| Original open question | Resolution |
| --- | --- |
| Agent-to-agent communication | Agents do not communicate directly. Unresolved items in the clinical handover XML are routed by the orchestrator. (Principle 4) |
| Multi-session awareness | Client context file loaded per session with current formulation, trajectory deltas, measurement series, and active flags. Updated as structural contract requirement. (Principle 5) |
| Stale documentation | Contract-enforced updates prevent specification drift. Agents cannot complete without confirming memory sync. (Principle 5) |
| Output format between agents and orchestrator | Clinical handover XML with defined sections: formulation summary, risk flags, contract verification, confidence signal, unresolved items. (Principle 4) |
| How to balance rules and examples in nodes | Safety-critical instructions remain as ALWAYS/NEVER rules. Clinical reasoning guidance becomes Symptom-Cause-Fix canonical examples. (Principle 2) |

## Source lineage

- **Anthropic:** "Effective Context Engineering for AI Agents" — context as a
  finite resource.
- **Karpathy:** "Deep Dive into LLMs" — mechanical foundations of probabilistic
  token generation, attention mechanisms, and chain-of-thought necessity.
- **Codified Context paper** (arxiv.org/abs/2602.20478) — three-tier memory
  architecture validated in production.
- **OpenAI Symphony:** isolated agent sessions, completion contracts,
  proof-of-work patterns.
- **Production agentic engineering practice:** rules versus skills separation,
  completion contracts, clean-up cycles.
