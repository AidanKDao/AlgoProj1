"""
Base data model for RescueRoute.

Times are stored as integer minutes since the start of the simulation
(e.g. ready_time=30 means 30 minutes after start of the simulation).
"""

from dataclasses import dataclass
from enum import Enum

class Status(Enum):
    ASSIGNED = "assigned"
    UNASSIGNED = "unassigned"
    DEFERRED = "deferred"

@dataclass
class Donation:
    donation_id: str
    donor_name: str
    food_type: str
    quantity: int          # units of food
    ready_time: int        # minute the donation can be picked up
    expiry_time: int       # minute the food is not safe for consumption
    pickup_area: str
    arrival_order: int     # order in which the donation is reported

@dataclass
class Recipient:
    recipient_id: str
    organization_name: str
    accepted_food_types: set[str]
    capacity: int          # maximum amount of food the recipient can accept
    closing_time: int      # minute the recipient is no longer accepting donations
    dropoff_area: str

@dataclass
class Volunteer:
    volunteer_id: str
    vehicle_capacity: int     # maximum amount of food the volunteer can transport
    maximum_pickups: int      # maximum number of donations the volunteer can pick up
    availability_start: int   # minute the volunteer is available
    availability_end: int     # minute the volunteer is no longer available
    pickup_area: str
    
@dataclass
class Assignment:
    donation_id: str
    recipient_id: str
    volunteer_id: str
    scheduled_time_start: int       # minute the assignment is scheduled to start
    scheduled_time_end: int         # minute the assignment is scheduled to end
    decision_reason: str
    status: Status