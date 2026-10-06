# Tools & Sources

Log of AI tool use and outside sources, as required by course policy. One entry per contribution. See the AI-use section of `AGENTS.md` for the rules.

## AI contributions

### 2026-10-05: Agent instruction files
- **Human requester:** AidanDao
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Turn the project brief into a CLAUDE.md so agents understand the scope; add the course AI-citation policy; make it work for other agents (Codex, Gemini).
- **Output used:** `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`
- **Modifications:** Pending human review.

### 2026-10-05: Week 1 tests
- **Human requester:** AidanDao
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Write the five week-1 tests (normal match, duplicate ID, expired donation, no compatible food type, insufficient recipient capacity) using unittest, on a separate branch. Loader and FIFO are written by teammates.
- **Output used:** `tests/__init__.py`, `tests/helpers.py`, `tests/test_week1.py`. The assumed loader/FIFO interface is documented in `tests/helpers.py`.
- **Modifications:** Pending human review. The test logic was checked against a throwaway stub loader/FIFO outside the repo (5/5 passed). Against the real code they fail until the teammates' loader and FIFO exist and match the assumed interface.

### 2026-10-05: Handoff document
- **Human requester:** AidanDao
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Write a handoff so a different model can continue the work.
- **Output used:** `docs/HANDOFF.md` (temporary)
- **Modifications:** Read by the next session (Claude Code, claude-opus-5-5) and then deleted at AidanDao's request. Not part of the submission.

### 2026-10-05: Project logic folder and near-expiry proposal
- **Human requester:** AidanDao
- **Tool/model:** Claude Code (claude-opus-5-5)
- **Prompt summary:** Create a project logic folder explaining confusing cases such as "a donation expires in 10 minutes", using real food-rescue procedures to make the decision. Mark decisions as proposals for now.
- **Output used:** `docs/project_logic/README.md`, `docs/project_logic/001-near-expiry-and-pickup-timing.md`. Web research; sources below.
- **Modifications:** Pending human review. Status is *Proposed*; the team has not accepted it. The proposed rule was checked by hand against all scenarios in `data/scenarios/`.

### 2026-10-05: Logging rules in AGENTS.md
- **Human requester:** AidanDao
- **Tool/model:** Claude Code (claude-opus-5-5)
- **Prompt summary:** Update AGENTS.md so other agents know exactly how to log their work.
- **Output used:** `AGENTS.md` (AI-use section: entry template, checklist, "everything counts" rule, source read-status rule; open-decisions section: pointer to `docs/project_logic/` and the do-not-implement-proposals rule).
- **Modifications:** Pending human review.

## Pre-existing AI-generated code
- `data/scripts/generate_data.py` is marked in its docstring as AI generated and attributed to "Dom". The tool/model and date are not recorded here yet; Dom should add an entry using the template in `AGENTS.md`.

## Outside sources

Read status: **read** = the original page was opened and read; **summary only** = only a search-result summary was seen, the original was not retrieved.

| Source | Used for | Read status |
|---|---|---|
| [Reading, MA: Time as a Public Health Control (TPHC)](https://www.readingma.gov/948/Time-as-a-Public-Health-Control-TPHC) | Food Code 3-501.19 four-hour limit (`docs/project_logic/001`) | Read |
| [Partner Food Rescue Training Quiz (Smartsheet)](https://app.smartsheet.com/b/form/a240b7197db4417abf03108bc8948170) | 15-minute non-refrigerated transport limit (`001`) | Summary only |
| [Grocery Rescue Program Guide (First Food Bank)](https://www.firstfoodbank.org/wp-content/uploads/2023/10/Grocery-Rescue-Program-Guide.pdf) | 2 hours above 41°F acceptance limit (`001`) | Summary only (link redirects to a 404) |
| [Food Rescue Driver listing (idealist.org)](https://www.idealist.org/en/volunteer-opportunity/b93ffd8317f24286b966c2ad5ce958ce-food-rescue-driver-dc-metro-area-the-jj-center-inc-washington) | "Deliver immediately" driver practice (`001`) | Summary only |
