# FIFO baseline strategy for RescueRoute.
#
# FIFO means "first in, first out":
# donations are processed in the order they were reported.
#
# This file does NOT repeat all of the matching rules.
# Instead, it uses the shared feasibility.py functions so FIFO and
# the greedy strategy follow the same compatibility rules.

from rescueroute.models import Assignment, Status

# Import the shared matching logic.
# Rules controls which feasibility rules are enabled.
# CapacityTracker remembers remaining recipient capacity
# and how many pickups each volunteer has already completed.
from rescueroute.feasibility import (
    Rules,
    CapacityTracker,
    find_match,
    assigned_reason,
    unassigned_reason,
)


def run_fifo(donations, recipients, volunteers):
    """
    Run the FIFO baseline scheduler.

    Donations are processed by arrival_order, meaning the donation
    reported first gets considered first.

    For each donation:
        1. Try to find the first feasible recipient + volunteer pair.
        2. If a match exists, create an ASSIGNED Assignment.
        3. If no match exists, create an UNASSIGNED Assignment.

    Returns:
        list[Assignment]: exactly one Assignment for every donation.
    """

    # Create the shared rule settings.
    # Rules() uses the default rules defined in feasibility.py.
    rules = Rules()

    # Create a tracker for values that change while scheduling.
    #
    # For example:
    # - how much recipient capacity is still available
    # - how many pickups a volunteer has already completed
    #
    # The original Recipient and Volunteer objects are not modified.
    tracker = CapacityTracker(recipients, volunteers)

    # This list will hold the final result for every donation.
    assignments = []

    # Sort donations by arrival_order.
    #
    # donations is a dictionary, so donations.values() gives us
    # the actual Donation objects.
    #
    # The lambda tells sorted() to use arrival_order as the value
    # that determines which donation comes first.
    ordered_donations = sorted(
        donations.values(),
        key=lambda donation: donation.arrival_order
    )

    # Process each donation one at a time in FIFO order.
    for donation in ordered_donations:

        # Ask the shared feasibility logic to find the first
        # recipient + volunteer combination that can handle this donation.
        #
        # If successful, find_match returns:
        # (recipient, volunteer, start_time, arrival_time)
        #
        # If nothing works, it returns None.
        match = find_match(
            donation,
            recipients,
            volunteers,
            tracker,
            rules
        )

        # If no valid recipient-volunteer combination exists,
        # the donation must still receive an Assignment object.
        if match is None:

            assignments.append(
                Assignment(
                    donation_id=donation.donation_id,

                    # No recipient or volunteer was selected.
                    recipient_id=None,
                    volunteer_id=None,

                    # Since no delivery happens, use the donation's
                    # ready time for both scheduling fields.
                    scheduled_time_start=donation.ready_time,
                    scheduled_time_end=donation.ready_time,

                    # Build a human-readable explanation such as:
                    # no compatible food type, insufficient capacity,
                    # expired donation, etc.
                    decision_reason=unassigned_reason(
                        donation,
                        recipients,
                        volunteers,
                        tracker,
                        rules
                    ),

                    status=Status.UNASSIGNED,
                )
            )

            # Skip the rest of this loop and move to the next donation.
            continue

        # If we get here, a valid match was found.
        #
        # "Unpacking" takes the 4 values returned by find_match()
        # and stores each one in its own variable.
        recipient, volunteer, start, arrival = match

        # Record the successful assignment.
        #
        # This reduces the recipient's remaining capacity and
        # increases the volunteer's pickup/quantity totals.
        #
        # This is important because later donations must respect
        # resources already used by earlier FIFO assignments.
        tracker.record(
            donation,
            recipient.recipient_id,
            volunteer.volunteer_id
        )

        # Create the successful Assignment result.
        assignments.append(
            Assignment(
                donation_id=donation.donation_id,
                recipient_id=recipient.recipient_id,
                volunteer_id=volunteer.volunteer_id,

                # start = when pickup begins
                # arrival = when the donation reaches the recipient
                scheduled_time_start=start,
                scheduled_time_end=arrival,

                # Build a readable explanation of why the assignment worked.
                decision_reason=assigned_reason(
                    donation,
                    recipient,
                    volunteer,
                    rules,
                    start,
                    arrival
                ),

                status=Status.ASSIGNED,
            )
        )

    # Return one Assignment object for every donation we processed.
    return assignments
