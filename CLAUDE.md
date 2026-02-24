# CLAUDE.md — Admin Assassin

## What This Project Is

**Admin Assassin** is an AI clinical scribe for CBT therapists.

It takes a therapy session transcript and produces four things automatically:
- A SOAP note
- A GP letter (NHS format)
- A CBT formulation (hot thoughts, maintenance cycle, safety behaviours)
- A risk summary (flags suicidal ideation and self-harm language)

The app is built with **Streamlit** (Python) and uses the **Anthropic Claude API** (`claude-sonnet-4-6`). The main app file is `app.py`.

---

## Who Is Building This

The owner is a trainee CBT therapist. **No coding background.** All explanations must be in plain English — no jargon, no assumed knowledge.

---

## How to Communicate

The owner has inattentive ADHD (2e). Follow these rules in every response:

- **Lead with what changed and why** — not how it works technically
- **Short paragraphs only** — no walls of text
- **One step at a time** — always confirm readiness before moving to the next step
- **Use clear headings** to break up information
- **Plain language** throughout

---

## The Skill Graph — Protected Content

The folder `skill_graphs/depression/` contains the clinical knowledge layer of the app.

**Never modify any file in `skill_graphs/` unless explicitly asked.**

These files are hand-authored clinical content. They are not code. Treat them as source-of-truth documents that must not be touched during routine development work.

Current skill graph files:
- `PHQ9_scoring.md`
- `automatic_thoughts_depression.md`
- `behavioural_activation.md`
- `cognitive_restructuring.md`
- `depression_maintenance_cycle.md`
- `intermediate_beliefs.md`
- `pleasure_mastery_ratings.md`
- `thought_records.md`

---

## Project Structure

```
admin-assassin/
├── app.py                        # The entire application
├── skill_graphs/
│   └── depression/               # Protected clinical content — do not modify
│       └── *.md
├── README.md
├── LICENSE
└── CLAUDE.md                     # This file
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Frontend | Streamlit (Python) |
| AI model | Claude Sonnet (`claude-sonnet-4-6`) via Anthropic SDK |
| Clinical knowledge | Markdown skill graph nodes |
| Deployment | GitHub Codespaces |

---

## After Every Task

Always commit and push changes when a task is complete.

- Use the branch: `claude/explore-repo-files-mxTq7`
- Write a clear, plain-English commit message describing what changed
- Push with: `git push -u origin claude/explore-repo-files-mxTq7`

---

## Known Issues / Notes

- Line 709 in `app.py` has an incorrect error message: it says "OpenAI API key" but the app uses Anthropic. Worth fixing when relevant.
- Audio upload (V2 feature) is stubbed out in the UI but not yet implemented.
- Local LLM support (Ollama/Llama 3) is planned for V3.
