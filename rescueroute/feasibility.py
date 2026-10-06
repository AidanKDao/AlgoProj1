"""
Shared feasibility rules and capacity tracking for both scheduling strategies.

AI-assisted: Claude Code (claude-sonnet-5-5), requested by Kaleb Robles, see docs/TOOLS_AND_SOURCES.md

FIFO and greedy must call the same code here so they differ only in processing order.
Settled checks that run by default: food type, recipient capacity, vehicle capacity,
donation not expired on arrival, recipient still open on arrival, volunteer
maximum_pickups, and volunteer availability window (the last two confirmed by the team).
Rules the team has not settled yet (docs/project_logic/, AGENTS.md "Open decisions")
live in the Rules dataclass and are OFF or placeholder by default:
    require_area_match, travel_minutes / min_minutes_left (proposal 001 suggests 30 and 15).

How the file is organized (top to bottom):
    1. Rules              the settings bundle (which rules are on, travel time)
    2. CapacityTracker    the running tally of capacity used during one run
    3. schedule           works out when a pickup starts and when it arrives
    4. _..._reason checks one small function per rule; each returns None (OK) or a reason
    5. check_pair         runs all the checks for one donation-recipient-volunteer trio
    6. find_match         tries recipients and volunteers in order until one passes
    7. assigned_reason / unassigned_reason   the human-readable explanations
"""

from dataclasses import dataclass

from rescueroute.models import Donation, Recipient, Volunteer


# @dataclass is a decorator: it makes Python write the setup code for a class that only
# holds fields. Each line is  name: type = default value.
@dataclass
class Rules:
    """Settings for the feasibility checks. Rules() uses the defaults; Rules(travel_minutes=30)
    changes just one. Strategies pass the same Rules object to every call so FIFO and
    greedy follow identical rules."""
    travel_minutes: int = 0               # minutes from pickup to delivery
    min_minutes_left: int = 1             # food must arrive at least this long before expiry
    require_area_match: bool = False      # donation pickup area == volunteer area == recipient area
    enforce_maximum_pickups: bool = True      # a volunteer cannot exceed their maximum_pickups
    enforce_volunteer_window: bool = True     # delivery must fit in the volunteer's availability


class CapacityTracker:
    """Remaining capacity for one run. Built fresh from the inputs, which are never changed.

    Think of it as a scoreboard: the loaded recipients and volunteers are the fixed facts,
    and this holds the numbers that change as donations are assigned.
    """

    # __init__ runs automatically when you write CapacityTracker(recipients, volunteers).
    # `self` means "this particular tracker"; it is how the object stores its own data.
    def __init__(self, recipients: dict[str, Recipient], volunteers: dict[str, Volunteer]):
        # Dict comprehension: for each recipient, key = its ID (rid), value = its capacity.
        # This is a COPY, so changing it never changes the Recipient objects themselves.
        self.recipient_remaining = {rid: r.capacity for rid, r in recipients.items()}
        # One entry per volunteer ID (vid), all starting at 0.
        self.volunteer_pickups = {vid: 0 for vid in volunteers}    # pickups given so far
        self.volunteer_quantity = {vid: 0 for vid in volunteers}   # units carried so far

    # The strategy must call this after every successful match. This file never calls it,
    # so without that call capacity would never go down. Returns nothing (-> None).
    def record(self, donation: Donation, recipient_id: str, volunteer_id: str) -> None:
        self.recipient_remaining[recipient_id] -= donation.quantity   # -= means subtract from itself
        self.volunteer_pickups[volunteer_id] += 1
        self.volunteer_quantity[volunteer_id] += donation.quantity


# schedule is a plain function (not indented inside a class, no `self`).
# schedule: works out WHEN a pickup would happen. Takes one donation, one volunteer and the
# rules, and returns a pair (start minute, arrival minute) used by the timing checks below.
def schedule(donation: Donation, volunteer: Volunteer, rules: Rules) -> tuple[int, int]:
    """Return (pickup start, delivery arrival) in minutes."""
    start = donation.ready_time
    if rules.enforce_volunteer_window:
        # max picks the larger number: the volunteer cannot start before they are available
        start = max(start, volunteer.availability_start)
    return start, start + rules.travel_minutes


# ---------- individual checks: each returns None if OK, else a reason ----------
# Each check looks at ONE rule. Returning None means "this rule passes"; returning a
# sentence means "this rule fails, and here is why". check_pair strings them together.

