
"""Performance metrics for the RescueRoute scheduling strategies.

This module measures how well FIFO and Greedy perform.
Both strategies use the same calculations for a fair comparison.

AI-assisted: Claude Code, requested by AidanKDao (urgent rescue rate, utilization
and food at risk), see docs/TOOLS_AND_SOURCES.md
"""

import math

from rescueroute.models import Status

# Urgent donations are the earliest-expiring 25% (docs/project_logic/002).
URGENT_FRACTION = 0.25


def calculate_metrics(donations, assignments, recipients, volunteers):
    """
    Calculate performance metrics for one scheduling strategy.

    Args:
        donations: Dictionary of Donation objects, keyed by donation ID.
        assignments: List of Assignment objects returned by the strategy.
        recipients: Dictionary of Recipient objects, keyed by recipient ID.
        volunteers: Dictionary of Volunteer objects, keyed by volunteer ID.

    Returns:
        Dictionary containing the performance results.
    """

    # Count how many donations were provided.
    total_donations = len(donations)

    # Count the total amount of food available.
    total_food = sum(
        donation.quantity for donation in donations.values()
    )

    # Identify all successfully assigned donations.
    assigned_ids = {
        assignment.donation_id
        for assignment in assignments
        if assignment.status == Status.ASSIGNED
        and assignment.donation_id in donations
    }

    # Count successful and unsuccessful donations.
    assigned_count = len(assigned_ids)
    unassigned_count = total_donations - assigned_count

    # Calculate the amount of food successfully rescued.
    rescued_food = sum(
        donations[donation_id].quantity
        for donation_id in assigned_ids
    )

    # Calculate the percentage of donations assigned.
    # Avoid dividing by zero if no donations exist.
    assignment_rate = (
        assigned_count / total_donations * 100
        if total_donations > 0 else 0.0
    )

    # Calculate what percentage of available food was rescued.
    food_rescue_rate = (
        rescued_food / total_food * 100
        if total_food > 0 else 0.0
    )

    # Food at risk is everything that was not assigned. Expired donations
    # are unassigned, so they are counted here once.
    food_at_risk = total_food - rescued_food

    # Urgent donations are the earliest-expiring 25%, rounded up so a small
    # dataset still has at least one. Ties on expiry go to arrival order.
    urgent_count = math.ceil(total_donations * URGENT_FRACTION)
    by_urgency = sorted(
        donations.values(),
        key=lambda donation: (donation.expiry_time, donation.arrival_order),
    )
    urgent_ids = {donation.donation_id for donation in by_urgency[:urgent_count]}
    urgent_assigned = len(urgent_ids & assigned_ids)

    # Urgent rescue rate: what share of the urgent donations were assigned.
    urgent_rescue_rate = (
        urgent_assigned / urgent_count * 100
        if urgent_count > 0 else 0.0
    )

    # Recipient utilization: assigned quantity / capacity of ALL recipients.
    recipient_capacity = sum(
        recipient.capacity for recipient in recipients.values()
    )
    recipient_utilization = (
        rescued_food / recipient_capacity * 100
        if recipient_capacity > 0 else 0.0
    )

    # Volunteer utilization: assigned quantity / what every volunteer could
    # carry in total (vehicle capacity times maximum pickups).
    volunteer_capacity = sum(
        volunteer.vehicle_capacity * volunteer.maximum_pickups
        for volunteer in volunteers.values()
    )
    volunteer_utilization = (
        rescued_food / volunteer_capacity * 100
        if volunteer_capacity > 0 else 0.0
    )

    # Return the results so FIFO and Greedy can be compared.
    return {
        "total_donations": total_donations,
        "assigned": assigned_count,
        "unassigned": unassigned_count,
        "total_food": total_food,
        "rescued_food": rescued_food,
        "assignment_rate": round(assignment_rate, 2),
        "food_rescue_rate": round(food_rescue_rate, 2),
        "food_at_risk": food_at_risk,
        "urgent_donations": urgent_count,
        "urgent_assigned": urgent_assigned,
        "urgent_rescue_rate": round(urgent_rescue_rate, 2),
        "recipient_utilization": round(recipient_utilization, 2),
        "volunteer_utilization": round(volunteer_utilization, 2),
    }
