"""
Shared feasibility rules and capacity tracking for both scheduling strategies.

AI-assisted: Claude Code (claude-sonnet-5-5), requested by Kaleb Robles, see docs/TOOLS_AND_SOURCES.md

FIFO and greedy must call the same code here so they differ only in processing order.
Rules that the team has not settled yet (docs/project_logic/, AGENTS.md "Open decisions")
live in the Rules dataclass and are OFF by default:
    require_area_match, enforce_maximum_pickups, enforce_volunteer_window,
    travel_minutes / min_minutes_left (proposal 001 suggests 30 and 15).
Settled checks that always run: food type, recipient capacity, vehicle capacity,
donation not expired on arrival, recipient still open on arrival.
"""

from dataclasses import dataclass

from rescueroute.models import Donation, Recipient, Volunteer


@dataclass
class Rules:
    travel_minutes: int = 0               # minutes from pickup to delivery
    min_minutes_left: int = 1             # food must arrive at least this long before expiry
    require_area_match: bool = False      # donation pickup area == volunteer area == recipient area
    enforce_maximum_pickups: bool = False
    enforce_volunteer_window: bool = False


class CapacityTracker:
    """Remaining capacity for one run. Built fresh from the inputs, which are never changed."""

    def __init__(self, recipients: dict[str, Recipient], volunteers: dict[str, Volunteer]):
        self.recipient_remaining = {rid: r.capacity for rid, r in recipients.items()}
        self.volunteer_pickups = {vid: 0 for vid in volunteers}
        self.volunteer_quantity = {vid: 0 for vid in volunteers}

    def record(self, donation: Donation, recipient_id: str, volunteer_id: str) -> None:
        self.recipient_remaining[recipient_id] -= donation.quantity
        self.volunteer_pickups[volunteer_id] += 1
        self.volunteer_quantity[volunteer_id] += donation.quantity


def schedule(donation: Donation, volunteer: Volunteer, rules: Rules) -> tuple[int, int]:
    """Return (pickup start, delivery arrival) in minutes."""
    start = donation.ready_time
    if rules.enforce_volunteer_window:
        start = max(start, volunteer.availability_start)
    return start, start + rules.travel_minutes


# ---------- individual checks: each returns None if OK, else a reason ----------

def _expired_reason(donation: Donation, arrival: int, rules: Rules) -> str | None:
    if arrival + rules.min_minutes_left > donation.expiry_time:
        if donation.expiry_time <= donation.ready_time:
            return (f"it was already expired when it became ready for pickup "
                    f"(ready at minute {donation.ready_time}, expires at minute {donation.expiry_time})")
        return (f"it expires at minute {donation.expiry_time}, but the earliest delivery is "
                f"minute {arrival} and it needs at least {rules.min_minutes_left} minute(s) of shelf life left on arrival")
    return None


def _food_reason(donation: Donation, recipient: Recipient) -> str | None:
    if donation.food_type not in recipient.accepted_food_types:
        return f"{recipient.organization_name} does not accept {donation.food_type}"
    return None


def _recipient_capacity_reason(donation, recipient, tracker) -> str | None:
    remaining = tracker.recipient_remaining[recipient.recipient_id]
    if donation.quantity > remaining:
        return (f"{recipient.organization_name} has only {remaining} units of capacity left "
                f"for {donation.quantity}")
    return None


def _vehicle_reason(donation: Donation, volunteer: Volunteer) -> str | None:
    if donation.quantity > volunteer.vehicle_capacity:
        return (f"volunteer {volunteer.volunteer_id}'s vehicle holds {volunteer.vehicle_capacity} units, "
                f"less than {donation.quantity}")
    return None


def _area_reason(donation, recipient, volunteer, rules) -> str | None:
    if rules.require_area_match and not (
            donation.pickup_area == volunteer.pickup_area == recipient.dropoff_area):
        return (f"areas do not match (donation in {donation.pickup_area}, volunteer "
                f"{volunteer.volunteer_id} in {volunteer.pickup_area}, "
                f"{recipient.organization_name} in {recipient.dropoff_area})")
    return None


def _pickups_reason(volunteer, tracker, rules) -> str | None:
    if rules.enforce_maximum_pickups and \
            tracker.volunteer_pickups[volunteer.volunteer_id] >= volunteer.maximum_pickups:
        return (f"volunteer {volunteer.volunteer_id} already has the maximum "
                f"{volunteer.maximum_pickups} pickup(s)")
    return None


def _closing_and_window_reason(recipient, volunteer, arrival, rules) -> str | None:
    if arrival > recipient.closing_time:
        return f"{recipient.organization_name} closes at minute {recipient.closing_time}, before arrival at minute {arrival}"
    if rules.enforce_volunteer_window and arrival > volunteer.availability_end:
        return (f"volunteer {volunteer.volunteer_id} is only available until minute "
                f"{volunteer.availability_end}, before arrival at minute {arrival}")
    return None


def check_pair(donation, recipient, volunteer, tracker, rules) -> str | None:
    """None if this donation-recipient-volunteer match is feasible, else why not."""
    _, arrival = schedule(donation, volunteer, rules)
    return (_expired_reason(donation, arrival, rules)
            or _food_reason(donation, recipient)
            or _recipient_capacity_reason(donation, recipient, tracker)
            or _vehicle_reason(donation, volunteer)
            or _area_reason(donation, recipient, volunteer, rules)
            or _pickups_reason(volunteer, tracker, rules)
            or _closing_and_window_reason(recipient, volunteer, arrival, rules))


# ---------- finding a match and explaining ----------

def find_match(donation, recipients, volunteers, tracker, rules):
    """First feasible (recipient, volunteer, start, arrival), in dict (input) order, or None."""
    for recipient in recipients.values():
        for volunteer in volunteers.values():
            if check_pair(donation, recipient, volunteer, tracker, rules) is None:
                start, arrival = schedule(donation, volunteer, rules)
                return recipient, volunteer, start, arrival
    return None


def assigned_reason(donation, recipient, volunteer, rules, start: int, arrival: int) -> str:
    return (f"Donation {donation.donation_id} was assigned to {recipient.organization_name} with volunteer "
            f"{volunteer.volunteer_id} because it expires in {donation.expiry_time - start} minutes "
            f"(at minute {donation.expiry_time}) and arrives at minute {arrival}, "
            f"{recipient.organization_name} accepts {donation.food_type}, capacity is available "
            f"({donation.quantity} units), and the volunteer's vehicle can carry the quantity.")


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

    # Narrow the recipients and volunteers one requirement at a time.
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
    reasons = {check_pair(donation, r, v, tracker, rules) for r in ok_cap for v in ok_vehicle}
    return prefix + "; ".join(sorted(reasons)) + "."
