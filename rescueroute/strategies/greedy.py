"""
Greedy Strategy for RescueRoute

The greedy rule is:
    1. Soonest expiring
    2. Fewest compatible recipients
    3. Largest payload
    4. Earliest arrival order

Deferral explanations follow docs/project_logic/002.
AI-assisted (deferral wording and jumper search): Claude Code (claude-opus-5-5), requested by AidanKDao, see docs/TOOLS_AND_SOURCES.md
"""

from rescueroute.models import Assignment, Status
from rescueroute.feasibility import (
    Rules,
    CapacityTracker,
    find_match,
    assigned_reason,
    unassigned_reason,
)

def deferral_reason(jumper, deferred, counts):
    """Explain why the deferred donation was considered after the 'jumper' donation under the greedy rule.

    Only levels 1-3 of the greedy rule can decide this. The jumper arrived AFTER the deferred
    donation, so if the two tied on levels 1-3, level 4 (earlier arrival) would have put the
    deferred donation first and there would be no jump to explain.
    """
    start = f"Donation {deferred.donation_id} was considered after {jumper.donation_id} because "
    jumper_count = counts[jumper.donation_id]
    deferred_count = counts[deferred.donation_id]

    # 1. Soonest expiring
    if jumper.expiry_time < deferred.expiry_time:
        return start + (f"{jumper.donation_id} expires sooner "
                        f"(minute {jumper.expiry_time} vs {deferred.expiry_time}).")

    # 2. Fewest compatible recipients (both expire at the same minute)
    if jumper_count < deferred_count:
        return start + (f"both expire at minute {deferred.expiry_time} and {jumper.donation_id} "
                        f"has fewer compatible recipients ({jumper_count} vs {deferred_count}).")

    # 3. Larger quantity. This is the only level left (see the docstring above).
    return start + (f"both expire at minute {deferred.expiry_time} with {deferred_count} compatible "
                    f"recipient(s) each, and {jumper.donation_id} is larger "
                    f"({jumper.quantity} vs {deferred.quantity} units).")

def run_greedy(donations, recipients, volunteers):
    """
    Run the Greedy scheduler.

    returns list[Assignment]: One Assignment object for every donation
    """

    # Create the shared rule settings.
    rules = Rules()

    # Create a tracker for values that change while scheduling.
    tracker = CapacityTracker(recipients, volunteers)

    # This list will hold the final result for every donation.
    assignments = []

    # Calculate the number of compatible recipients for each donation.
    # We need this to sort donations by the greedy criteria. (part 2 of the greedy rule)
    compatible_recipients_count = {}
    for donation in donations.values():
        count = 0
        for recipient in recipients.values():
            if donation.food_type not in recipient.accepted_food_types:
                continue
            if recipient.capacity < donation.quantity:
                continue
            count += 1
        compatible_recipients_count[donation.donation_id] = count

    # Define the sorting key for donations based on the greedy criteria.
    def donation_sort_key(donation):
        return (
            donation.expiry_time,
            compatible_recipients_count[donation.donation_id],
            -donation.quantity,
            donation.arrival_order
        )

    # Sort donations by the greedy criteria.
    ordered_donations = sorted(
        donations.values(),
        key=donation_sort_key
    )

    # Process each donation one at a time in Greedy order.
    # TODO consider refactoring to avoid code duplication.
    for donation in ordered_donations:

        # Find the first recipient + volunteer combination that can handle this donation.
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
        # resources already used by earlier Greedy assignments.
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

    # Find all deferred donations
    for i, deferred_candidate in enumerate(assignments):
        # A deferred donation will not have an assigned status
        if deferred_candidate.status != Status.UNASSIGNED:
            continue

        # A donation with no compatible recipients is not deferred, it is unassignable
        if compatible_recipients_count[deferred_candidate.donation_id] == 0:
            continue

        # Find the donation that caused the deferral
        for jumper_candidate in reversed(assignments[:i]):
            # Skip donations with zero compatible recipients: they could never be assigned,
            # so naming them as the reason would be misleading (docs/project_logic/002)
            if compatible_recipients_count[jumper_candidate.donation_id] == 0:
                continue

            # The jumper must have a later arrival order to defer the deferred candidate
            if donations[jumper_candidate.donation_id].arrival_order < donations[deferred_candidate.donation_id].arrival_order:
                continue

            # Confirm the deferred and jumper
            jumper = donations[jumper_candidate.donation_id]
            deferred = donations[deferred_candidate.donation_id]

            # Assign a reason for the deferral based on the greedy rule
            reason_suffix = deferral_reason(jumper, deferred, counts=compatible_recipients_count)
            deferred_candidate.decision_reason += " " + reason_suffix

            # Once we find the first donation that caused the deferral, we can stop looking for more
            break


    # Return one Assignment object for every donation we processed.
    return assignments
