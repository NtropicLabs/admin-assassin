# 🧠 Admin Assassin
### A Privacy-First Clinical Scribe for CBT Therapists

---

## The Problem

A CBT therapist seeing 6–8 clients a day spends up to **2 hours every evening** writing session notes, drafting GP letters, and scoring clinical metrics like PHQ-9 and GAD-7.

That's not therapy. That's administration. And it's burning out an already stretched workforce.

In the UK's IAPT / NHS Talking Therapies framework, therapist burnout directly translates to longer patient waitlists, reduced treatment fidelity, and worse clinical outcomes.

**There has to be a better way.**

---

## The Solution

Admin Assassin is a secure, local-first clinical scribe that takes a therapy session transcript and outputs everything the therapist needs in under 30 seconds:

- ✅ **SOAP Note** — Structured clinical documentation (Subjective, Objective, Assessment, Plan)
- 🚨 **Risk Triage** — Automatic flagging of high-risk language (suicidality, self-harm) in a clear visual alert
- 💌 **GP Summary Letter** — NHS-style correspondence draft, ready for review and sign-off
- 🧩 **CBT Formulation Extraction** — Identifies Hot Thoughts, Safety Behaviours, and Maintenance Cycles from the session

The therapist **always reviews and approves** everything. The AI drafts. The clinician decides.

---

## Why This Is Different

Most AI note-taking tools are built by engineers who have never sat in a therapy room.

This is being built by a **trainee CBT therapist** with clinical training in high-intensity psychological interventions — someone who understands the difference between a maintenance cycle and a coping strategy, and why that distinction matters in a SOAP note.

The prompts aren't generic. They are clinically informed.

---

## Privacy Architecture

> **Patient data is never stored. Patient data is never trained on.**

- **Local-First Design**: Built to run on local inference (Llama 3 via Ollama) so data never leaves the therapy room
- **Human-in-the-Loop**: AI drafts, therapist approves. Nothing is sent without clinical sign-off
- **No Patient Names in Logs**: The system is designed to process anonymised transcripts
- **GDPR-Conscious from Day One**: Not retrofitted for compliance — built with it as a constraint

---

## Current Status: MVP (v1.0)

Built on Replit as a **proof of concept**. Current capabilities:

| Feature | Status |
|---|---|
| Transcript input (paste) | ✅ Live |
| Hot Thought extraction | ✅ Live |
| SOAP Note generation | ✅ Live |
| Suicidal ideation risk flag | ✅ Live |
| GP Letter draft | ✅ Live |
| Audio upload + transcription | 🔄 In Progress |
| Local LLM support (Ollama) | 📋 Planned |

---

## Roadmap

### v1 — Software MVP *(Now)*
A browser-based tool. Paste a transcript, receive clinical documentation.

### v2 — Ambient Room Intelligence *(Next)*
A dedicated hardware device sits on the therapy desk. No laptop required.
The therapist says *"end session"* — the notes are already written.
*(Exploring integration with [OpenHome Dev Kit](https://dev.openhome.com/) for local, privacy-hardened voice capture)*

### v3 — Longitudinal Clinical Intelligence *(Future)*
Track patient progress across all 8 sessions. Flag when intervention doesn't match formulation. Generate supervision-ready summaries. Support trainee therapists in learning CBT fidelity.

---

## The Stack

- **Frontend**: Streamlit (Python)
- **LLM**: OpenAI GPT-4o / Whisper (migrating to local Llama 3)
- **IDE**: Cursor (Vibe Coding — natural language to working code)
- **Deployment**: Replit MVP → Local-first v2

---

## Who Is Building This

A 30-year-old trainee CBT therapist currently completing a High Intensity postgraduate qualification in psychological interventions.

Not a traditional developer. Building this with AI-assisted coding tools and clinical domain knowledge that no generic AI company has.

**The mission**: Reduce administrative burnout by 40%, increase CBT fidelity, and give therapists back the time they should be spending with patients.

---

## Building in Public

This entire project is being documented openly — the wins, the dead ends, and everything in between.

Follow the journey:
- 🐦 Twitter/X: `[Adding Soon]`
- 💼 LinkedIn: `[Adding Soon]`
- 📱 TikTok/Instagram: `[Adding Soon]`

---

## Disclaimer

Admin Assassin is a **clinical productivity tool**, not a diagnostic or treatment system. All AI-generated content must be reviewed and approved by a qualified clinician before use. This tool does not replace clinical judgement.

---

*"The future of psychology isn't just more therapists. It's augmented therapists."*
