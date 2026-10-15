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
- **Human requester:** AidanKDao
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Turn the project brief into a CLAUDE.md so agents understand the scope; add the course AI-citation policy; make it work for other agents (Codex, Gemini).
- **Output used:** `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`
- **Modifications:** Reviewed by AidanKDao (2026-10-15).

### 2026-10-05: Week 1 tests
- **Human requester:** AidanKDao
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Write the five week-1 tests (normal match, duplicate ID, expired donation, no compatible food type, insufficient recipient capacity) using unittest, on a separate branch. Loader and FIFO are written by teammates.
- **Output used:** `tests/__init__.py`, `tests/helpers.py`, `tests/test_week1.py`. The assumed loader/FIFO interface is documented in `tests/helpers.py`.
- **Modifications:** Reviewed by AidanKDao (2026-10-15). The test logic was first checked against a throwaway stub loader/FIFO outside the repo (5/5 passed); the tests now run against the real loader and FIFO and pass.

### 2026-10-05: Handoff document
- **Human requester:** AidanKDao
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Write a handoff so a different model can continue the work.
- **Output used:** `docs/HANDOFF.md` (temporary)
- **Modifications:** Read by the next session (Claude Code, claude-opus-5-5) and then deleted at AidanKDao's request. Not part of the submission.

### 2026-10-05: Project logic folder and near-expiry proposal
- **Human requester:** AidanKDao
- **Tool/model:** Claude Code (claude-opus-5-5)
- **Prompt summary:** Create a project logic folder explaining confusing cases such as "a donation expires in 10 minutes", using real food-rescue procedures to make the decision. Mark decisions as proposals for now.
- **Output used:** `docs/project_logic/README.md`, `docs/project_logic/001-near-expiry-and-pickup-timing.md`. Web research; sources below.
- **Modifications:** Reviewed by AidanKDao (2026-10-15). The proposed rule was checked by hand against all scenarios in `data/scenarios/`. Later superseded by `002` (accepted 2026-10-14); `001` is kept for its research.

### 2026-10-05: Logging rules in AGENTS.md
- **Human requester:** AidanKDao
- **Tool/model:** Claude Code (claude-opus-5-5)
- **Prompt summary:** Update AGENTS.md so other agents know exactly how to log their work.
- **Output used:** `AGENTS.md` (AI-use section: entry template, checklist, "everything counts" rule, source read-status rule; open-decisions section: pointer to `docs/project_logic/` and the do-not-implement-proposals rule).
- **Modifications:** Reviewed by AidanKDao (2026-10-15).

### 2026-10-05: Loader and validation
- **Human requester:** Kaleb Robles
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Implement CSV/JSON loading and validation (Data & Matching Lead role) matching the interface assumed in `tests/helpers.py`.
- **Output used:** `rescueroute/loader.py` (load_donations/recipients/volunteers), `tests/test_loader.py`.
- **Modifications:** Reviewed by Kaleb Robles (2026-10-05). Checked against every dataset in `data/scenarios/` and `data/scale/` (CSV and JSON load identically); `tests/test_loader.py` passes.

### 2026-10-05: Shared feasibility check and capacity tracking
- **Human requester:** Kaleb Robles
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Write the shared donation-recipient-volunteer feasibility check (Data & Matching Lead role), with the unsettled rules as switchable options that default to off.
- **Output used:** `rescueroute/feasibility.py` (Rules, CapacityTracker, check_pair, find_match, assigned_reason, unassigned_reason), `tests/test_feasibility.py`.
- **Modifications:** Reviewed by Kaleb Robles (2026-10-05). Open rules (area match, maximum pickups, volunteer window, travel/shelf-life buffer from proposal 001) are off by default and not treated as settled. `tests/test_feasibility.py` passes.

### 2026-10-05: Enforce maximum pickups and volunteer window by default
- **Human requester:** Kaleb Robles
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Teammates confirmed volunteer maximum pickups and availability window are enforced; update the feasibility defaults to match.
- **Output used:** `rescueroute/feasibility.py` (defaults and docstring), `tests/test_feasibility.py` (tests now assert on-by-default), `AGENTS.md` (open-decisions entry).
- **Modifications:** Reviewed by Kaleb Robles (2026-10-05). Area matching, travel time and shelf-life buffer remain unsettled and off.

