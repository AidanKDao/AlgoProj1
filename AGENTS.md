# AGENTS.md — RescueRoute

Instructions for every AI coding agent and teammate working in this repo (Claude Code, Codex, Copilot, Cursor, Gemini, etc.). `CLAUDE.md` and `GEMINI.md` just import this file.

CPSC 335 (Algorithms and Data Structures) group project, 3 students, 3 weeks. Source brief: `docs/CPSC335_RescueRoute_Group_Project_Brief-1.pdf`.

## What this project is

An **explainable** Python CLI that matches time-sensitive surplus-food **donations** to compatible **recipients** (shelters, pantries) and **volunteer drivers**, then compares two scheduling strategies on the same input:

- **A. FIFO baseline** — process donations in arrival order; assign the first feasible recipient + volunteer; record unmatched.
- **B. Greedy urgency-first** — process donations by an explicit priority rule. Earliest expiry must be considered; quantity, recipient closing time, area, and arrival order may be tie-breakers.

The guiding question: *how can we prioritize time-sensitive donations and assign them to compatible recipients and volunteers in a way that is efficient, transparent, and easy to explain?* The goal is clear, testable decisions, not just a schedule.

This is an educational prototype on **simulated data**. Never claim food-safety, medical, or operational readiness, in code, docs, or output.

## Requirements (the grading checklist)

1. Load donations, recipients, volunteers from CSV or JSON.
2. Validate IDs (incl. duplicates), quantities, food types, capacities, availability, and time values.
3. Identify feasible donation–recipient–volunteer matches.
4. Implement the FIFO baseline and one greedy strategy.
5. **Every** donation gets a human-readable explanation: assigned, unassigned, or deferred. Never output only IDs or a table.
6. Compute metrics and compare FIFO vs greedy.
7. Automated tests (unittest or pytest) that verify behavior, not just that the program runs.

### Explanation examples (match this style)
- Assigned: "Donation D-1001 was assigned to Community Shelter with volunteer V-301 because it expires in 90 minutes, the shelter accepts prepared meals, capacity is available, and the volunteer can carry the quantity."
- Unassigned: "Donation D-1008 could not be assigned because no compatible recipient had remaining capacity before the donation expired."
- Deferred: "Donation D-1014 was considered after D-1002 because D-1002 had less remaining shelf life under the urgency-first greedy rule."

### Required metrics
Donations received / assigned / unassigned; food quantity rescued; food quantity at risk (unassigned or expired); urgent rescue rate (% of earliest-expiring donations assigned); recipient capacity utilization (assigned qty / available recipient capacity); volunteer capacity utilization (assigned qty / volunteer capacity); FIFO-vs-greedy comparison (difference in assigned count, rescued quantity, urgent rescue rate, or another justified metric).

### Required tests
Normal match; duplicate donation ID; expired/nearly expired donation; no compatible food type; insufficient recipient capacity; no volunteer with enough vehicle capacity; two donations competing for the same capacity; empty inputs; a case where FIFO and greedy differ; a fairness/starvation case (which donation is deferred and why). Each has a matching hand-built dataset in `data/scenarios/` (see `data/README.md`).

## Repo layout

```
main.py                      CLI entry point (currently empty)
rescueroute/
  models.py                  Dataclasses: Donation, Recipient, Volunteer, Assignment; Status enum (done)
  loader.py                  CSV/JSON loading + validation (empty, to do)
  strategies/fifo.py         FIFO baseline (empty, to do)
  strategies/greedy.py       Greedy urgency-first (empty, to do)
data/
  README.md                  Data format and dataset catalogue — read this before touching data
  scripts/generate_data.py   Generates all sample data (data/scale/, data/scenarios/ are gitignored)
docs/                        Project brief PDF
```
No `tests/` directory yet. Create `tests/` and run with `python -m unittest` or `pytest`. Update this layout section as files fill in.

Run `python data/scripts/generate_data.py` once after cloning to create the sample data. Edit the generator, never the generated files.

## Data model conventions

- **Times** are integer minutes since simulation start (0 = 8:00 AM). No datetimes.
- `arrival_order` is **not** in the files; the loader assigns it from row order (`enumerate`), JSON array order likewise.
- `accepted_food_types` is a JSON array or a `;`-separated CSV cell; load it as `set[str]`.
- CSV values are all strings, so the loader must convert numeric fields to `int`.
- Food types: `prepared_meals, produce, bakery, dairy, frozen, canned_goods`. Areas: `north, south, east, west, central`.
- Store entities in `dict`s keyed by ID; use `set`s for accepted food types and duplicate-ID detection; use a `list` for assignment history (ordered audit trail); use a `dict` for metrics; use `heapq` or a sorted list for the greedy pending queue only because the priority rule needs it.

