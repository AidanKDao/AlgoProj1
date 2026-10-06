# AlgoProj1

We need to answer: How can we prioritize time-sensitive food donations and assign them to compatible recipients and volunteers in a way that is efficient, transparent, and easy to explain?

## Requirements

- Command-line Python application
- Loads donation, recipient, and volunteer information from CSV or JSON files
- Validates IDs, quantities, food types, capacities, availability, and time values
- Identifies feasible donation-recipient-volunteer matches
- Implements a FIFO baseline and one clearly defined greedy strategy
- Produces an explainable assignment or rejection message for every donation
- Calculates metrics that compare the two strategies
- Includes automated tests for normal and edge cases

## Team Role Statement
Our team is split into the following roles:
- Algorithm & Optimization Lead: Dominic Dionne (FIFO scheduler, greedy rule, priority selection, complexity analysis, strategy
comparison.)
- Data & Matching Lead: Kaleb (Input files, validation, compatibility checks, capacity rules, data structures, test data.)
- Product & Quality Lead: Saheil (Explainable output, metrics, tests, README, demo materials, interface or CLI polish.)
- Pending 4th role...

## Running the Project

From the project root directory, run:

```bash
python main.py
```

## Week 1 Checkpoint
- [x] Repository created
- [x] Data model established
- [x] Input validation implemented
- [ ] FIFO baseline implemented
- [x] Sample input data included
- [ ] Initial automated tests included
- [x] Team roles documented