### 2026-10-06: Explanatory comments in loader.py
- **Human requester:** Kaleb Robles
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Walk through loader.py line by line for a Python beginner, then add comments to each chunk so the team can follow it.
- **Output used:** `rescueroute/loader.py` (comments and a file-organization note in the docstring only; no logic changes).
- **Modifications:** Reviewed by Kaleb Robles (2026-10-06). `tests/test_loader.py` and `tests/test_feasibility.py` still pass.

### 2026-10-06: Explanatory comments in feasibility.py
- **Human requester:** Kaleb Robles
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Walk through feasibility.py for a Python beginner and add comments so the team can follow it.
- **Output used:** `rescueroute/feasibility.py` (comments, a file-organization note, a docstring on `Rules`, and a summary comment above each function; no logic changes).
- **Modifications:** Reviewed by Kaleb Robles (2026-10-06). `tests/test_loader.py` and `tests/test_feasibility.py` still pass.

### 2026-10-06: Explanatory comments in test_loader.py and test_feasibility.py
- **Human requester:** Kaleb Robles
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Walk through the test files and add a comment above every function so the team can follow what each test checks.
- **Output used:** `tests/test_loader.py`, `tests/test_feasibility.py` (comments and a docstring note on the assert methods only; no change to what the tests check).
- **Modifications:** Reviewed by Kaleb Robles (2026-10-06). All 18 tests in the two files still pass.

### 2026-10-14: Accepted scheduling, feasibility, and metrics rules
- **Human requester:** Dominic Dionne
- **Tool/model:** Claude Code (claude-opus-5-5)
- **Prompt summary:** Create a source of truth for open questions in the repo using answers provided by Dominic Dionne, then search the repo for any questions Dominic Dionne did not answer and bring them up.
- **Output used:** `docs/project_logic/002-scheduling-feasibility-and-metrics-rules.md`, `docs/project_logic/README.md`, `docs/project_logic/001-near-expiry-and-pickup-timing.md`, `AGENTS.md`
- **Modifications:** Every decision was made by and description was verified by Dominic Dionne.

### 2026-10-15: Greedy deferral sentences and the remaining required tests
- **Human requester:** AidanKDao
- **Tool/model:** Claude Code (claude-opus-5-5)
- **Prompt summary:** Check that the greedy rule Dominic described (earliest expiry, then fewest compatible recipients, then larger quantity, then earlier arrival) is implemented, align greedy's deferral explanations with `docs/project_logic/002`, and write the rest of the 10 required tests, on a separate branch.
- **Output used:** `rescueroute/strategies/greedy.py` (`deferral_reason` wording now matches 002; the closest-jumper search skips donations with zero compatible recipients instead of unassigned ones; the sort key was already correct and is unchanged), `tests/test_week2.py` (new: vehicle capacity, competing capacity, empty inputs, starvation, and deferral sentences for each greedy level), `tests/test_week1.py` (expired test now asserts D-1002 is unassigned), `tests/helpers.py` (docstring: greedy returns results in processing order). The README 10-tests checkpoint was not ticked, because the "FIFO and greedy differ" test is Soheil's and is not in yet.
- **Modifications:** Reviewed by AidanKDao (2026-10-16): read the `greedy.py` changes (the `deferral_reason` wording and the closest-jumper skip rule) and confirmed they match 002. No human edits. All 32 tests passed when the agent ran them; `tests/test_week2.py` and the `test_week1.py` change have not been read line by line by a human.

### 2026-10-15: Handoff document for the Claude CLI
- **Human requester:** AidanKDao
- **Tool/model:** Claude Code (claude-opus-5-5)
- **Prompt summary:** Write a handoff of this session so work can continue in the Claude CLI.
- **Output used:** `docs/HANDOFF.md` (temporary, not part of the submission; deleted on 2026-10-15, never committed)
- **Modifications:** Read by the next session's agent (Claude Code, claude-sonnet-5-5), then deleted at AidanKDao's request on 2026-10-15. Never committed and not part of the submission. AidanKDao did not read it; only the agent did.

