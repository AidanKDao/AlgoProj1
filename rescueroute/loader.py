"""
Loading and validation of donations, recipients, and volunteers from CSV or JSON.

AI-assisted: Claude Code (claude-sonnet-5-5), requested by Kaleb Robles, see docs/TOOLS_AND_SOURCES.md

Each load_* function returns (records, errors):
    records: dict keyed by ID. Records that fail validation are left out.
    errors:  list of human-readable messages naming the row, ID, field, and reason.
Nothing here raises on bad data; a missing or unreadable file is reported as an error.
When an ID is repeated, the first record is kept and the later ones are reported.

How the file is organized (top to bottom):
    1. _read_rows           open a .csv or .json file and give back a list of row dicts
    2. field checks         small functions that check ONE field and return (value, error)
    3. _check / _load       glue code and the shared loop that processes every row
    4. _validate_*          one function per entity type (donation, recipient, volunteer)
    5. load_*               the three public functions that the rest of the project calls
"""

import csv
import json
from pathlib import Path

from rescueroute.models import Donation, Recipient, Volunteer

# Allowed values. Sets are used because "is this value in here?" is fast and reads naturally.
FOOD_TYPES = {"prepared_meals", "produce", "bakery", "dairy", "frozen", "canned_goods"}
AREAS = {"north", "south", "east", "west", "central"}


# ---------- reading files ----------

def _read_rows(path, kind: str) -> tuple[list[dict], list[str]]:
    """Read a .csv or .json file into a list of row dicts. Returns (rows, errors).

    Both formats end up in the same shape: one dict per record, keyed by column name.
    `kind` says which file this is ("donations", "recipients" or "volunteers"), not a food
    type. It is only used to label error messages. The return value is a tuple (a fixed pair):
    the rows first, then the list of errors.
    """
    path = Path(path)   # Path gives us .suffix (the extension) and .name (the file name)
    try:
        if path.suffix.lower() == ".json":
            with open(path, encoding="utf-8") as f:   # "with" closes the file for us
                rows = json.load(f)
            # The JSON must be a list of objects, e.g. [{"donation_id": "D-1", ...}, ...]
            if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
                return [], [f"{kind} file {path.name}: JSON must be a list of objects"]
            return rows, []
        if path.suffix.lower() == ".csv":
            with open(path, newline="", encoding="utf-8") as f:
                # DictReader turns each CSV line into a dict using the header row as keys.
                # Every value is a string; the field checks below convert numbers later.
                return list(csv.DictReader(f)), []
        return [], [f"{kind} file {path.name}: unsupported file type (use .csv or .json)"]
    except FileNotFoundError:
        return [], [f"{kind} file {path.name}: file not found"]
    except (OSError, ValueError) as e:  # ValueError covers bad JSON and bad encoding
        return [], [f"{kind} file {path.name}: could not be read ({e})"]


# ---------- field checks: each returns (value, error_message_or_None) ----------
# Pattern: if the field is fine, return (the_value, None).
#          if not, return (None, "reason it is bad"). Exactly one of the two is None.

def _text(row: dict, field: str):
    """A non-empty text field, such as donor_name."""
    value = row.get(field)   # .get returns None instead of crashing when the key is missing
    if not isinstance(value, str) or not value.strip():
        return None, "is missing or empty"
    return value.strip(), None


def _integer(row: dict, field: str, minimum: int):
    """A whole number that is at least `minimum` (quantity >= 1, times >= 0, etc.)."""
    value = row.get(field)
    # bool is rejected on purpose: Python treats True as 1, which would sneak through.
    if isinstance(value, bool) or value is None or (isinstance(value, str) and not value.strip()):
        return None, "is missing or empty"
    try:
        # CSV gives strings ("30"); JSON gives real numbers (30). Handle both.
        number = int(value.strip()) if isinstance(value, str) else int(value)
        if isinstance(value, float) and value != number:   # 5.5 must not quietly become 5
            raise ValueError
    except ValueError:    # int("abc") lands here
        return None, f"must be a whole number, got {value!r}"
    if number < minimum:
        return None, f"must be at least {minimum}, got {number}"
    return number, None


def _choice(row: dict, field: str, allowed: set[str]):
    """A text field whose value must be one of `allowed` (food type, area)."""
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
        # "dairy;produce" -> ["dairy", "produce"], dropping any blank pieces
        items = [item.strip() for item in value.split(";") if item.strip()]
    elif isinstance(value, list):
        items = [str(item).strip() for item in value]
    else:
        return None, "is missing or empty"
    if not items:
        return None, "is missing or empty"
    unknown = sorted(set(items) - FOOD_TYPES)   # set subtraction: what is NOT a known type
    if unknown:
        return None, f"has unknown food type(s): {', '.join(unknown)}"
    return set(items), None


