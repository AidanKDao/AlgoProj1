# Tools & Sources

Log of AI tool use and outside sources, as required by course policy. One entry per contribution. See the AI-use section of `AGENTS.md` for the rules.

## AI contributions

### 2026-09-26: Sample data generator and dataset catalogue
- **Human requester:** Dominic Dionne
- **Tool/model:** Claude Code (claude-opus-5-5)
- **Prompt summary:** Write a script that produces food-rescue input data in both CSV and JSON, covering seeded random datasets at increasing scale.
- **Output used:** `data/scripts/generate_data.py` , `data/README.md`
- **Modifications:** Reviewed and run by Dominic Dionne; the generated files were checked.

### 2026-10-05: Agent instruction files
- **Human requester:** AidanDao
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Turn the project brief into a CLAUDE.md so agents understand the scope; add the course AI-citation policy; make it work for other agents (Codex, Gemini).
- **Output used:** `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`
- **Modifications:** Reviewed by AidanDao (2026-10-15).

### 2026-10-05: Week 1 tests
- **Human requester:** AidanDao
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Write the five week-1 tests (normal match, duplicate ID, expired donation, no compatible food type, insufficient recipient capacity) using unittest, on a separate branch. Loader and FIFO are written by teammates.
- **Output used:** `tests/__init__.py`, `tests/helpers.py`, `tests/test_week1.py`. The assumed loader/FIFO interface is documented in `tests/helpers.py`.
- **Modifications:** Reviewed by AidanDao (2026-10-15). The test logic was first checked against a throwaway stub loader/FIFO outside the repo (5/5 passed); the tests now run against the real loader and FIFO and pass.

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
- **Modifications:** Reviewed by AidanDao (2026-10-15). The proposed rule was checked by hand against all scenarios in `data/scenarios/`. Later superseded by `002` (accepted 2026-10-14); `001` is kept for its research.

### 2026-10-05: Logging rules in AGENTS.md
- **Human requester:** AidanDao
- **Tool/model:** Claude Code (claude-opus-5-5)
- **Prompt summary:** Update AGENTS.md so other agents know exactly how to log their work.
- **Output used:** `AGENTS.md` (AI-use section: entry template, checklist, "everything counts" rule, source read-status rule; open-decisions section: pointer to `docs/project_logic/` and the do-not-implement-proposals rule).
- **Modifications:** Reviewed by AidanDao (2026-10-15).

### 2026-10-05: Loader and validation
- **Human requester:** Kaleb Robles
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Implement CSV/JSON loading and validation (Data & Matching Lead role) matching the interface assumed in `tests/helpers.py`.
- **Output used:** `rescueroute/loader.py` (load_donations/recipients/volunteers), `tests/test_loader.py`.
- **Modifications:** Pending human review. Checked against every dataset in `data/scenarios/` and `data/scale/` (CSV and JSON load identically); `tests/test_loader.py` passes.

### 2026-10-05: Shared feasibility check and capacity tracking
- **Human requester:** Kaleb Robles
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Write the shared donation-recipient-volunteer feasibility check (Data & Matching Lead role), with the unsettled rules as switchable options that default to off.
- **Output used:** `rescueroute/feasibility.py` (Rules, CapacityTracker, check_pair, find_match, assigned_reason, unassigned_reason), `tests/test_feasibility.py`.
- **Modifications:** Pending human review. Open rules (area match, maximum pickups, volunteer window, travel/shelf-life buffer from proposal 001) are off by default and not treated as settled. `tests/test_feasibility.py` passes.

### 2026-10-05: Enforce maximum pickups and volunteer window by default
- **Human requester:** Kaleb Robles
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Teammates confirmed volunteer maximum pickups and availability window are enforced; update the feasibility defaults to match.
- **Output used:** `rescueroute/feasibility.py` (defaults and docstring), `tests/test_feasibility.py` (tests now assert on-by-default), `AGENTS.md` (open-decisions entry).
- **Modifications:** Pending human review. Area matching, travel time and shelf-life buffer remain unsettled and off.

### 2026-10-06: Explanatory comments in loader.py
- **Human requester:** Kaleb Robles
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Walk through loader.py line by line for a Python beginner, then add comments to each chunk so the team can follow it.
- **Output used:** `rescueroute/loader.py` (comments and a file-organization note in the docstring only; no logic changes).
- **Modifications:** Pending human review. `tests/test_loader.py` and `tests/test_feasibility.py` still pass.

### 2026-10-06: Explanatory comments in feasibility.py
- **Human requester:** Kaleb Robles
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Walk through feasibility.py for a Python beginner and add comments so the team can follow it.
- **Output used:** `rescueroute/feasibility.py` (comments, a file-organization note, a docstring on `Rules`, and a summary comment above each function; no logic changes).
- **Modifications:** Pending human review. `tests/test_loader.py` and `tests/test_feasibility.py` still pass.

### 2026-10-06: Explanatory comments in test_loader.py and test_feasibility.py
- **Human requester:** Kaleb Robles
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Walk through the test files and add a comment above every function so the team can follow what each test checks.
- **Output used:** `tests/test_loader.py`, `tests/test_feasibility.py` (comments and a docstring note on the assert methods only; no change to what the tests check).
- **Modifications:** Pending human review. All 18 tests in the two files still pass.

