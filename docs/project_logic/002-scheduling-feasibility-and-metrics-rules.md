# 002: Scheduling, feasibility, greedy, metrics, and report rules

AI-assisted: Claude Code (claude-opus-5-5), requested by Dom, see docs/TOOLS_AND_SOURCES.md

**Status: Accepted** (2026-10-14, decided by Dom, Algorithm & Optimization Lead). Code and tests should follow these rules. Greedy tie-breakers were settled later the same day. This file supersedes [001](001-near-expiry-and-pickup-timing.md): it keeps 001's structure (travel time plus a minimum shelf-life buffer) but changes the numbers and the volunteer timing model.

## Timing

| Constant | Value | Meaning |
|---|---|---|
| `TRAVEL_MINUTES` | 15 | Base time for one trip, pickup to drop-off |
| `CROSS_AREA_MINUTES` | 15 | Added once for each leg that crosses areas (see below) |
| `MIN_MINUTES_LEFT` | 15 | Food must arrive with at least this much shelf life left |

**Trip duration** for donation `d`, recipient `r`, volunteer `v`:

```
trip = TRAVEL_MINUTES
     + CROSS_AREA_MINUTES  if v.pickup_area != d.pickup_area     (volunteer drives to the donor's area)
     + CROSS_AREA_MINUTES  if d.pickup_area != r.dropoff_area    (donation crosses to the recipient's area)
```

So a trip takes 15, 30, or 45 minutes. A same-area donation needs at least 30 minutes between ready time and expiry to be rescuable.

**Any area is allowed.** Areas never make a match infeasible on their own; they only add time. (`require_area_match` stays off.)

**Volunteers start every trip from their home `pickup_area`**, not from their last drop-off. Chaining trips by location would be more realistic, but inserting a trip into a gap would change the start location of the next booked trip, which could make an already-assigned trip late. That is route planning, which the brief lists as a stretch feature. This is a stated limitation.

## Volunteer schedule (busy model with gap filling)

A volunteer is **busy from the start of a trip until its delivery arrival**. Each volunteer keeps a list of booked trips `(start, end)` for the run. Trips are half-open intervals: a trip ending at minute 15 lets the next one start at minute 15.

To place a new trip of length `trip`:

```
start = max(d.ready_time, v.availability_start)
for each booked (a, b) of v, in order of a:
    if start < b and a < start + trip:     # overlaps
        start = b                          # try right after that trip
arrival = start + trip
```

The trip is feasible on time only if all of these hold:

```
arrival + MIN_MINUTES_LEFT <= d.expiry_time
arrival <= r.closing_time
arrival <= v.availability_end
```

The whole trip, including the drive to the donor's area, is booked from `start`. This is slightly pessimistic (a real volunteer could leave early to arrive at the ready time) but keeps the rule simple.

The assignment stores `scheduled_time_start = start` and `scheduled_time_end = arrival`. Greedy processes donations out of time order, which is why gaps are needed: a donation ready at minute 0 that is processed after a trip booked at minute 300 can still use the free time before minute 300.

## Other feasibility rules

- **Recipient capacity** is one total for the whole run; it never frees up.
- **Vehicle capacity** is a limit per trip: each donation's quantity must fit in the vehicle.
- **Maximum pickups** and the **availability window** are enforced (settled 2026-10-05).
- **Match selection:** both strategies take the **first feasible recipient and volunteer pair, in input order**. The strategies differ only in the order they process donations.

## Greedy rule

Donations are sorted once, before the run, by:

1. **Earliest `expiry_time`** (the absolute deadline, not `expiry_time - ready_time`). Urgency, as the brief requires.
2. **Fewest compatible recipients.** Among equally urgent donations, the hardest to place goes first, so it is not crowded out by donations that have alternatives.
3. **Larger quantity.** Among equally urgent and equally constrained donations, rescue more food.
4. **Earlier `arrival_order`.** First come, first served; makes the order fully defined.

**Compatible recipients** for a donation = recipients whose `accepted_food_types` include its `food_type` **and** whose starting `capacity` is at least its `quantity`. Both come straight from the input, so the count is computed once before sorting and never changes. Area and timing are not part of it (areas only add time, and timing depends on volunteer schedules).

**Cost:** counting is one O(D·R) pass before the O(D log D) sort. Matching stays O(D·R·V), so the overall bound is unchanged.