### 2026-10-15: Commit of the greedy and test work, handoff cleanup
- **Human requester:** AidanKDao
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Read the handoff and `AGENTS.md` then delete the handoff; commit the previous session's work; summarize it in the logs; draft instructions for Soheil's agent.
- **Output used:** Deleted `docs/HANDOFF.md`. Committed the greedy deferral wording fix (`rescueroute/strategies/greedy.py`), the new tests (`tests/test_week2.py`, `tests/test_week1.py`, `tests/helpers.py`) and this log, all written in the entry above. Corrected that entry (32 tests pass, not 33; README was not changed). `README.md` and `fifo.py` were left out of the commit because they differ only in line endings. No new code was written.
- **Modifications:** Reviewed by AidanKDao (2026-10-16): checked the contents of commit `b220c0f` against this entry and they match. The agent re-ran the full suite before committing: 32 tests, OK.

### 2026-10-15: Merge Soheil's branch and add the missing required metrics
- **Human requester:** AidanKDao
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Merge the greedy/test branch and Soheil's `soheil-week2-metrics` branch into `main`, then add the required metrics his `metrics.py` did not have (food at risk, urgent rescue rate, recipient and volunteer utilization).
- **Output used:** Merged both branches into `main` (merge commit `dc8c6e0`; Soheil's code is his own, not AI output). New work on `AidanKDao/feat/required-metrics`: `rescueroute/metrics.py` (`calculate_metrics` now also takes `recipients` and `volunteers` and returns `food_at_risk`, `urgent_donations`, `urgent_assigned`, `urgent_rescue_rate`, `recipient_utilization`, `volunteer_utilization`; urgent = earliest-expiring 25% rounded up, ties by arrival order, per 002), `compare_strategies.py` (passes recipients/volunteers, prints the new rows and an urgent-rate difference), `tests/test_metrics.py` (existing three tests adapted, six new tests), `tests/test_compare_strategies.py` (four new assertions), `README.md` (metric definitions, results table, test counts; the "10 tests" box is now unticked because the "FIFO and greedy differ" test is still missing).
- **Modifications:** Reviewed by AidanKDao (2026-10-16): checked that Soheil's files arrived intact in the merge, ran `compare_strategies.py`, and ran the metric tests. Went through the urgent-donation calculation in `metrics.py` line by line with the agent (without having read the file first) and can explain it; the other three metrics were not walked through. No human edits. 43 tests passed at the time (44 now); `data/scale/small` shows urgent rescue rate 85.71% (FIFO) vs 100% (greedy).

### 2026-10-15: "FIFO and greedy differ" test
- **Human requester:** AidanKDao
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Add the last required test, where FIFO and greedy give different results on the same input, with comments explaining the reasoning.
- **Output used:** `tests/test_week2.py` (new `test_fifo_and_greedy_differ`, using the existing `fifo_vs_greedy_differ` scenario; it checks the assignments, the explanation wording, and the metrics difference), `README.md` (ticked the "10 required tests" box, test count now 44). No scenario data was changed. Also added the urgent-donation rounding rule (round up, ties by arrival order) to `docs/project_logic/002` and the Metrics line in `AGENTS.md`, and changed the requester name from `AidanDao` to `AidanKDao` across the log and file markers.
- **Modifications:** Reviewed by AidanKDao (2026-10-16): read `test_fifo_and_greedy_differ` and its comments, looked at the `fifo_vs_greedy_differ` scenario data, and went through why FIFO assigns 1 donation and greedy assigns 2 with the agent; can explain it. No human edits. The rounding clarification in 002 was confirmed with Dom by AidanKDao. The agent ran the suite (44 tests pass); the requester-name rename and the README tick were not separately reviewed by a human.

### 2026-10-16: Team handoff for tomorrow's work
- **Human requester:** AidanKDao
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Write a handoff that tells the teammates' agents what is left on the project, to be read and then deleted.
- **Output used:** `docs/HANDOFF.md` (temporary, not part of the submission; the last teammate to finish deletes it). A plain-text message for the teammates was also drafted in chat and is not stored in the repo.
- **Modifications:** Reviewed by AidanKDao (2026-10-16): read `docs/HANDOFF.md` and checked the suggested task split against what the team agreed. The split did not match, so the agent removed all suggested owners; the tasks are now unassigned and the team decides. The chat message to teammates needs the same change before it is sent.

### 2026-10-15: Busy-volunteer schedule with gap filling
- **Human requester:** Kaleb Robles
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Implement the settled "Volunteer schedule" rule from docs/project_logic/002 (HANDOFF item 2): a volunteer is busy during booked trips, a new trip moves to the earliest free gap, and unassigned explanations mention a busy volunteer.
- **Output used:** `rescueroute/feasibility.py` (`CapacityTracker.volunteer_trips`, optional `start`/`arrival` on `record`, gap search in `schedule`, `_busy_note` in `unassigned_reason`); `rescueroute/strategies/fifo.py` and `greedy.py` (pass `start` and `arrival` to `tracker.record`, two lines each); `data/scripts/generate_data.py` (scenarios `volunteer_busy`, `volunteer_gap_filling`, `cross_area_trip`); `tests/test_volunteer_schedule.py`; `data/README.md` (scenario table); `README.md` (Week 2 comparison table and summary numbers).
- **Modifications:** Reviewed by Kaleb Robles (2026-10-15). Full suite (52 tests) passes. Small-dataset comparison changed: greedy now rescues 816 units (was 839), FIFO unchanged at 814. The two-line edits in the strategy files touch Dominic's and Aidan's code and need their review.

### 2026-10-15: main.py CLI, report, README sections, and demo script
- **Human requester:** Kaleb Robles
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Build the `main.py` CLI specified in docs/project_logic/002 (HANDOFF item 1), fill the missing README sections (HANDOFF item 3), and write a live-demo script, because the team wants a live demo for submission.
- **Output used:** `main.py`, `rescueroute/report.py` (report text: validation errors first, every donation's explanation in each strategy's processing order, metrics table and differences, optional `--out`), `tests/test_main.py` (10 tests), `README.md` (run instructions, architecture, data model, precise greedy rule, complexity analysis, results on larger datasets, limitations, tools and sources, team contributions, test count and structure), `docs/DEMO_SCRIPT.md` (written, but kept local and not committed). Timings and dataset results in the README come from runs of `python3 main.py` on the generated datasets.
- **Modifications:** Pending human review. Full suite (62 tests) passes. `compare_strategies.py` was left unchanged (it still reads only `donations.csv`; `main.py` accepts CSV or JSON folders). The README text was not reviewed by Dominic or Soheil, who own the greedy rule and metrics.

### 2026-10-15: Remove unused Status.DEFERRED
- **Human requester:** Kaleb Robles
- **Tool/model:** Claude Code (claude-sonnet-5-5)
- **Prompt summary:** Clean up HANDOFF item 6: `Status.DEFERRED` in `models.py` is unused, and rule 002 says deferred is not a final status.
- **Output used:** `rescueroute/models.py` (deleted the `DEFERRED` member of `Status`). A search found no other use in the code, tests, or scripts.
- **Modifications:** Pending human review. Full suite passes after the change.


### 2026-10-15: Retroactive log of Week 1 documentation
- **Human requester:** Soheil Douzandeh
- **Tool/model:** ChatGPT (GPT-6)
- **Prompt summary:** Structure the project README to clearly define the RescueRoute objectives, functional requirements, team responsibilities, execution instructions, and Week 1 deliverables. Organize the documentation according to the project specifications and maintain consistency with the established repository structure.
- **Output used:** `README.md` (team roles, setup instructions, Week 1 checklist).
- **Modifications:** Reviewed and edited the README in VS Code, committed the documentation updates, and submitted a pull request that was merged into main.

### 2026-10-15: Retroactive log of FIFO baseline implementation
- **Human requester:** Soheil Douzandeh
- **Tool/model:** ChatGPT (GPT-6)
- **Prompt summary:** Implement a First-In, First-Out scheduling algorithm that processes food donations according to their arrival order. Integrate the existing data models, shared feasibility checks, and capacity tracking to identify valid recipient-volunteer assignments. Ensure every donation receives an explainable scheduling decision, and include comments documenting the primary algorithmic operations.
- **Output used:** `rescueroute/strategies/fifo.py`.
- **Modifications:** Reviewed the implementation, added explanatory comments, verified the scheduling behavior through automated tests, and committed the FIFO implementation.

### 2026-10-15: Retroactive log of Week 2 performance metrics
- **Human requester:** Soheil Douzandeh
- **Tool/model:** ChatGPT (GPT-6)
- **Prompt summary:** Develop a reusable performance evaluation module for comparing the FIFO and Greedy scheduling algorithms. Calculate total donations, successful assignments, rejected assignments, rescued food quantities, assignment rates, and food rescue percentages. Implement automated unit tests to validate metric accuracy across different donation and assignment scenarios.
- **Output used:** `rescueroute/metrics.py`, `tests/test_metrics.py`.
- **Modifications:** Reviewed the metric calculations, executed the automated tests, and verified the results against the generated dataset. Committed the implementation to `soheil-week2-metrics`. Additional metrics were subsequently implemented by Aidan using Claude Code and documented separately.

### 2026-10-15: Retroactive log of FIFO vs Greedy comparison
- **Human requester:** Soheil Douzandeh
- **Tool/model:** ChatGPT (GPT-6)
- **Prompt summary:** Design and implement a command-line comparison module that evaluates FIFO and Greedy under identical input conditions. Load and validate donation, recipient, and volunteer datasets, execute both scheduling strategies independently, and present performance metrics in a consistent side-by-side report. Include integration tests covering successful execution, metric output, and missing-input error handling.
- **Output used:** `compare_strategies.py`, `tests/test_compare_strategies.py`.
- **Modifications:** Executed both scheduling strategies using the same dataset, reviewed the output, and validated the comparison results. Added integration tests and confirmed that all 29 automated tests passed at the initial Week 2 checkpoint. Submitted the changes through PR #4.

### 2026-10-15: Retroactive log of Week 2 README documentation
- **Human requester:** Soheil Douzandeh
- **Tool/model:** ChatGPT (GPT-6)
- **Prompt summary:** Refactor the README to provide comprehensive documentation of the RescueRoute system, including project architecture, FIFO and Greedy scheduling methods, dataset generation, execution commands, testing procedures, and performance evaluation. Integrate verified comparison results, organize the project structure, and update milestone completion status to reflect Week 2 development progress.
- **Output used:** `README.md`.
- **Modifications:** Reviewed and updated the documentation, verified the recorded performance metrics, and committed the revised README to the Week 2 branch. Submitted the changes through PR #4, which was subsequently merged into main.

### 2026-10-15: Automated test troubleshooting and dataset validation
- **Human requester:** Soheil Douzandeh
- **Tool/model:** ChatGPT (GPT-6)
- **Prompt summary:** Investigate automated test failures occurring after integrating the latest repository changes. Analyze the missing donation identifier errors in volunteer scheduling tests, evaluate the relationship between generated scenario datasets and test dependencies, and determine the appropriate corrective action without modifying existing scheduling logic. Reexecute the complete test suite to verify system stability.
- **Output used:** Diagnostic guidance, dataset regeneration commands, and automated test execution instructions. No source code modifications.
- **Modifications:** Regenerated the simulation datasets using the existing data generator and executed the complete unittest suite. Verified that all 62 automated tests passed successfully.

## Outside sources

Read status: **read** = the original page was opened and read; **summary only** = only a search-result summary was seen, the original was not retrieved.

| Source | Used for | Read status |
|---|---|---|
| [Reading, MA: Time as a Public Health Control (TPHC)](https://www.readingma.gov/948/Time-as-a-Public-Health-Control-TPHC) | Food Code 3-501.19 four-hour limit (`docs/project_logic/001`) | Read |
| [Partner Food Rescue Training Quiz (Smartsheet)](https://app.smartsheet.com/b/form/a240b7197db4417abf03108bc8948170) | 15-minute non-refrigerated transport limit (`001`) | Summary only |
| [Grocery Rescue Program Guide (First Food Bank)](https://www.firstfoodbank.org/wp-content/uploads/2023/10/Grocery-Rescue-Program-Guide.pdf) | 2 hours above 41°F acceptance limit (`001`) | Summary only (link redirects to a 404) |
| [Food Rescue Driver listing (idealist.org)](https://www.idealist.org/en/volunteer-opportunity/b93ffd8317f24286b966c2ad5ce958ce-food-rescue-driver-dc-metro-area-the-jj-center-inc-washington) | "Deliver immediately" driver practice (`001`) | Summary only |

