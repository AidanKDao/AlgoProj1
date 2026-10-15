
# AlgoProj1 — RescueRoute

## Project Overview

RescueRoute is a Python-based food donation scheduling project.

Our goal is to answer the following question:

How can we prioritize time-sensitive food donations and assign them to compatible recipients and volunteers in a way that is efficient, transparent, and easy to explain?

We compare two scheduling algorithms, FIFO (First In, First Out) and Greedy, to evaluate which approach can assign more donations and rescue more food under the same conditions.

## Requirements

- Command-line Python application
- Load donation, recipient, and volunteer data from CSV or JSON files
- Validate IDs, quantities, food types, capacities, availability, and time values
- Identify feasible donation-recipient-volunteer matches
- Implement a FIFO baseline and a clearly defined greedy strategy
- Produce explainable assignment or rejection messages for every donation
- Calculate metrics to compare both strategies
- Include automated tests for normal and edge cases

## Team Role Statement

Our team is split into the following roles:

- **Algorithm & Optimization Lead: Dominic Dionne**
  FIFO scheduler, greedy rule, priority selection, complexity analysis, and strategy comparison.

- **Data & Matching Lead: Kaleb**
  Input files, validation, compatibility checks, capacity rules, data structures, and test data.

- **Product & Quality Lead: Soheil Douzandeh**
  Explainable output, performance metrics, automated tests, README documentation, demo materials, and CLI improvements.

- **4th Team Role:** Pending confirmation.

All team members contribute to testing, debugging, code review, and project documentation.

## Scheduling Strategies

### FIFO (First In, First Out)

FIFO processes donations in the order they are received.

For each donation, the algorithm searches for a compatible recipient and an available volunteer.

If a feasible match is found, the donation is assigned. Otherwise, it is marked unassigned with an explanation.

FIFO serves as the baseline for evaluating the greedy strategy.

### Greedy Strategy

The greedy algorithm prioritizes donations using the following rules:

1. Soonest expiration time
2. Fewest compatible recipients
3. Largest food quantity
4. Earliest arrival order

The goal is to prioritize time-sensitive donations and improve the total amount of food successfully assigned.

Both strategies use the shared feasibility rules to check compatibility, capacity, timing, and volunteer availability.

## Running the Project

Use Python 3 and run the following commands from the project's root directory.

### 1. Generate Sample Data

```bash
python3 data/scripts/generate_data.py
```

This generates sample CSV and JSON datasets for testing.

Generated datasets are ignored by Git, so this command should be run after cloning the repository.

### 2. Run the Report (FIFO vs. Greedy)

Run both strategies on the small dataset and print the full report:

```bash
python3 main.py
```

Choose another dataset folder, such as a hand-built scenario or a larger dataset, and optionally save the report:

```bash
python3 main.py data/scenarios/starvation
python3 main.py data/scale/medium --out report.txt
```

The report prints, in this order: validation errors (invalid records are skipped and the run continues), then **every donation's explanation for each strategy in the order that strategy processed it**, then the metrics table and the FIFO-vs-greedy differences. Both strategies run on the same loaded data and the same feasibility rules.

`python3 compare_strategies.py [folder]` prints only the metrics table.

### 3. Run Automated Tests

Run the complete test suite:

```bash
python3 -m unittest discover -s tests -t . -v
```

All 62 automated tests currently pass (44 at the Week 2 checkpoint).

The tests cover input validation, matching feasibility, scheduling behavior, performance metrics, and strategy comparison.

## Performance Metrics

To evaluate both strategies fairly, we calculate:

- **Total Donations:** Number of donations in the dataset.
- **Assigned Donations:** Number of donations successfully matched.
- **Unassigned Donations:** Number of donations that could not be matched.
- **Total Food Units:** Total food quantity available.
- **Food Rescued:** Total food units successfully assigned.
- **Assignment Rate:** Percentage of donations successfully assigned.
- **Food Rescue Rate:** Percentage of available food units successfully assigned.
- **Food at Risk:** Total quantity of donations left unassigned (expired donations are counted once, here).
- **Urgent Rescue Rate:** Percentage of urgent donations assigned. Urgent donations are the earliest-expiring 25% by expiry time, rounded up, with ties broken by arrival order.
- **Recipient Utilization:** Assigned quantity divided by the total capacity of all recipients.
- **Volunteer Utilization:** Assigned quantity divided by the sum of vehicle capacity times maximum pickups over all volunteers.

These metrics allow us to compare how efficiently FIFO and Greedy allocate available resources.

## Week 2 Comparison Results

The following results were obtained using the generated small dataset containing 25 donations, with volunteers booked one trip at a time (a volunteer cannot take overlapping trips).

| Metric | FIFO | Greedy |
|---|---:|---:|
| Total Donations | 25 | 25 |
| Assigned Donations | 19 | 20 |
| Unassigned Donations | 6 | 5 |
| Total Food Units | 1084 | 1084 |
| Food Rescued | 814 | 816 |
| Assignment Rate | 76.00% | 80.00% |
| Food Rescue Rate | 75.09% | 75.28% |
| Food at Risk | 270 | 268 |
| Urgent Rescue Rate (7 urgent donations) | 85.71% | 100.00% |
| Recipient Utilization | 87.53% | 87.74% |
| Volunteer Utilization | 44.73% | 44.84% |