## Deferred explanations

- Deferred is **not a final status**. Every donation gets exactly one `Assignment`, `ASSIGNED` or `UNASSIGNED`.
- A donation is **deferred** when a donation that arrived after it was processed before it (it was "jumped").
- **Only deferred donations that end up `UNASSIGNED` get a deferral sentence.** A donation that was jumped but still assigned lost nothing, so its normal assigned explanation is enough. This meets the brief: every donation gets an assigned or unassigned explanation (§5), and the starvation case shows which donation was deferred and why (§8). The brief does not require a sentence for every reordering.
- The sentence names the **closest jumper**: of the donations processed before it that arrived after it, the one processed most recently. Donations with **zero compatible recipients** are skipped (they could never be assigned, so naming them would be misleading). If no jumper remains, no deferral sentence is added.
- Example (`starvation`): D-1001 is unassigned; its closest jumper is D-1005, so its explanation ends "...was considered after D-1005 because D-1005 expires sooner (minute 120 vs 2880)."
- The sentence names the sort level that decided the order:
  - "...was considered after D-1002 because D-1002 expires sooner (minute 90 vs 120)."
  - "...because both expire at minute 120 and D-1002 has fewer compatible recipients (1 vs 4)."
  - "...because both expire at minute 120 with 2 compatible recipients each, and D-1002 is larger (40 vs 15 units)."
  - "...because both expire at minute 120 with 2 compatible recipients and 40 units each, and D-1002 arrived first."

## Metrics

| Metric | Definition |
|---|---|
| Urgent donations | The earliest-expiring 25% of donations by `expiry_time` |
| Urgent rescue rate | Urgent donations assigned ÷ urgent donations |
| Recipient capacity utilization | Assigned quantity ÷ total `capacity` of **all** recipients |
| Volunteer capacity utilization | Assigned quantity ÷ sum of `vehicle_capacity × maximum_pickups` over all volunteers |
| Food quantity at risk | Total unassigned quantity. Expired donations are unassigned, so they are counted once, there |

## Validation and output

- **Bad records:** the first record with an ID is kept; later duplicates and invalid rows are dropped and reported, and the run continues (current `loader.py` behavior). `main.py` prints these errors before the results.
- **CLI:** takes a dataset folder and runs **both** strategies by default; prints to the terminal; an optional `--out` saves the report.
- **Order:** each strategy's decisions are listed **in the order that strategy processed them**, including in the side-by-side report, so the reordering is visible.

## Effect on the scenario datasets

Checked by hand. Every intended outcome in `data/README.md` still holds:

| Scenario | Outcome |
|---|---|
| `normal_match` | Trip 0-15, 75 min left → **assigned** |
| `expired_donation` | D-1001 **unassigned** (expired at ready time); D-1002 **unassigned** (arrives at 15, expires at 10); D-1003 **assigned** |
| `competing_capacity` | One assigned. FIFO assigns D-1001 (arrived first); greedy assigns D-1002 (expires at 300, before D-1001's 400) |
| `fifo_vs_greedy_differ` | FIFO 1, greedy 2, as designed |
| `starvation` | Greedy: meals booked 0-15, 20-35, 40-55, 60-75, all with 45 min left; V-301's 4 pickups are used up and D-1001 starves. FIFO: D-1001 0-15, then meals at 15-30, 30-45, 45-60; D-1005 unassigned (no pickups left) |
| `duplicate_ids` | Surviving D-1001 and D-1002 both assigned to V-301 (0-15, 15-30) |
| other scenarios | Fail on food type, capacity, or vehicle size before timing matters |

All scenarios are single-area, so **no scenario yet tests the cross-area penalty or gap filling.** New scenarios are needed for both.

## What changes in the code

- `rescueroute/feasibility.py`: `travel_minutes` 0 → 15, `min_minutes_left` 1 → 15; trip duration depends on areas; `CapacityTracker` keeps each volunteer's booked trips; `schedule` finds the earliest free gap; `unassigned_reason` needs a "volunteer busy" explanation.
- `rescueroute/strategies/greedy.py`: count compatible recipients per donation, sort by the four-level key, add deferral sentences to unassigned deferred donations.
- Metrics and `main.py`: follow the definitions above.
- `tests/test_week1.py`: `test_expired_donation_is_not_assigned` can now assert D-1002 is unassigned.
