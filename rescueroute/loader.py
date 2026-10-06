"""
Loading and validation of donations, recipients, and volunteers from CSV or JSON.

AI-assisted: Claude Code (claude-sonnet-5-5), requested by Kaleb Robles, see docs/TOOLS_AND_SOURCES.md

Each load_* function returns (records, errors):
    records: dict keyed by ID. Records that fail validation are left out.
    errors:  list of human-readable messages naming the row, ID, field, and reason.
Nothing here raises on bad data; a missing or unreadable file is reported as an error.
When an ID is repeated, the first record is kept and the later ones are reported.
"""

import csv
import json
from pathlib import Path

from rescueroute.models import Donation, Recipient, Volunteer

FOOD_TYPES = {"prepared_meals", "produce", "bakery", "dairy", "frozen", "canned_goods"}
AREAS = {"north", "south", "east", "west", "central"}


# ---------- reading files ----------

def _read_rows(path, kind: str) -> tuple[list[dict], list[str]]:
    """Read a .csv or .json file into a list of row dicts. Returns (rows, errors)."""
    path = Path(path)
    try:
        if path.suffix.lower() == ".json":
            with open(path, encoding="utf-8") as f:
                rows = json.load(f)
            if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
                return [], [f"{kind} file {path.name}: JSON must be a list of objects"]
            return rows, []
        if path.suffix.lower() == ".csv":
            with open(path, newline="", encoding="utf-8") as f:
                return list(csv.DictReader(f)), []
        return [], [f"{kind} file {path.name}: unsupported file type (use .csv or .json)"]
    except FileNotFoundError:
        return [], [f"{kind} file {path.name}: file not found"]
    except (OSError, ValueError) as e:  # ValueError covers bad JSON and bad encoding
        return [], [f"{kind} file {path.name}: could not be read ({e})"]


# ---------- field checks: each returns (value, error_message_or_None) ----------

def _text(row: dict, field: str):
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        return None, "is missing or empty"
    return value.strip(), None


def _integer(row: dict, field: str, minimum: int):
    value = row.get(field)
    if isinstance(value, bool) or value is None or (isinstance(value, str) and not value.strip()):
        return None, "is missing or empty"
    try:
        number = int(value.strip()) if isinstance(value, str) else int(value)
        if isinstance(value, float) and value != number:
            raise ValueError
    except ValueError:
        return None, f"must be a whole number, got {value!r}"
    if number < minimum:
        return None, f"must be at least {minimum}, got {number}"
    return number, None


def _choice(row: dict, field: str, allowed: set[str]):
    value, error = _text(row, field)
    if error:
        return None, error
    if value not in allowed:
        return None, f"{value!r} is not one of: {', '.join(sorted(allowed))}"
    return value, None


def _food_type_set(row: dict, field: str):
    """CSV gives 'dairy;produce'; JSON gives a list. Both become a set of known food types."""
    value = row.get(field)
    if isinstance(value, str):
        items = [item.strip() for item in value.split(";") if item.strip()]
    elif isinstance(value, list):
        items = [str(item).strip() for item in value]
    else:
        return None, "is missing or empty"
    if not items:
        return None, "is missing or empty"
    unknown = sorted(set(items) - FOOD_TYPES)
    if unknown:
        return None, f"has unknown food type(s): {', '.join(unknown)}"
    return set(items), None


def _check(fields: dict, errors: list[str], name: str, result: tuple) -> None:
    """Store a field result, or add its error message to errors."""
    value, error = result
    if error:
        errors.append(f"field '{name}' {error}")
    else:
        fields[name] = value


def _load(path, kind: str, id_field: str, validate_row) -> tuple[dict, list[str]]:
    """Shared loop: read rows, reject duplicate IDs, validate fields, build records."""
    rows, errors = _read_rows(path, kind)
    records = {}
    seen_ids = set()                      # every ID seen so far, for duplicate detection
    for order, row in enumerate(rows):    # order = row position, used as arrival_order
        label = f"{kind} row {order + 1}"
        record_id = str(row.get(id_field) or "").strip()
        if not record_id:
            errors.append(f"{label}: field '{id_field}' is missing or empty")
            continue
        label += f" ({record_id})"
        if record_id in seen_ids:
            errors.append(f"{label}: duplicate {id_field}, record ignored (first one kept)")
            continue
        seen_ids.add(record_id)

        problems = []
        record = validate_row(row, record_id, order, problems)
        if problems:
            errors.extend(f"{label}: {p}" for p in problems)
        else:
            records[record_id] = record
    return records, errors


# ---------- the three entity types ----------

def _validate_donation(row, donation_id, order, problems):
    f = {}
    _check(f, problems, "donor_name", _text(row, "donor_name"))
    _check(f, problems, "food_type", _choice(row, "food_type", FOOD_TYPES))
    _check(f, problems, "quantity", _integer(row, "quantity", 1))
    _check(f, problems, "ready_time", _integer(row, "ready_time", 0))
    _check(f, problems, "expiry_time", _integer(row, "expiry_time", 0))
    _check(f, problems, "pickup_area", _choice(row, "pickup_area", AREAS))
    # expiry == ready is allowed (an already-expired donation the strategies must reject);
    # expiry before ready is a data error.
    if "ready_time" in f and "expiry_time" in f and f["expiry_time"] < f["ready_time"]:
        problems.append(f"field 'expiry_time' ({f['expiry_time']}) is before ready_time ({f['ready_time']})")
    if problems:
        return None
    return Donation(donation_id=donation_id, arrival_order=order, **f)


def _validate_recipient(row, recipient_id, order, problems):
    f = {}
    _check(f, problems, "organization_name", _text(row, "organization_name"))
    _check(f, problems, "accepted_food_types", _food_type_set(row, "accepted_food_types"))
    _check(f, problems, "capacity", _integer(row, "capacity", 1))
    _check(f, problems, "closing_time", _integer(row, "closing_time", 0))
    _check(f, problems, "dropoff_area", _choice(row, "dropoff_area", AREAS))
    if problems:
        return None
    return Recipient(recipient_id=recipient_id, **f)


def _validate_volunteer(row, volunteer_id, order, problems):
    f = {}
    _check(f, problems, "vehicle_capacity", _integer(row, "vehicle_capacity", 1))
    _check(f, problems, "maximum_pickups", _integer(row, "maximum_pickups", 1))
    _check(f, problems, "availability_start", _integer(row, "availability_start", 0))
    _check(f, problems, "availability_end", _integer(row, "availability_end", 0))
    _check(f, problems, "pickup_area", _choice(row, "pickup_area", AREAS))
    if "availability_start" in f and "availability_end" in f and f["availability_end"] <= f["availability_start"]:
        problems.append(f"field 'availability_end' ({f['availability_end']}) must be after "
                        f"availability_start ({f['availability_start']})")
    if problems:
        return None
    return Volunteer(volunteer_id=volunteer_id, **f)


def load_donations(path) -> tuple[dict[str, Donation], list[str]]:
    return _load(path, "donations", "donation_id", _validate_donation)


def load_recipients(path) -> tuple[dict[str, Recipient], list[str]]:
    return _load(path, "recipients", "recipient_id", _validate_recipient)


def load_volunteers(path) -> tuple[dict[str, Volunteer], list[str]]:
    return _load(path, "volunteers", "volunteer_id", _validate_volunteer)
