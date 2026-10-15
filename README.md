
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

### 2. Compare FIFO vs. Greedy

Run the comparison using the small dataset:

```bash
python3 compare_strategies.py
```

To compare larger datasets:

```bash
python3 compare_strategies.py data/scale/medium
python3 compare_strategies.py data/scale/large
```

The comparison program loads the same data for both algorithms, runs each strategy independently, and displays their performance metrics side by side.

### 3. Run Automated Tests

Run the complete test suite:

```bash
python3 -m unittest discover -s tests -t . -v
```

At the Week 2 checkpoint, all 29 automated tests passed.

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

These metrics allow us to compare how efficiently FIFO and Greedy allocate available resources.

## Week 2 Comparison Results

The following results were obtained using the generated small dataset containing 25 donations.

| Metric | FIFO | Greedy |
|---|---:|---:|
| Total Donations | 25 | 25 |
| Assigned Donations | 19 | 20 |
| Unassigned Donations | 6 | 5 |
| Total Food Units | 1084 | 1084 |
| Food Rescued | 814 | 839 |
| Assignment Rate | 76.00% | 80.00% |
| Food Rescue Rate | 75.09% | 77.40% |

### Results Summary

On this dataset, Greedy performed better than FIFO.

- Greedy assigned 1 additional donation.
- Greedy rescued 25 additional food units.
- Assignment rate improved by 4 percentage points.
- Food rescue rate improved by 2.31 percentage points.

These results suggest that prioritizing time-sensitive donations can improve resource allocation.

However, Greedy is not guaranteed to outperform FIFO on every dataset. Additional testing with different scenarios and dataset sizes is needed to evaluate overall performance.

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
|   `-- metrics.py
|
|-- tests/
|   |-- test_week1.py
|   |-- test_loader.py
|   |-- test_feasibility.py
|   |-- test_greedy.py
|   |-- test_metrics.py
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
- [x] At least 10 automated tests (29 passing)
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

All 29 tests passed during local Week 2 verification.

### Week 3 — Finalization

Next steps include reviewing the code, finalizing documentation, preparing demonstration materials, and completing the final report and presentation.
