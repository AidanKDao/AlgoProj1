
"""Performance metrics for the RescueRoute scheduling strategies.

This module measures how well FIFO and Greedy perform.
Both strategies use the same calculations for a fair comparison.
"""

from rescueroute.models import Status


def calculate_metrics(donations, assignments):
    """
    Calculate performance metrics for one scheduling strategy.

    Args:
        donations: Dictionary of Donation objects, keyed by donation ID.
        assignments: List of Assignment objects returned by the strategy.

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

    # Return the results so FIFO and Greedy can be compared.
    return {
        "total_donations": total_donations,
        "assigned": assigned_count,
        "unassigned": unassigned_count,
        "total_food": total_food,
        "rescued_food": rescued_food,
        "assignment_rate": round(assignment_rate, 2),
        "food_rescue_rate": round(food_rescue_rate, 2),
    }
