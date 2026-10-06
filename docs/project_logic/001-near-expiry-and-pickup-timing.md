# 001: Near-expiry donations and pickup timing

AI-assisted: Claude Code (claude-opus-5-5), requested by AidanDao, see docs/TOOLS_AND_SOURCES.md

**Status: Proposed.** This is not yet agreed by the team. Do not implement it as settled behavior.

## The question

In `data/scenarios/expired_donation`, donation D-1002 is ready at minute 0 and expires at minute 10. Can it be rescued?

The data model has `ready_time` and `expiry_time` on donations, `closing_time` on recipients, and an availability window on volunteers, but it says nothing about **how long a pickup takes**. Without that, "10 minutes left" has no answer: the trip might take 5 minutes or 45. The `Assignment` dataclass already has `scheduled_time_start` and `scheduled_time_end`, so the team needs a rule for filling them in.

## What real food-rescue practice suggests

Real programs treat transport time as a hard limit for perishable food and do not move food that cannot arrive in usable condition:

- **Food Code 3-501.19 (time as a public health control):** food kept out of temperature control may be used for at most 4 hours and must then be discarded. *Source read:* [Reading, MA: Time as a Public Health Control](https://www.readingma.gov/948/Time-as-a-Public-Health-Control-TPHC).
- **Transport-time limits:** a partner food-rescue training form states that, with a freezer blanket but no refrigerated vehicle, travel from donor to agency should not exceed **15 minutes**. A search summary also mentioned a food-bank guide allowing **30 minutes**, but the specific guide was not identified. *Search-result summaries only; originals not retrieved:* [Partner Food Rescue Training Quiz](https://app.smartsheet.com/b/form/a240b7197db4417abf03108bc8948170).
- **Time above 41°F:** grocery-rescue guides say not to accept perishable product held above 41°F for more than 2 hours. *Search-result summary only; original not retrieved:* [Grocery Rescue Program Guide](https://www.firstfoodbank.org/wp-content/uploads/2023/10/Grocery-Rescue-Program-Guide.pdf).
- **Driver practice:** volunteer driver listings say to deliver collected food immediately and to refuse product that doesn't meet food-safety criteria. *Search-result summary only:* e.g. [Food Rescue Driver listing (idealist.org)](https://www.idealist.org/en/volunteer-opportunity/b93ffd8317f24286b966c2ad5ce958ce-food-rescue-driver-dc-metro-area-the-jj-center-inc-washington).

The takeaway for the simulation: **a donation is only rescued if it can reach the recipient with usable time left, and the trip itself takes a fixed, short amount of time.** The numbers below are simulation parameters informed by these practices, not derived from them.

## Proposed rule

Two constants (one place in the code, e.g. a `config.py` or the top of the matching module):

| Constant | Proposed value | Why |
|---|---|---|
| `TRAVEL_MINUTES` | 30 | One pickup-and-dropoff trip. Upper end of the 15-30 minute non-refrigerated transport limits above. |
| `MIN_MINUTES_LEFT_ON_ARRIVAL` | 15 | The recipient needs some time to store or serve the food. Arriving at the exact minute of expiry rescues nothing. |

For a donation `d`, recipient `r`, and volunteer `v`:

```
start   = max(d.ready_time, v.availability_start)
arrival = start + TRAVEL_MINUTES

feasible on time  if  arrival + MIN_MINUTES_LEFT_ON_ARRIVAL <= d.expiry_time
                 and  arrival <= r.closing_time
                 and  arrival <= v.availability_end
```

These checks are in addition to the existing food-type, recipient-capacity, vehicle-capacity, and `maximum_pickups` checks. The assignment stores `scheduled_time_start = start` and `scheduled_time_end = arrival`.

In practice this means a donation needs at least **45 minutes** between its ready time and its expiry to be rescuable at all.

### Volunteer timing assumption

**Each pickup is an independent direct trip.** A volunteer is limited only by `maximum_pickups`, their availability window, and vehicle capacity. We do *not* track a volunteer being busy until their previous trip ends.

- **Why:** it keeps the matching simple and explainable, and `maximum_pickups` already models a volunteer's limited time.
- **Limitation:** a volunteer could in theory be scheduled for two trips at overlapping times. A "busy until" model would be more realistic, but it would make the `starvation` scenario show "volunteer busy" instead of starvation, and it adds route-planning complexity the brief lists as a stretch feature.

The constant travel time also ignores area: crossing town takes the same 30 minutes as staying in one area. Whether areas must match is a separate open decision.

### Example explanation messages
- "Donation D-1002 could not be assigned because it expires at minute 10, but the earliest delivery is minute 30, and recipients need at least 15 minutes of shelf life left on arrival."
- "Donation D-1001 could not be assigned because it was already expired when it became ready for pickup (ready and expiry both at minute 60)."

## Effect on the scenario datasets

Checked by hand against every scenario in `data/scenarios/`. Every intended outcome in `data/README.md` still holds:

| Scenario | Outcome under this rule |
|---|---|
| `normal_match` | D-1001 arrives at 30, 60 min left → **assigned** |
| `expired_donation` | D-1001 **unassigned** (expired at ready time); D-1002 **unassigned** (arrives at 30, expires at 10); D-1003 **assigned** |
| `competing_capacity` | Unchanged: both arrive in time; capacity decides |
| `fifo_vs_greedy_differ` | Unchanged: D-1002 arrives at 30 with 60 min left; FIFO 1, greedy 2 |
| `starvation` | Unchanged: meal *i* arrives at 20*i*+30 and expires at 20*i*+60, so each has 30 min left; all four fit V-301's 4 pickups under greedy and D-1001 starves |
| other scenarios | Fail on food type, capacity, or duplicates before timing matters |

**Scale data:** prepared meals have 45-180 minutes of shelf life in the generator, so the shortest ones are right at the 45-minute threshold and become unassignable if the volunteer starts later than the ready time. That is intended: it is what makes urgency-first matter.

## Alternatives considered

| Alternative | Effect |
|---|---|
| No travel time; feasible if `ready_time < expiry_time` | D-1002 is **assigned**. Simple, but "10 minutes left" counts as fine, which no real program would do. |
| Travel time only, no minimum-left buffer (`arrival <= expiry`) | D-1002 still unassigned. Allows food to arrive at the exact minute it expires. |
| `TRAVEL_MINUTES = 15` | Closer to the strictest guidance. Thresholds shrink to 30 minutes total; no scenario outcomes change. |
| Travel time by area (e.g. 15 same area, 30 different area) | More realistic, but it depends on the open area-matching decision. Better as a later stretch. |
| Volunteer busy until previous trip ends | More realistic; breaks the `starvation` scenario as designed (see above). |

## If accepted

- Move the rule into `AGENTS.md` as settled and change this file's status to **Accepted**.
- In `tests/test_week1.py`, `test_expired_donation_is_not_assigned` can then assert that **D-1002 is unassigned** and that its explanation mentions expiry. That assertion is deliberately left out until the team accepts this.
