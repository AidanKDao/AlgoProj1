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

## Team Roles

- Project Owner: Coordinates project goals, requirements, and team progress
- Development Team: Implements the scheduling algorithms, validation, and data processing
- Testing Team: Creates test cases and verifies FIFO and scheduling behavior
- Documentation Team: Maintains project documentation, setup instructions, and checkpoint evidence

## Running the Project

From the project root directory, run:

```bash
python main.py

## Week 1 Checkpoint
- Repository created
- Data model established
- Input validation implemented
- FIFO baseline implemented
- Sample input data included
- Initial automated tests included
- Team roles documented