### Results Summary

On this dataset, Greedy performed better than FIFO.

- Greedy assigned 1 additional donation.
- Greedy rescued 2 additional food units.
- Assignment rate improved by 4 percentage points.
- Food rescue rate improved by 0.19 percentage points.

These results suggest that prioritizing time-sensitive donations can improve resource allocation.

However, Greedy is not guaranteed to outperform FIFO on every dataset. Additional testing with different scenarios and dataset sizes is needed to evaluate overall performance.

## Architecture

```text
CSV / JSON files --> loader.py --> models (Donation, Recipient, Volunteer)
                                         |
                      feasibility.py (shared rules + CapacityTracker)
                         |                                  |
                  strategies/fifo.py                strategies/greedy.py
                         |                                  |
                         +---------- list of Assignment ----+
                                         |
                       metrics.py --> report.py --> main.py (terminal / --out file)
```

- **`models.py`**: dataclasses `Donation`, `Recipient`, `Volunteer`, `Assignment` and the `Status` enum.
- **`loader.py`**: reads CSV or JSON, converts values, assigns `arrival_order` from row order, and reports every problem with its row, ID, field and reason. Invalid records are skipped.
- **`feasibility.py`**: the one shared rule book. `check_pair` answers "can this donation go to this recipient with this volunteer?", `find_match` returns the first feasible pair, and `CapacityTracker` holds the state that changes during a run (recipient capacity left, volunteer pickups and booked trips). It also writes the human-readable explanations.
- **`strategies/`**: `run_fifo` and `run_greedy`. They differ **only in the order they process donations**; both use the same feasibility code, each with a fresh `CapacityTracker`, and neither changes the loaded input.
- **`metrics.py`** and **`report.py`**: the required metrics and the text report.

## Data Model

Times are whole minutes since the simulation start (0 = 8:00 AM). Records are stored in dictionaries keyed by ID. Sets are used for accepted food types and for duplicate-ID detection, and a list keeps the ordered assignment history.

| Entity | Fields |
|---|---|
| Donation | `donation_id`, `donor_name`, `food_type`, `quantity`, `ready_time`, `expiry_time`, `pickup_area`, `arrival_order` |
| Recipient | `recipient_id`, `organization_name`, `accepted_food_types`, `capacity`, `closing_time`, `dropoff_area` |
| Volunteer | `volunteer_id`, `vehicle_capacity`, `maximum_pickups`, `availability_start`, `availability_end`, `pickup_area` |
| Assignment | `donation_id`, `recipient_id`, `volunteer_id`, `scheduled_time_start`, `scheduled_time_end`, `decision_reason`, `status` |

**Feasibility rules** (a match is feasible only if all hold; the rules are in `docs/project_logic/002-scheduling-feasibility-and-metrics-rules.md`):

- the recipient accepts the donation's food type;
- the recipient has enough capacity left (one total for the whole run);
- the volunteer's vehicle can carry the quantity (a per-trip limit);
- the volunteer has not reached `maximum_pickups`;
- the trip does not overlap another trip booked for that volunteer, so a new trip moves to the earliest free gap;
- delivery arrives at least 15 minutes before the donation expires, no later than the recipient's closing time, and within the volunteer's availability window.

A trip takes 15 minutes, plus 15 for each leg that crosses areas (volunteer home to pickup, pickup to recipient), so 15, 30, or 45 minutes. Any area may be matched; areas only add time.

## Greedy Rule (precise)

Donations are sorted once, before the run, by:

1. **Earliest `expiry_time`** (the absolute deadline).
2. **Fewest compatible recipients** (accepts the food type and has enough starting capacity), so the hardest donation to place is not crowded out.
3. **Larger quantity.**
4. **Earlier arrival order**, so the order is fully defined.

Each donation then takes the first feasible recipient and volunteer, in input order, exactly as in FIFO.

**What it optimizes locally:** at each step the donation closest to expiring gets the first pick of the remaining capacity and volunteer time, so the food most at risk of being lost is placed first.

**Why it is reasonable:** food that expires soon can be lost, while food with a long shelf life can wait. On our generated datasets this raised the urgent rescue rate sharply (see the comparison below).

**Where it can fail or cause starvation:** it is a local rule, not a global optimum.

- A donation with a long shelf life can be pushed back repeatedly. In the `starvation` scenario the canned goods (D-1001) arrive first but are processed last, and the lone volunteer runs out of pickups before reaching it. The report names the donation that jumped ahead and why.
- Putting small urgent donations first can use up capacity or volunteer time that a large donation needed. In `starvation`, FIFO rescues 50 units and greedy only 40.
- It never reconsiders a placement, so it can give up total food rescued to protect the most urgent donations.

## Complexity Analysis

Let **D** = donations, **R** = recipients, **V** = volunteers, and **P** = the most trips one volunteer holds (at most `maximum_pickups`).