## Engineering rules

- **MVP first.** No dashboards, maps, APIs, optimization libraries, or Streamlit until all required features work. Prefer the standard library; `requirements.txt` is currently empty. Document any external library, dataset, or code reference.
- **Both strategies must run on identical input** and use the same feasibility check, so differences come only from ordering and not from different rules. Share feasibility, capacity-tracking, and explanation code rather than duplicating it.
- Strategies must not mutate the loaded input; each run needs fresh capacity state.
- Keep the code simple and explainable. Every group member must be able to explain every line, so avoid clever abstractions.
- Validation failures should be reported clearly (which record, which field, why), not crash with a bare traceback.
- Match existing style: dataclasses with trailing field comments, type hints, a short module docstring.

## Open decisions (not yet fixed; confirm with the user before assuming)

- **Exact greedy rule.** The README must state it precisely. Brief's example: least remaining shelf life first; tie → larger quantity; tie → earlier arrival.
- **Feasibility details.** Whether area must match between donation, volunteer, and recipient, how scheduled time is computed (`scheduled_time_start/end` on `Assignment`), whether volunteer `maximum_pickups` and availability window are enforced per pickup, and whether recipient capacity is a single total or per-time.
- **"Urgent" definition** for the urgent rescue rate (e.g. earliest-expiring N% of donations).
- **Output format** of the comparison report.

## Final deliverables (README must cover)

Architecture; algorithm design with the precise greedy rule and what it optimizes locally, why it is reasonable, and where it can fail or cause starvation; complexity analysis (define D, R, V; identify the dominant work; state assumptions); limitations; setup instructions; sample inputs; FIFO-vs-greedy comparison report; team contributions. Also a 3-5 minute demo and individual contribution statements. The repo should be something a student would show an internship interviewer: concise, tested, honestly documented.

## AI use, citation, and attribution (mandatory)

Course policy: AI tools (ChatGPT, Copilot, Claude, Codex, etc.) are permitted **only if cited**. This applies to every tool, including ones used outside the repo (e.g. ChatGPT in a browser); humans must log those by hand. Each submission must include a short **"Tools & Sources"** section describing the prompts, the outputs used, and how the tool's response was modified. Uncited AI-assisted work is treated as plagiarism under CSUF's Academic Dishonesty Policy. Several people work in this repo, so we also need to know **who** prompted what.

Every agent working in this repo must follow these rules:

1. **Log every AI contribution** in `docs/TOOLS_AND_SOURCES.md` (create it if missing; the README's "Tools & Sources" section summarizes or links to it). Append one entry per contribution, with:
   - **Date**
   - **Human requester**: the team member who gave the prompt. Take it from `git config user.name` / the user's stated name. If it is unclear, **ask**; never guess or leave it blank.
   - **Tool/model**: e.g. "Codex (model name)" or "Claude Code (claude-sonnet-5-5)"; use whatever tool you actually are
   - **Prompt summary**: what was asked
   - **Output used**: which files/functions were created or changed
   - **Modifications**: how the output was edited, reviewed, or tested by a human afterwards (leave "pending human review" if not yet done)
2. **Mark AI-generated code in the source.** Add a short note to the module docstring or above the function, e.g. `# AI-assisted: <tool name>, requested by <name>, see docs/TOOLS_AND_SOURCES.md`. Don't mark files with no AI contribution.
3. **Attribute in commits.** Commit messages for AI-assisted work include the requester and the tool, e.g. a trailer `Requested-by: <name>` plus a `Co-Authored-By` line naming the tool (follow your tool's own convention). Never commit AI work under a name that hides its origin.
4. **Cite outside sources too.** Any tutorial, StackOverflow answer, library, or dataset used goes in the same file with its URL.
5. **Do the log update in the same change as the work**, not later. If you create or edit code, the log entry is part of the task and you should mention it in your final summary.
6. Students must understand every line they submit. Explain your code clearly, and don't add code that nobody on the team could justify.

## Git

Commit history should show meaningful contributions from each member. Use conventional-style messages as in the existing log (`feat:`, `fix:`). Do not commit generated data or `output/`.
