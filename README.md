# 🧠 Admin Assassin
### A Privacy-First Clinical Scribe for CBT Therapists

---

## The Problem

A CBT therapist seeing 6–8 clients a day spends up to 2 hours every evening writing session notes, drafting GP letters, and scoring clinical metrics like PHQ-9 and GAD-7.

That's not therapy. That's administration. And it's burning out an already stretched workforce.

In the UK's IAPT / NHS Talking Therapies framework, therapist burnout directly translates to longer patient waitlists, reduced treatment fidelity, and worse clinical outcomes.

There has to be a better way.

---

## The Solution

Admin Assassin is a secure, local-first clinical scribe that takes a therapy session transcript and outputs everything the therapist needs in under 30 seconds:

- ✅ **SOAP Note** — Structured clinical documentation (Subjective, Objective, Assessment, Plan)
- 🚨 **Risk Triage** — Automatic flagging of high-risk language (suicidality, self-harm) in a clear visual alert
- 💌 **GP Summary Letter** — NHS-style correspondence draft, ready for review and sign-off
- 🧩 **CBT Formulation Extraction** — Identifies Hot Thoughts, Safety Behaviours, and Maintenance Cycles from the session

The therapist always reviews and approves everything. The AI drafts. The clinician decides.

---

## Why This Is Different

Most AI note-taking tools are built by engineers who have never sat in a therapy room.

This is being built by a trainee CBT therapist with clinical training in high-intensity psychological interventions — someone who understands the difference between a maintenance cycle and a coping strategy, and why that distinction matters in a SOAP note.

The prompts aren't generic. They are clinically informed.

---

## The Clinical Skill Graph

This is what separates Admin Assassin from every other AI documentation tool on the market.

Rather than relying on a single generic prompt, Admin Assassin is built on a **clinical skill graph** — a network of hand-authored knowledge nodes, each covering a specific CBT concept in clinical depth. When a transcript is processed, the agent navigates the relevant nodes and applies that knowledge to produce documentation that reads like it was written by a senior clinician.

These nodes weren't written by an engineer. They were written by someone who has trained in CBT and understands the clinical precision required.

### Depression Skill Graph — Complete ✅

| Node | Clinical Role | What It Enables |
|------|--------------|-----------------|
| `depression_maintenance_cycle` | The Engine | Identifies specific maintenance mechanisms — Mood-First Fallacy, False Binary, Predictive Apathy — not just "low mood" |
| `behavioural_activation` | The Intervention | Documents BA tasks with prediction vs actual ratings, prediction error calculation, and correct clinical interpretation |
| `automatic_thoughts_depression` | The Alarm | Categorises cognitive distortions by specific type — Fortune Telling, Disqualifying the Positive, Identity Anchoring — with transcript-level evidence |
| `PHQ9_scoring` | The Measurement | Interprets PHQ-9 trajectory not just raw score — calculates assessment delta, session delta, RCI status, and flags plateaus as clinical signals |
| `pleasure_mastery_ratings` | The Data | Tracks dual metrics separately, identifies Mastery First recovery pattern, calculates prediction error and emotional delta |
| `thought_records` | The Tool | Identifies five vs seven column format, calculates emotional delta, flags Head-Heart Discrepancy when cognitive work doesn't produce emotional shift |
| `cognitive_restructuring` | The Mechanism | Distinguishes Socratic questioning from leading questions, documents whether genuine cognitive shift occurred, flags when validation was absent |
| `intermediate_beliefs` | The Pattern | Detects cross-session belief patterns, articulates If-Then structure, flags when belief-level work is needed vs automatic thought work |

### Anxiety / GAD Skill Graph — In Development 🔄

| Node | Status |
|------|--------|
| `GAD_cognitive_model` | Coming soon |
| `worry_model` | Coming soon |
| `intolerance_of_uncertainty` | Coming soon |
| `safety_behaviours_anxiety` | Coming soon |
| `exposure_hierarchy` | Coming soon |
| `GAD7_scoring` | Coming soon |