# _expired_reason: checks the food will still be good when it arrives. Returns None if it
# will, or a sentence explaining that it will have expired.
def _expired_reason(donation: Donation, arrival: int, rules: Rules) -> str | None:
    # Fails if the food would arrive with less than min_minutes_left before it expires.
    if arrival + rules.min_minutes_left > donation.expiry_time:
        # Special wording when it was already expired the moment it became ready
        if donation.expiry_time <= donation.ready_time:
            return (f"it was already expired when it became ready for pickup "
                    f"(ready at minute {donation.ready_time}, expires at minute {donation.expiry_time})")
        return (f"it expires at minute {donation.expiry_time}, but the earliest delivery is "
                f"minute {arrival} and it needs at least {rules.min_minutes_left} minute(s) of shelf life left on arrival")
    return None


# _food_reason: checks the recipient accepts this type of food. Returns None if it does,
# or a sentence naming the food type they do not accept.
def _food_reason(donation: Donation, recipient: Recipient) -> str | None:
    # Set membership: is this food type in the recipient's accepted set?
    if donation.food_type not in recipient.accepted_food_types:
        return f"{recipient.organization_name} does not accept {donation.food_type}"
    return None


# _recipient_capacity_reason: checks the recipient still has room for the whole quantity.
# Returns None if there is room, or a sentence saying how much room is left.
def _recipient_capacity_reason(donation, recipient, tracker) -> str | None:
    # Reads the tracker's live number, not recipient.capacity, so earlier assignments count
    remaining = tracker.recipient_remaining[recipient.recipient_id]
    if donation.quantity > remaining:
        return (f"{recipient.organization_name} has only {remaining} units of capacity left "
                f"for {donation.quantity}")
    return None


# _vehicle_reason: checks the volunteer's vehicle can carry the whole quantity in one trip.
# Returns None if it can, or a sentence giving the vehicle size.
def _vehicle_reason(donation: Donation, volunteer: Volunteer) -> str | None:
    # The vehicle limit is per trip, so this compares against vehicle_capacity directly
    if donation.quantity > volunteer.vehicle_capacity:
        return (f"volunteer {volunteer.volunteer_id}'s vehicle holds {volunteer.vehicle_capacity} units, "
                f"less than {donation.quantity}")
    return None


# _area_reason: checks donation, volunteer and recipient are all in the same area. Does
# nothing (returns None) unless the area rule is switched on in Rules.
def _area_reason(donation, recipient, volunteer, rules) -> str | None:
    # Only applies when the rule is switched on. a == b == c checks all three are equal.
    if rules.require_area_match and not (
            donation.pickup_area == volunteer.pickup_area == recipient.dropoff_area):
        return (f"areas do not match (donation in {donation.pickup_area}, volunteer "
                f"{volunteer.volunteer_id} in {volunteer.pickup_area}, "
                f"{recipient.organization_name} in {recipient.dropoff_area})")
    return None


# _pickups_reason: checks the volunteer has not already used up their maximum number of
# pickups. Does nothing unless the pickup rule is switched on in Rules.
def _pickups_reason(volunteer, tracker, rules) -> str | None:
    # Fails once the volunteer's pickup count in the tracker has reached their maximum
    if rules.enforce_maximum_pickups and \
            tracker.volunteer_pickups[volunteer.volunteer_id] >= volunteer.maximum_pickups:
        return (f"volunteer {volunteer.volunteer_id} already has the maximum "
                f"{volunteer.maximum_pickups} pickup(s)")
    return None


# _closing_and_window_reason: checks the recipient is still open when the food arrives, and
# (if the window rule is on) that the volunteer is still available. Returns None or a sentence.
def _closing_and_window_reason(recipient, volunteer, arrival, rules) -> str | None:
    # Two timing checks on the arrival minute: recipient still open, volunteer still available
    if arrival > recipient.closing_time:
        return f"{recipient.organization_name} closes at minute {recipient.closing_time}, before arrival at minute {arrival}"
    if rules.enforce_volunteer_window and arrival > volunteer.availability_end:
        return (f"volunteer {volunteer.volunteer_id} is only available until minute "
                f"{volunteer.availability_end}, before arrival at minute {arrival}")
    return None


