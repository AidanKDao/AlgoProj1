# Handoff: 2026-10-16 team pickup (temporary, delete after completing)

AI-assisted: Claude Code (claude-sonnet-5-5), requested by AidanKDao, see docs/TOOLS_AND_SOURCES.md

For any AI agent (Claude, Codex, Copilot, Cursor, Gemini) working for Dominic, Kaleb, Soheil or Aidan. **Read `AGENTS.md` first.** It is the rulebook. The accepted scheduling rules are in `docs/project_logic/002-scheduling-feasibility-and-metrics-rules.md`.

**When every task you were given is done, delete this file** (`docs/HANDOFF.md`) in the same change as your last task, and mention that in your summary. Do not delete it if a teammate's tasks are still open: it is shared, so only the last person to finish removes it. If it is already gone, nothing is left to do here.

## State of the project (2026-10-15 end of day)

- `main` is up to date with `origin/main` and contains everything. All 44 tests pass: `python -m unittest discover -s tests -t .`
- **Week 2 is finished:** loader and validation, shared feasibility check, FIFO, greedy (earliest expiry, then fewest compatible recipients, then larger quantity, then earlier arrival), all 10 required tests, and the required metrics (counts, rescued quantity, food at risk, urgent rescue rate, recipient and volunteer utilization).
- `python compare_strategies.py [dataset_folder]` prints a FIFO-vs-greedy metrics table (default `data/scale/small`: FIFO 19 assigned and 814 units rescued, greedy 20 and 839).
- `data/scale/` and `data/scenarios/` are generated and gitignored. Run `python data/scripts/generate_data.py` if they are missing (the tests do it automatically).

## Who is who

- **AidanKDao** (log name for Aidan): 4th role, still "Pending confirmation" in the README.
- **Dominic Dionne** (git `imdomlol`): Algorithm & Optimization Lead. Wrote `greedy.py` and decided the rules in 002.
- **Kaleb Robles**: Data & Matching Lead. Owns `loader.py` and `feasibility.py`.
- **Soheil Douzandeh**: Product & Quality Lead. Wrote the first `metrics.py` and `compare_strategies.py`.

**Nobody is assigned yet.** The team decides who takes what. Ask your user which task is theirs before starting, and check with them before touching anything in a teammate's area (for example `feasibility.py` is Kaleb's, `greedy.py` is Dominic's).

## What is left

### 1. `main.py` CLI

`main.py` is empty. Rule 002, "Validation and output", specifies it:

- takes a dataset folder, prints validation errors (record, field, reason) before results;
- runs **both** strategies by default and prints to the terminal;
- lists **every donation's explanation**, in the order each strategy processed it, side by side so the reordering is visible;
- optional `--out <file>` saves the report;
- shows the metrics table and the FIFO-vs-greedy differences.

Today `compare_strategies.py` prints metrics only, with no per-donation explanations, and the brief requires an explanation for every donation. Either fold `compare_strategies.py` into `main.py` (keep its error handling and tests) or have `main.py` call it. Update `README.md` ("Running the Project" still shows `compare_strategies.py`) and add tests for the new output. `compare_strategies.py` also hardcodes `donations.csv`; JSON input should work too.

### 2. Busy-volunteer schedule with gap filling

This settled rule from 002 ("Volunteer schedule") is **not implemented**. A volunteer is busy from trip start to delivery arrival; each volunteer keeps a list of booked `(start, end)` trips (half-open); a new trip starts at `max(ready_time, availability_start)` and moves to the earliest free gap; `maximum_pickups` and the availability window still apply. Today `CapacityTracker` in `rescueroute/feasibility.py` only counts pickups, so one volunteer can take overlapping trips (for example FIFO on `starvation` books D-1001 and D-1002 on V-301 both at minutes 0 to 15).

Needs: booked trips in `CapacityTracker`, a gap search in `schedule`, a "volunteer busy" explanation in `unassigned_reason`, and new hand-built scenarios (cross-area trips, gap filling) added **in `data/scripts/generate_data.py`**, never by editing generated files. It changes the numbers in the README comparison table, so re-run `compare_strategies.py` and update the README and the metric tests that depend on them. Both strategies must keep sharing one feasibility check.

### 3. Final README and report content

The README must cover (from `AGENTS.md`, "Final deliverables"): architecture; the precise greedy rule, what it optimizes locally, why it is reasonable, and where it can fail or starve a donation (`starvation` scenario); complexity analysis (define D, R, V, name the dominant work, state assumptions; 002 has the greedy cost notes); limitations; setup; sample inputs; the FIFO-vs-greedy comparison; team contributions. Say plainly that this is an educational prototype on simulated data, not food-safety or operational advice.

### 4. Demo, presentation, contribution statements (everyone)

3 to 5 minute demo (live or video), the final report, and an individual contribution statement per member. Commit history should show work from each member.

### 5. AI log review (each person, for their own entries)

Several entries in `docs/TOOLS_AND_SOURCES.md` still say "Pending human review" (six are Kaleb's, plus the newest handoff entries). Only the person who reviewed or edited the output can update its **Modifications** line. Soheil's branch added no entries; if he used any AI tool, he needs to add them by hand. The README's "Tools & Sources" section should summarize or link to this file.

### 6. Small cleanups (anyone, low priority)

- `Status.DEFERRED` in `models.py` is unused. 002 says deferred is not a final status; delete it or leave a comment.
- Three stale lock files may still exist under `.git/` (`stale-index-lock-from-claude`, `stale-index-lock-2-from-claude`, `stale-maintenance-lock-from-claude`). Harmless; the human can delete them.
- The README still lists the 4th team role as pending.

## Rules that are easy to forget

- Do only what your user asked. Check before touching a teammate's area, and do not commit or push unless asked.
- **Log every AI contribution** in `docs/TOOLS_AND_SOURCES.md` with the template in `AGENTS.md` (including docs and deleted files), and mark AI-assisted code with the `# AI-assisted:` note. Ask for the human requester's name; do not guess.
- Commits for AI-assisted work carry a `Requested-by: <name>` trailer plus your tool's co-author line.
- Do not claim food-safety or operational readiness anywhere.
- Both strategies run on identical input and the same feasibility check; they must not mutate the loaded input.
- Many files use CRLF line endings. Keep each file's existing endings when editing.
- Use `python -m unittest discover -s tests -t .` and keep all tests passing before you commit.
