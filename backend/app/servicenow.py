import requests
from datetime import datetime, timezone

from app.settings import settings


# ============================================================
# In-memory mock ServiceNow storage
# ============================================================

counter = 1245

incidents = {}
requests_db = {}


# ============================================================
# ID Generator
# ============================================================

def next_id(prefix: str) -> str:
    global counter

    counter += 1

    return f"{prefix}{counter}"


# ============================================================
# Mock Incident
# ============================================================

def mock_incident(payload: dict):

    number = next_id("INC")

    row = {
        "number": number,
        "sys_id": f"mock-{number.lower()}",
        "state": "New",
        **payload,
        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    incidents[number] = row

    return row


# ============================================================
# Mock Request
# ============================================================

def mock_request(payload: dict):

    number = next_id("REQ")

    row = {
        "number": number,
        "sys_id": f"mock-{number.lower()}",
        "state": "Open",
        **payload,
        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    requests_db[number] = row

    return row


# ============================================================
# Create Incident
# ============================================================

def create_incident(payload: dict):

    # --------------------------------------------------------
    # Mock mode
    # --------------------------------------------------------

    if not settings.servicenow_enabled:

        return mock_incident(
            payload
        )

    # --------------------------------------------------------
    # Real ServiceNow
    # --------------------------------------------------------

    url = (
        settings.servicenow_instance.rstrip("/")
        + "/api/now/table/incident"
    )

    response = requests.post(
        url,
        json=payload,
        auth=(
            settings.servicenow_username,
            settings.servicenow_password,
        ),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=15,
    )

    response.raise_for_status()

    return response.json()["result"]


# ============================================================
# Create Request
# ============================================================

def create_request(payload: dict):

    # --------------------------------------------------------
    # Mock mode
    # --------------------------------------------------------

    if not settings.servicenow_enabled:

        return mock_request(
            payload
        )

    # --------------------------------------------------------
    # ServiceNow Request
    #
    # For now we keep the request workflow compatible with
    # the mock implementation. A real Service Catalog API
    # can be connected later.
    # --------------------------------------------------------

    return mock_request(
        payload
    )


# ============================================================
# Update Incident
# ============================================================

def update_incident(
    number: str,
    payload: dict
):

    # --------------------------------------------------------
    # Mock mode
    # --------------------------------------------------------

    if not settings.servicenow_enabled:

        if number in incidents:

            incidents[number].update(
                payload
            )

            incidents[number]["state"] = payload.get(
                "state",
                incidents[number].get(
                    "state"
                ),
            )

            incidents[number]["updated_at"] = (
                datetime.now(
                    timezone.utc
                ).isoformat()
            )

        return incidents.get(
            number
        )

    # --------------------------------------------------------
    # Real ServiceNow
    # --------------------------------------------------------

    query_url = (
        settings.servicenow_instance.rstrip("/")
        + "/api/now/table/incident"
    )

    response = requests.get(
        query_url,
        params={
            "sysparm_query": f"number={number}",
            "sysparm_limit": 1,
        },
        auth=(
            settings.servicenow_username,
            settings.servicenow_password,
        ),
        headers={
            "Accept": "application/json",
        },
        timeout=15,
    )

    response.raise_for_status()

    rows = response.json().get(
        "result",
        []
    )

    if not rows:
        return None

    sys_id = rows[0]["sys_id"]

    response = requests.patch(
        f"{query_url}/{sys_id}",
        json=payload,
        auth=(
            settings.servicenow_username,
            settings.servicenow_password,
        ),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=15,
    )

    response.raise_for_status()

    return response.json()["result"]


# ============================================================
# Get Mock Incident
# ============================================================

def get_incident(
    number: str
):

    return incidents.get(
        number
    )


# ============================================================
# Get Mock Request
# ============================================================

def get_request(
    number: str
):

    return requests_db.get(
        number
    )


# ============================================================
# List Mock Incidents
# ============================================================

def list_incidents():

    return list(
        incidents.values()
    )


# ============================================================
# List Mock Requests
# ============================================================

def list_requests():

    return list(
        requests_db.values()
    )