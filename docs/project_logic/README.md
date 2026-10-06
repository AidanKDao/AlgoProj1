# Project Logic

AI-assisted: Claude Code (claude-opus-5-5), requested by AidanDao, see docs/TOOLS_AND_SOURCES.md

This folder records how RescueRoute handles questions the project brief leaves open, such as *"a donation expires in 10 minutes: can it still be rescued?"* Each file covers one question: what the confusion is, what real food-rescue practice suggests, the rule we propose, the alternatives, and how each one changes the scenario datasets in `data/scenarios/`.

**Disclaimer:** RescueRoute is an educational simulation. The rules here are simulation parameters *informed by* public food-rescue and food-safety guidance. They are not food-safety rules, and nothing here should be read as certified or operationally approved.

## Status legend

| Status | Meaning |
|---|---|
| **Proposed** | Draft for team discussion. Code must **not** treat it as settled behavior yet. |
| **Accepted** | Agreed by the team. Code and tests should follow it, and `AGENTS.md` should list it as a settled rule. |
| **Rejected** | Kept for the record, with the reason. |

## Index

| # | Question | Status |
|---|---|---|
| [001](001-near-expiry-and-pickup-timing.md) | When is a donation too close to expiry to rescue, and how is pickup/delivery time computed? | Proposed |

### Not yet written (other open decisions from `AGENTS.md`)
- Must the donation, volunteer, and recipient areas match?
- How is the "urgent" set defined for the urgent rescue rate?
- What is the exact greedy priority rule and its tie-breakers?
- What format should the FIFO-vs-greedy comparison report use?

## Adding a file

Name it `NNN-short-topic.md` and include: the question, sources (with whether each one was actually read), the proposed rule, alternatives, the effect on each relevant scenario, and its status. Add a row to the index, and log the work in `docs/TOOLS_AND_SOURCES.md`.