- **Feasibility of one match** is constant work, plus a scan of that volunteer's booked trips for the gap search, so O(P).
- **FIFO:** each donation tries recipient-volunteer pairs until one works, so the dominant work is O(D · R · V · P) in the worst case (when many donations match nothing).
- **Greedy:** counting compatible recipients is O(D · R), sorting is O(D log D), then the same matching loop, so the matching term O(D · R · V · P) still dominates.
- **Explanations for unassigned donations** add O(R · V) per unassigned donation, which does not change the bound.
- **Space:** O(D + R + V) for the records and the assignment list, plus O(D) booked trips.

**Assumptions:** P is small (bounded by each volunteer's maximum pickups), so the matching loop is effectively O(D · R · V); the first feasible pair is accepted, with no search for a best pair.

**Measured (both strategies together):** the small dataset (25/6/6) and the medium dataset (100/20/15) finish instantly (about 0.06 s for medium), and the large dataset (1,000/120/90) takes about 14 seconds. The 10,000-donation `xlarge` dataset is far slower, as the D · R · V term predicts, and was not used for results.

## FIFO vs. Greedy on Larger Datasets

Run with `python3 main.py data/scale/<name>`. Greedy rescued more food than FIFO on every generated dataset we ran.

| Dataset | Assigned (FIFO / Greedy) | Food rescued (FIFO / Greedy) | Urgent rescue rate (FIFO / Greedy) |
|---|---|---|---|
| small (25 donations) | 19 / 20 | 814 / 816 | 85.71% / 100% |
| medium (100) | 61 / 61 | 2335 / 2484 | 64% / 92% |
| large (1,000) | 342 / 359 | 14027 / 15259 | 34% / 99.2% |

The gain comes mostly from the urgent donations. It is not guaranteed: on the hand-built `starvation` scenario FIFO rescued more food.

## Limitations

- **Educational prototype on simulated data.** It makes no claim of food-safety, medical, or operational readiness.
- Volunteers always start each trip from their home area, not from their last drop-off, so routes are not chained.
- Recipient capacity is one total for the whole run and never frees up.
- Travel times are fixed constants (15 minutes plus 15 per area-crossing leg), not real distances.
- Both strategies take the first feasible match, not the best match, and greedy never undoes a placement.
- Invalid records are skipped and reported rather than given their own explanation in the report.
- The matching loop grows with D · R · V, so very large datasets are slow.

## Tools & Sources

AI coding tools (Claude Code) were used by several team members. Every AI contribution is logged in [docs/TOOLS_AND_SOURCES.md](docs/TOOLS_AND_SOURCES.md) with who prompted it, the model, what was used, and how it was reviewed. Outside sources are listed there with their read status. The rules the team accepted are in [docs/project_logic/](docs/project_logic/). The code uses only the Python standard library.

## Team Contributions

Roles are listed under Team Role Statement. Each member's individual contribution statement is submitted separately, and the commit history (`git log`) shows who wrote what.

## Project Structure

```text
AlgoProj1/
|
|-- data/
|   |-- scripts/
|   |   `-- generate_data.py
|   |-- scenarios/
|   `-- scale/
|
|-- docs/
|
|-- rescueroute/
|   |-- strategies/
|   |   |-- fifo.py
|   |   `-- greedy.py
|   |-- models.py
|   |-- loader.py
|   |-- feasibility.py
|   |-- metrics.py
|   `-- report.py
|
|-- tests/
|   |-- test_week1.py
|   |-- test_loader.py
|   |-- test_feasibility.py
|   |-- test_greedy.py
|   |-- test_metrics.py
|   |-- test_volunteer_schedule.py
|   |-- test_main.py
|   |-- test_week2.py
|   `-- test_compare_strategies.py
|
|-- compare_strategies.py
|-- main.py
|-- README.md
`-- requirements.txt
```

## Week 1 Checkpoint

- [x] Repository created
- [x] Data model established
- [x] Input validation implemented
- [x] FIFO baseline implemented
- [x] Sample input data generation included
- [x] Initial automated tests included
- [x] Team roles documented

## Week 2 Checkpoints

- [x] Implement greedy strategy
- [x] FIFO vs. Greedy comparison
- [x] All 10 required tests (44 passing)
- [x] Performance metrics
- [x] Updated README documentation

## Week 3 Checkpoints

- [ ] Polish code
- [ ] Finalize tests
- [ ] Finalize documentation
- [ ] Demo materials
- [ ] Prepare presentation (live or video demo)
- [ ] Final report
- [ ] Contribution statements

## Current Progress

### Week 1 — Foundation

Completed the initial project structure, data model, validation system, FIFO baseline, and automated tests.

### Week 2 — Strategy Comparison

Implemented the greedy strategy and developed performance metrics to compare FIFO and Greedy.

Created a reusable comparison program and added automated tests.

All 44 tests passed during local Week 2 verification; 62 pass now.

### Week 3 — Finalization

Next steps include reviewing the code, finalizing documentation, preparing demonstration materials, and completing the final report and presentation.
