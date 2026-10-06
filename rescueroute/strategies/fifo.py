"""
FIFO (First-In, First-Out) strategy for distributing donations.
"""

from rescueroute.feasibility import CapacityTracker, Rules, find_match, assigned_reason, unassigned_reason
from rescueroute.models import Assignment, Status

def run_fifo(donations, recipients, volunteers):
    """FIFO strategy for distribution of donations with one assignment per donation."""
    tracker = CapacityTracker(recipients, volunteers)
    rules = Rules()
    history = []

    # Implementation for FIFO strategy
    for donation in sorted(donations.values(), key=lambda x: x.arrival_order):
        # Process each donation in the order they were received
        match = find_match(donation, recipients, volunteers, tracker, rules)
        if not match:
            # If no match is found, the donation remains unassigned
            history.append(
                Assignment(
                    donation_id=donation.donation_id,
                    recipient_id=None,
                    volunteer_id=None,
                    scheduled_time_start=None,
                    scheduled_time_end=None,
                    decision_reason=unassigned_reason(donation, recipients, volunteers, tracker, rules),
                    status=Status.UNASSIGNED,
                )
            )
            continue

        recipient, volunteer, start, arrival = match
        tracker.record(donation, recipient.recipient_id, volunteer.volunteer_id)

        # Create an assignment for the donation
        assignment = Assignment(
            donation_id=donation.donation_id,
            recipient_id=recipient.recipient_id,
            volunteer_id=volunteer.volunteer_id,
            scheduled_time_start=start,
            scheduled_time_end=arrival,
            decision_reason=assigned_reason(donation, recipient, volunteer, rules, start, arrival),
            status=Status.ASSIGNED,
        )

        history.append(assignment)
    return history