def _check(fields: dict, errors: list[str], name: str, result: tuple) -> None:
    """Store a field result, or add its error message to errors.

    This saves repeating the same four lines for every field. Because it only ever
    adds to `errors` (it never stops early), one bad record reports ALL its problems.
    """
    value, error = result    # unpack the (value, error) pair: first item to value, second to error
    if error:
        errors.append(f"field '{name}' {error}")
    else:
        fields[name] = value


# ---------- the shared loop ----------

def _load(path, kind: str, id_field: str, validate_row) -> tuple[dict, list[str]]:
    """Shared loop: read rows, reject duplicate IDs, validate fields, build records.

    `validate_row` is a function handed in by the caller (one per entity type), so this
    one loop works for donations, recipients, and volunteers alike.
    `id_field` is the name of the ID column, e.g. "donation_id".

    Returns a tuple: (records, errors). `records` is a dict, which stores values under keys
    so we can look one up directly, e.g. records["D-1001"] gives that donation.
    """
    rows, errors = _read_rows(path, kind)
    records = {}                          # the valid records, keyed by ID
    seen_ids = set()                      # every ID seen so far, for duplicate detection
    for order, row in enumerate(rows):    # order = row position, used as arrival_order
        label = f"{kind} row {order + 1}"   # +1 so humans see "row 1", not "row 0"
        # .strip() removes spaces at both ends, so " D-1 " and "D-1" count as the same ID
        record_id = str(row.get(id_field) or "").strip()
        # Check 1: the ID is blank or missing. Record an error and skip to the next row.
        if not record_id:
            errors.append(f"{label}: field '{id_field}' is missing or empty")
            continue                      # skip this row, move on to the next
        label += f" ({record_id})"
        # Check 2: the ID was already seen, so this row is a duplicate. First one is kept.
        if record_id in seen_ids:
            errors.append(f"{label}: duplicate {id_field}, record ignored (first one kept)")
            continue
        seen_ids.add(record_id)

        # Start an empty list for THIS row. The validator adds one message per bad field,
        # so every problem in the row is collected instead of stopping at the first one.
        problems = []
        record = validate_row(row, record_id, order, problems)
        if problems:
            # Put the row label in front of each message, then add them all to the main list
            errors.extend(f"{label}: {p}" for p in problems)
        else:
            records[record_id] = record   # no problems: keep the record under its ID
    return records, errors


# ---------- the three entity types ----------
# Each one: run a field check for every column, then do checks that compare two fields.
# `f` collects the valid values; the dataclass is only built if there were no problems.

def _validate_donation(row, donation_id, order, problems):
    f = {}
    _check(f, problems, "donor_name", _text(row, "donor_name"))
    _check(f, problems, "food_type", _choice(row, "food_type", FOOD_TYPES))
    _check(f, problems, "quantity", _integer(row, "quantity", 1))
    _check(f, problems, "ready_time", _integer(row, "ready_time", 0))
    _check(f, problems, "expiry_time", _integer(row, "expiry_time", 0))
    _check(f, problems, "pickup_area", _choice(row, "pickup_area", AREAS))
    # expiry == ready is allowed (an already-expired donation the strategies must reject);
    # expiry before ready is a data error. Only compared if both times were valid numbers.
    if "ready_time" in f and "expiry_time" in f and f["expiry_time"] < f["ready_time"]:
        problems.append(f"field 'expiry_time' ({f['expiry_time']}) is before ready_time ({f['ready_time']})")
    if problems:
        return None
    # **f unpacks the dict into keyword arguments: {"quantity": 30} becomes quantity=30
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


# ---------- public functions: the only ones other files should call ----------
# Each one hands the work to _load with four things:
#   1. path               which file to read
#   2. "donations"        the kind, used to label error messages
#   3. "donation_id"      the name of the ID column
#   4. _validate_donation the function that checks each row's fields. There are no
#                         parentheses after it: we pass the function itself and _load
#                         calls it once per row.
# The -> part is a type hint (a label, not enforced): it returns a tuple of
# (dict of records keyed by ID, list of error message strings).

def load_donations(path) -> tuple[dict[str, Donation], list[str]]:
    return _load(path, "donations", "donation_id", _validate_donation)


def load_recipients(path) -> tuple[dict[str, Recipient], list[str]]:
    return _load(path, "recipients", "recipient_id", _validate_recipient)


def load_volunteers(path) -> tuple[dict[str, Volunteer], list[str]]:
    return _load(path, "volunteers", "volunteer_id", _validate_volunteer)
