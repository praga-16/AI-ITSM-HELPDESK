from typing import Any, Dict


# ============================================================
# Automation Engine
# ============================================================

def execute(
    message: str,
    analysis: Dict[str, Any],
) -> Dict[str, Any]:

    message = (
        message or ""
    ).strip()

    route = analysis.get(
        "route",
        "unknown",
    )

    intent = analysis.get(
        "intent",
        "Unknown",
    )

    category = analysis.get(
        "category",
        "General",
    )

    subcategory = analysis.get(
        "subcategory",
        "General",
    )

    # ========================================================
    # Password / Self-Healing
    # ========================================================

    if route in {
        "self_heal",
        "self-heal",
        "password_reset",
        "password",
    }:

        return {
            "status": "completed",
            "automation_type": "password_reset",
            "action": "password_reset_workflow",
            "message": (
                "Password self-service workflow "
                "has been triggered."
            ),
            "audit": {
                "intent": intent,
                "category": category,
                "subcategory": subcategory,
            },
        }

    # ========================================================
    # Software Provisioning
    # ========================================================

    if route in {
        "software",
        "software_request",
        "request",
    }:

        return {
            "status": "pending_approval",
            "automation_type": "software_provisioning",
            "action": "software_request_workflow",
            "message": (
                "Software provisioning request has been "
                "created and is awaiting the configured "
                "approval/provisioning workflow."
            ),
            "audit": {
                "intent": intent,
                "category": category,
                "subcategory": subcategory,
            },
        }

    # ========================================================
    # Incident
    # ========================================================

    if route == "incident":

        return {
            "status": "ticket_created",
            "automation_type": "incident",
            "action": "incident_workflow",
            "message": (
                "Incident workflow has been initiated."
            ),
            "audit": {
                "intent": intent,
                "category": category,
                "subcategory": subcategory,
            },
        }

    # ========================================================
    # Knowledge
    # ========================================================

    if route == "knowledge":

        return {
            "status": "completed",
            "automation_type": "knowledge",
            "action": "knowledge_response",
            "message": (
                "Knowledge-base response workflow completed."
            ),
            "audit": {
                "intent": intent,
                "category": category,
                "subcategory": subcategory,
            },
        }

    # ========================================================
    # Escalation
    # ========================================================

    return {
        "status": "escalated",
        "automation_type": "escalation",
        "action": "manual_review",
        "message": (
            "The request requires manual IT support review."
        ),
        "audit": {
            "intent": intent,
            "category": category,
            "subcategory": subcategory,
        },
    }