### What the Skill Graph Produces

Admin Assassin with the full depression skill graph has been stress-tested against complex clinical transcripts. Output includes:

- PHQ-9 trajectory analysis with Reliable Change Index calculation — not just a raw score
- Specific cognitive distortion taxonomy applied to quoted client language
- Intermediate belief identification from cross-session patterns
- Emotional delta calculation from thought record work
- Risk content categorised and clinically formulated — not just flagged

**Stress test grade: A** — Output assessed against clinical supervision standards.

---

## Privacy Architecture

Patient data is never stored. Patient data is never trained on.

- **Local-First Design:** Built to run on local inference (Llama 3 via Ollama) so data never leaves the therapy room
- **Human-in-the-Loop:** AI drafts, therapist approves. Nothing is sent without clinical sign-off
- **No Patient Names in Logs:** The system is designed to process anonymised transcripts
- **GDPR-Conscious from Day One:** Not retrofitted for compliance — built with it as a constraint

---

## Current Status: V1.0 Beta

| Feature | Status |
|---------|--------|
| Transcript input (paste) | ✅ Live |
| Hot Thought extraction | ✅ Live |
| SOAP Note generation | ✅ Live |
| Suicidal ideation risk flag | ✅ Live |
| GP Letter draft (NHS format) | ✅ Live |
| Depression skill graph (8 nodes) | ✅ Live |
| CBT Formulation with distortion taxonomy | ✅ Live |
| PHQ-9 trajectory analysis | ✅ Live |
| Intermediate belief detection | ✅ Live |
| Audio upload + transcription | 🔄 In Progress |
| GAD / Anxiety skill graph | 🔄 In Progress |
| Local LLM support (Ollama) | 📋 Planned |

---

## Roadmap

### v1 — Software MVP (Now)
A browser-based clinical scribe with a full depression skill graph. Paste a transcript, receive supervision-quality clinical documentation.

### v2 — Ambient Room Intelligence (Next)
A dedicated hardware device sits on the therapy desk. No laptop required. The therapist says "end session" — the notes are already written. Exploring integration with OpenHome Dev Kit for local, privacy-hardened voice capture.

### v3 — Longitudinal Clinical Intelligence (Future)
Track patient progress across all 8 sessions. Flag when intervention doesn't match formulation. Generate supervision-ready summaries. Support trainee therapists in learning CBT fidelity.

---

## The Stack

- **Frontend:** Streamlit (Python)
- **LLM:** Claude Sonnet / OpenAI GPT-4o (migrating to local Llama 3)
- **Clinical Knowledge Layer:** Hand-authored CBT skill graph (markdown nodes)
- **IDE:** Cursor (AI-assisted development)
- **Deployment:** GitHub Codespaces → Local-first v2

---

## Who Is Building This

A 30-year-old trainee CBT therapist currently completing a High Intensity postgraduate qualification in psychological interventions.

Not a traditional developer. Building this with AI-assisted coding tools and clinical domain knowledge that no generic AI company has.

The clinical skill graph — the knowledge layer that makes Admin Assassin clinically precise rather than generically useful — can only be built by someone who has trained as a CBT therapist. That's the moat.

**The mission:** Reduce administrative burnout for CBT therapists, increase clinical fidelity, and give therapists back the time they should be spending with patients.

---

## Building in Public

This entire project is being documented openly — the wins, the dead ends, and everything in between.

- 🐦 Twitter/X: [Adding Soon]
- 💼 LinkedIn: [Adding Soon]
- 📱 TikTok/Instagram: [Adding Soon]

- *"The future of psychology isn't just more therapists. It's augmented therapists."*

---

## Disclaimer

Admin Assassin is a clinical productivity tool, not a diagnostic or treatment system. All AI-generated content must be reviewed and approved by a qualified clinician before use. This tool does not replace clinical judgement.