# check_pair: the main feasibility question for ONE donation, recipient and volunteer. Runs every
# check above in order and returns the first problem found, or None if the match is feasible.
def check_pair(donation, recipient, volunteer, tracker, rules) -> str | None:
    """None if this donation-recipient-volunteer match is feasible, else why not."""
    _, arrival = schedule(donation, volunteer, rules)   # _ means "ignore the start value"
    # `a or b or c` returns the first one that is not None, so this returns the FIRST failing
    # reason, or None if every check passes. The order here decides which reason the user sees.
    return (_expired_reason(donation, arrival, rules)
            or _food_reason(donation, recipient)
            or _recipient_capacity_reason(donation, recipient, tracker)
            or _vehicle_reason(donation, volunteer)
            or _area_reason(donation, recipient, volunteer, rules)
            or _pickups_reason(volunteer, tracker, rules)
            or _closing_and_window_reason(recipient, volunteer, arrival, rules))


# ---------- finding a match and explaining ----------

# find_match: looks for a recipient and volunteer for ONE donation. Tries each pair in input
# order, using check_pair, and returns the first feasible one (with its start and arrival
# times), or None if no pair works.
def find_match(donation, recipients, volunteers, tracker, rules):
    """First feasible (recipient, volunteer, start, arrival), in dict (input) order, or None."""
    # Two nested loops: every recipient, and for each one every volunteer, in input order.
    # The first pair that passes check_pair wins, which is the "first feasible" FIFO rule.
    for recipient in recipients.values():
        for volunteer in volunteers.values():
            if check_pair(donation, recipient, volunteer, tracker, rules) is None:
                start, arrival = schedule(donation, volunteer, rules)
                return recipient, volunteer, start, arrival
    return None


# assigned_reason: builds the human-readable sentence explaining why a donation WAS assigned.
# It only builds text; it does not decide anything or update the tracker.
def assigned_reason(donation, recipient, volunteer, rules, start: int, arrival: int) -> str:
    return (f"Donation {donation.donation_id} was assigned to {recipient.organization_name} with volunteer "
            f"{volunteer.volunteer_id} because it expires in {donation.expiry_time - start} minutes "
            f"(at minute {donation.expiry_time}) and arrives at minute {arrival}, "
            f"{recipient.organization_name} accepts {donation.food_type}, capacity is available "
            f"({donation.quantity} units), and the volunteer's vehicle can carry the quantity.")


# unassigned_reason: builds the sentence explaining why a donation could NOT be assigned. It
# narrows the candidates one requirement at a time so the message names the real cause.
def unassigned_reason(donation, recipients, volunteers, tracker, rules) -> str:
    """Explain why no feasible match exists, naming the first requirement nobody could meet."""
    prefix = f"Donation {donation.donation_id} could not be assigned because "
    if not recipients:
        return prefix + "there are no recipients."
    if not volunteers:
        return prefix + "there are no volunteers."

    best_start = donation.ready_time      # earliest any pickup could start
    expired = _expired_reason(donation, best_start + rules.travel_minutes, rules)
    if expired:
        return prefix + expired + "."

    # Narrow the recipients and volunteers one requirement at a time. Each list holds the
    # candidates that still pass; the first time a list is empty, that requirement is the
    # reason, which gives a specific message instead of a vague "no match".
    ok_food = [r for r in recipients.values() if _food_reason(donation, r) is None]
    if not ok_food:
        return prefix + f"no recipient accepts {donation.food_type}."
    ok_cap = [r for r in ok_food if _recipient_capacity_reason(donation, r, tracker) is None]
    if not ok_cap:
        return prefix + (f"no compatible recipient had remaining capacity for {donation.quantity} units "
                         f"before the donation expired.")
    ok_vehicle = [v for v in volunteers.values() if _vehicle_reason(donation, v) is None]
    if not ok_vehicle:
        biggest = max(v.vehicle_capacity for v in volunteers.values())
        return prefix + (f"no volunteer had a vehicle that can carry {donation.quantity} units "
                         f"(largest vehicle holds {biggest}).")

    # Everything above passed on its own, so a combination or timing rule blocked it.
    # A set comprehension collects each distinct reason once; sorted() makes the order stable.
    reasons = {check_pair(donation, r, v, tracker, rules) for r in ok_cap for v in ok_vehicle}
    return prefix + "; ".join(sorted(reasons)) + "."