### 2026-10-14: Accepted scheduling, feasibility, and metrics rules
- **Human requester:** Dominic Dionne
- **Tool/model:** Claude Code (claude-opus-5-5)
- **Prompt summary:** Create a source of truth for open questions in the repo using answers provided by Dominic Dionne, then search the repo for any questions Dominic Dionne did not answer and bring them up.
- **Output used:** `docs/project_logic/002-scheduling-feasibility-and-metrics-rules.md`, `docs/project_logic/README.md`, `docs/project_logic/001-near-expiry-and-pickup-timing.md`, `AGENTS.md`
- **Modifications:** Every decision was made by and description was verified by Dominic Dionne.

### 2026-10-15: Greedy deferral sentences and the remaining required tests
- **Human requester:** AidanDao
- **Tool/model:** Claude Code (claude-opus-5-5)
- **Prompt summary:** Check that the greedy rule Dominic described (earliest expiry, then fewest compatible recipients, then larger quantity, then earlier arrival) is implemented, align greedy's deferral explanations with `docs/project_logic/002`, and write the rest of the 10 required tests, on a separate branch.
- **Output used:** `rescueroute/strategies/greedy.py` (`deferral_reason` wording now matches 002; the closest-jumper search skips donations with zero compatible recipients instead of unassigned ones; the sort key was already correct and is unchanged), `tests/test_week2.py` (new: vehicle capacity, competing capacity, empty inputs, starvation, and deferral sentences for each greedy level), `tests/test_week1.py` (expired test now asserts D-1002 is unassigned), `tests/helpers.py` (docstring: greedy returns results in processing order). The README 10-tests checkpoint was not ticked, because the "FIFO and greedy differ" test is Soheil's and is not in yet.
- **Modifications:** Pending human review. All 32 tests pass.

### 2026-10-15: Handoff document for the Claude CLI
- **Human requester:** AidanDao
- **Tool/model:** Claude Code (claude-opus-5-5)
- **Prompt summary:** Write a handoff of this session so work can continue in the Claude CLI.
- **Output used:** `docs/HANDOFF.md` (temporary, not part of the submission; deleted on 2026-10-15, never committed)
- **Modifications:** Pending human review.

### 2026-10-15: Commit of the greedy and test work, handoff cleanup
- **Human requester:** AidanDao
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Read the handoff and `AGENTS.md` then delete the handoff; commit the previous session's work; summarize it in the logs; draft instructions for Soheil's agent.
- **Output used:** Deleted `docs/HANDOFF.md`. Committed the greedy deferral wording fix (`rescueroute/strategies/greedy.py`), the new tests (`tests/test_week2.py`, `tests/test_week1.py`, `tests/helpers.py`) and this log, all written in the entry above. Corrected that entry (32 tests pass, not 33; README was not changed). `README.md` and `fifo.py` were left out of the commit because they differ only in line endings. No new code was written.
- **Modifications:** Pending human review. Re-ran the full suite before committing: 32 tests, OK.

### 2026-10-15: Merge Soheil's branch and add the missing required metrics
- **Human requester:** AidanDao
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Merge the greedy/test branch and Soheil's `soheil-week2-metrics` branch into `main`, then add the required metrics his `metrics.py` did not have (food at risk, urgent rescue rate, recipient and volunteer utilization).
- **Output used:** Merged both branches into `main` (merge commit `dc8c6e0`; Soheil's code is his own, not AI output). New work on `AidanKDao/feat/required-metrics`: `rescueroute/metrics.py` (`calculate_metrics` now also takes `recipients` and `volunteers` and returns `food_at_risk`, `urgent_donations`, `urgent_assigned`, `urgent_rescue_rate`, `recipient_utilization`, `volunteer_utilization`; urgent = earliest-expiring 25% rounded up, ties by arrival order, per 002), `compare_strategies.py` (passes recipients/volunteers, prints the new rows and an urgent-rate difference), `tests/test_metrics.py` (existing three tests adapted, six new tests), `tests/test_compare_strategies.py` (four new assertions), `README.md` (metric definitions, results table, test counts; the "10 tests" box is now unticked because the "FIFO and greedy differ" test is still missing).
- **Modifications:** Pending human review. All 43 tests pass; comparison on `data/scale/small` shows urgent rescue rate 85.71% (FIFO) vs 100% (greedy).

## Outside sources

Read status: **read** = the original page was opened and read; **summary only** = only a search-result summary was seen, the original was not retrieved.

| Source | Used for | Read status |
|---|---|---|
| [Reading, MA: Time as a Public Health Control (TPHC)](https://www.readingma.gov/948/Time-as-a-Public-Health-Control-TPHC) | Food Code 3-501.19 four-hour limit (`docs/project_logic/001`) | Read |
| [Partner Food Rescue Training Quiz (Smartsheet)](https://app.smartsheet.com/b/form/a240b7197db4417abf03108bc8948170) | 15-minute non-refrigerated transport limit (`001`) | Summary only |
| [Grocery Rescue Program Guide (First Food Bank)](https://www.firstfoodbank.org/wp-content/uploads/2023/10/Grocery-Rescue-Program-Guide.pdf) | 2 hours above 41°F acceptance limit (`001`) | Summary only (link redirects to a 404) |
| [Food Rescue Driver listing (idealist.org)](https://www.idealist.org/en/volunteer-opportunity/b93ffd8317f24286b966c2ad5ce958ce-food-rescue-driver-dc-metro-area-the-jj-center-inc-washington) | "Deliver immediately" driver practice (`001`) | Summary only |
