from typing import Any, Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.automation import execute
from app.classifier import classify
from app.llm import generate
from app.rag import build, search
from app.servicenow import (
    create_incident,
    create_request,
)
from app.store import all_items, count, save
from app.settings import settings


# ============================================================
# FastAPI
# ============================================================

app = FastAPI(
    title="AI ITSM Helpdesk Automation Platform",
    version="1.0.0",
    description=(
        "AI-powered IT Service Management Helpdesk "
        "using classification, RAG, open-source LLM, "
        "automation, ServiceNow and MongoDB."
    ),
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Request Models
# ============================================================

class ChatRequest(BaseModel):
    message: str


class TicketRequest(BaseModel):
    message: str


# ============================================================
# Startup
# ============================================================

@app.on_event("startup")
def startup_event():
    # The embedding model is loaded on the first retrieval. Keeping startup
    # lightweight lets the health check and UI become available immediately.
    print("AI ITSM Helpdesk started; RAG index will initialize on first search.")


# ============================================================
# Health
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "AI ITSM Helpdesk",
        "llm": settings.hf_model,
    }


# ============================================================
# Source Formatter
# ============================================================

def source_response(
    rows: List[Dict[str, Any]]
):

    sources = []

    for item in rows:

        sources.append(
            {
                "name": (
                    item.get("name")
                    or item.get("title")
                    or item.get("source")
                    or "Knowledge Article"
                ),
                "score": float(
                    item.get(
                        "score",
                        0,
                    )
                ),
                "excerpt": item.get(
                    "text",
                    "",
                )[:500],
            }
        )

    return sources


# ============================================================
# RAG Context
# ============================================================

def build_context(
    rows: List[Dict[str, Any]]
) -> str:

    if not rows:
        return ""

    parts = []

    for item in rows:

        title = (
            item.get("title")
            or item.get("name")
            or item.get("source")
            or "Knowledge Article"
        )

        text = item.get(
            "text",
            "",
        )

        if text:

            parts.append(
                f"TITLE: {title}\n"
                f"{text}"
            )

    return "\n\n---\n\n".join(
        parts
    )


# ============================================================
# RAG Search
# ============================================================

def retrieve_knowledge(
    message: str,
    top_k: int = 3,
):

    try:

        rows = search(
            message,
            top_k=top_k,
        )

        if not rows:
            return []

        # Keep weakly related articles out of the LLM prompt. This prevents a
        # strong match such as VPN troubleshooting from being diluted by a
        # generic article that merely happens to be in the top-k results.
        best_score = float(rows[0].get("score", 0))
        minimum_score = max(0.25, best_score * 0.65)

        return [
            row for row in rows
            if float(row.get("score", 0)) >= minimum_score
        ]

    except Exception as exc:

        print(
            "RAG search error:"
        )

        print(
            str(exc)
        )

        return []


# ============================================================
# LLM + RAG
# ============================================================

def generate_grounded_answer(
    message: str,
    rows: List[Dict[str, Any]],
):

    if not rows:
        return None

    context = build_context(
        rows
    )

    if not context:
        return None

    try:

        return generate(
            message,
            context,
        )

    except Exception as exc:

        print(
            "LLM generation error:"
        )

        print(
            str(exc)
        )

        return None


# ============================================================
# CHAT
# ============================================================

@app.post("/api/chat")
def chat(
    request: ChatRequest,
):

    message = (
        request.message
        or ""
    ).strip()

    # --------------------------------------------------------
    # Empty request
    # --------------------------------------------------------

    if not message:

        return {
            "response": (
                "Please enter an IT support question."
            ),
            "intent": "Unknown",
            "confidence": 0,
            "route": "escalate",
            "analysis": {},
            "sources": [],
        }

    print("=" * 60)
    print("NEW ITSM REQUEST")
    print(message)
    print("=" * 60)

    # ========================================================
    # 1. CLASSIFICATION
    # ========================================================

    try:

        analysis = classify(
            message
        )

    except Exception as exc:

        print(
            "Classification error:"
        )

        print(
            str(exc)
        )

        return {
            "response": (
                "I could not classify this request. "
                "Please contact IT support."
            ),
            "intent": "Unknown",
            "confidence": 0,
            "route": "escalate",
            "analysis": {},
            "sources": [],
        }

    intent = analysis.get(
        "intent",
        "Unknown",
    )

    route = analysis.get(
        "route",
        "escalate",
    )

    confidence = float(
        analysis.get(
            "confidence",
            0,
        )
    )

    # ========================================================
    # 2. RAG
    # ========================================================

    rows = retrieve_knowledge(
        message,
        top_k=5,
    )

    sources = source_response(
        rows
    )

    # ========================================================
    # 3. INCIDENT
    # ========================================================

    if route == "incident":

        answer = generate_grounded_answer(
            message,
            rows,
        )

        if not answer:

            answer = (
                "I could not generate a grounded response "
                "from the approved enterprise knowledge base. "
                "This incident should be escalated to the "
                "appropriate IT support group."
            )

        # ----------------------------------------------------
        # ServiceNow Incident
        # ----------------------------------------------------

        servicenow_payload = {
            "short_description": analysis.get(
                "summary",
                message,
            ),
            "description": message,
            "category": analysis.get(
                "category",
                "General",
            ),
            "subcategory": analysis.get(
                "subcategory",
                "General",
            ),
            "priority": analysis.get(
                "priority",
                "P3",
            ),
            "impact": analysis.get(
                "impact",
                "Individual",
            ),
            "urgency": analysis.get(
                "urgency",
                "Medium",
            ),
            "assignment_group": analysis.get(
                "assignment_group",
                "IT Support",
            ),
        }

        try:

            servicenow_result = create_incident(
                servicenow_payload
            )

        except Exception as exc:

            print(
                "ServiceNow incident error:"
            )

            print(
                str(exc)
            )

            servicenow_result = {
                "status": "error",
                "message": str(exc),
            }

        # ----------------------------------------------------
        # Automation
        # ----------------------------------------------------

        try:

            automation_result = execute(
                message,
                analysis,
            )

        except Exception as exc:

            print(
                "Automation error:"
            )

            print(
                str(exc)
            )

            automation_result = {
                "status": "error",
                "message": str(exc),
            }

        ticket = {
            "ticket_id": servicenow_result.get("number", "Pending"),
            "status": servicenow_result.get("state", "New"),
        }

        result = {
            "message": message,
            "response": answer,
            "intent": intent,
            "confidence": confidence,
            "route": "incident",
            "analysis": analysis,
            "sources": sources,
            "servicenow": servicenow_result,
            "ticket": ticket,
            "automation": automation_result,
        }

        try:

            save("tickets", result)
            save("automation_logs", automation_result)

        except Exception as exc:

            print(
                "Store error:"
            )

            print(
                str(exc)
            )

        return result

    # ========================================================
    # 4. KNOWLEDGE
    # ========================================================

    if route == "knowledge":

        if (
            not rows
            or float(
                rows[0].get(
                    "score",
                    0,
                )
            ) < 0.35
        ):

            return {
                "response": (
                    "I could not find sufficient information "
                    "in the approved enterprise knowledge base "
                    "to answer this question."
                ),
                "intent": intent,
                "confidence": min(
                    confidence,
                    0.34,
                ),
                "route": "escalate",
                "analysis": {
                    **analysis,
                    "route": "escalate",
                },
                "sources": sources,
            }

        answer = generate_grounded_answer(
            message,
            rows,
        )

        if not answer:

            answer = (
                "The AI model could not generate a grounded "
                "answer from the approved enterprise "
                "knowledge base. Please contact IT support."
            )

        return {
            "response": answer,
            "intent": intent,
            "confidence": confidence,
            "route": "knowledge",
            "analysis": analysis,
            "sources": sources,
        }

    # ========================================================
    # 5. SELF-HEALING / PASSWORD
    # ========================================================

    if route in {
        "self_heal",
        "self-heal",
        "password_reset",
        "password",
    }:

        try:

            automation_result = execute(
                message,
                analysis,
            )

        except Exception as exc:

            print(
                "Self-healing error:"
            )

            print(
                str(exc)
            )

            automation_result = {
                "status": "error",
                "message": str(exc),
            }

        answer = generate_grounded_answer(
            message,
            rows,
        )

        if not answer:

            answer = (
                "Your request has been identified as a "
                "self-service IT request. The approved "
                "automation workflow has been triggered."
            )

        result = {
            "message": message,
            "response": answer,
            "intent": intent,
            "confidence": confidence,
            "route": "self_heal",
            "analysis": analysis,
            "sources": sources,
            "automation": automation_result,
        }

        try:

            save("chat_history", result)
            save("automation_logs", automation_result)

        except Exception as exc:

            print(
                "Store error:"
            )

            print(
                str(exc)
            )

        return result

    # ========================================================
    # 6. SOFTWARE REQUEST
    # ========================================================

    if route in {
        "software",
        "software_request",
        "request",
    }:

        answer = generate_grounded_answer(
            message,
            rows,
        )

        if not answer:

            answer = (
                "This request has been identified as a "
                "software or service request. It will be "
                "processed through the approved IT "
                "provisioning workflow."
            )

        # ----------------------------------------------------
        # ServiceNow Request
        # ----------------------------------------------------

        request_payload = {
            "short_description": analysis.get(
                "summary",
                message,
            ),
            "description": message,
            "category": analysis.get(
                "category",
                "Software",
            ),
            "subcategory": analysis.get(
                "subcategory",
                "Software Request",
            ),
            "priority": analysis.get(
                "priority",
                "P3",
            ),
            "requested_for": "Employee",
        }

        try:

            servicenow_result = create_request(
                request_payload
            )

        except Exception as exc:

            print(
                "ServiceNow request error:"
            )

            print(
                str(exc)
            )

            servicenow_result = {
                "status": "error",
                "message": str(exc),
            }

        # ----------------------------------------------------
        # Automation
        # ----------------------------------------------------

        try:

            automation_result = execute(
                message,
                analysis,
            )

        except Exception as exc:

            print(
                "Software automation error:"
            )

            print(
                str(exc)
            )

            automation_result = {
                "status": "error",
                "message": str(exc),
            }
        if isinstance(automation_result, dict):
            automation_result["servicenow_number"] = (
                servicenow_result.get("number")
            )

            automation_result["servicenow_sys_id"] = (
                servicenow_result.get("sys_id")
            )
        software_request = {
            "request_id": servicenow_result.get("number", "Pending"),
            "status": servicenow_result.get("state", "Open"),
        }

        result = {
            "message": message,
            "response": answer,
            "intent": intent,
            "confidence": confidence,
            "route": "software",
            "analysis": analysis,
            "sources": sources,
            "servicenow": servicenow_result,
            "software_request": software_request,
            "automation": automation_result,
        }

        try:

            save("software_requests", result)
            save("automation_logs", automation_result)

        except Exception as exc:

            print(
                "Store error:"
            )

            print(
                str(exc)
            )

        return result

    # ========================================================
    # 7. UNKNOWN / ESCALATION
    # ========================================================

    if route in {
        "escalate",
        "unknown",
        "unsupported",
    }:

        return {
            "response": (
                "I could not find sufficient approved "
                "enterprise knowledge to safely answer "
                "this request. I recommend escalating "
                "it to IT support rather than providing "
                "an unsupported answer."
            ),
            "intent": intent,
            "confidence": confidence,
            "route": "escalate",
            "analysis": {
                **analysis,
                "route": "escalate",
            },
            "sources": sources,
        }

    # ========================================================
    # 8. GENERAL FALLBACK
    # ========================================================

    answer = generate_grounded_answer(
        message,
        rows,
    )

    if not answer:

        answer = (
            "I could not generate a grounded answer "
            "from the approved enterprise knowledge base. "
            "Please contact IT support."
        )

    return {
        "response": answer,
        "intent": intent,
        "confidence": confidence,
        "route": route,
        "analysis": analysis,
        "sources": sources,
    }


# ============================================================
# KNOWLEDGE BASE
# ============================================================

@app.get("/api/knowledge")
def knowledge_list():

    from pathlib import Path

    base = (
        Path(__file__).resolve().parents[2]
        / "knowledge"
    )

    documents = []

    if base.exists():

        for path in sorted(
            base.rglob("*")
        ):

            if (
                path.is_file()
                and path.suffix.lower()
                in {
                    ".txt",
                    ".md",
                    ".markdown",
                }
            ):

                documents.append(
                    {
                        "name": path.name,
                        "source": str(
                            path.relative_to(
                                base
                            )
                        ),
                    }
                )

    return {
        "documents": documents
    }


# ============================================================
# KNOWLEDGE SEARCH
# ============================================================

@app.post("/api/knowledge/search")
def knowledge_search(
    request: Dict[str, Any],
):

    q = str(request.get("query", ""))
    top_k = int(request.get("top_k", 5))

    rows = retrieve_knowledge(
        q,
        top_k=top_k,
    )

    return {
        "query": q,
        "results": rows,
    }


# ============================================================
# OPERATIONS DATA
# ============================================================

@app.get("/api/tickets")
def tickets_list():
    return {"tickets": all_items("tickets")}


@app.get("/api/software/requests")
def software_requests_list():
    return {"requests": all_items("software_requests")}


@app.get("/api/automation/logs")
def automation_logs_list():
    return {"logs": all_items("automation_logs")}


@app.get("/api/dashboard/stats")
def dashboard_stats():
    tickets = all_items("tickets")
    automation_logs = all_items("automation_logs")

    return {
        "total_tickets": len(tickets),
        "open_tickets": sum(
            1 for ticket in tickets
            if ticket.get("ticket", {}).get("status") not in {"Resolved", "Closed"}
        ),
        "ai_resolved": sum(
            1 for log in automation_logs
            if log.get("status") == "completed"
        ),
        "escalated": count("escalations"),
        "software_requests": count("software_requests"),
        "automation_actions": len(automation_logs),
    }


# ============================================================
# MANUAL TICKET CREATION
# ============================================================

@app.post("/api/tickets")
def create_ticket(
    request: TicketRequest,
):

    message = (
        request.message
        or ""
    ).strip()

    if not message:

        return {
            "status": "error",
            "message": "Ticket message is required.",
        }

    analysis = classify(
        message
    )

    # --------------------------------------------------------
    # Incident
    # --------------------------------------------------------

    if analysis.get(
        "route"
    ) == "incident":

        payload = {
            "short_description": analysis.get(
                "summary",
                message,
            ),
            "description": message,
            "category": analysis.get(
                "category",
                "General",
            ),
            "subcategory": analysis.get(
                "subcategory",
                "General",
            ),
            "priority": analysis.get(
                "priority",
                "P3",
            ),
            "impact": analysis.get(
                "impact",
                "Individual",
            ),
            "urgency": analysis.get(
                "urgency",
                "Medium",
            ),
            "assignment_group": analysis.get(
                "assignment_group",
                "IT Support",
            ),
        }

        servicenow_result = create_incident(
            payload
        )

    # --------------------------------------------------------
    # Request
    # --------------------------------------------------------

    else:

        payload = {
            "short_description": analysis.get(
                "summary",
                message,
            ),
            "description": message,
            "category": analysis.get(
                "category",
                "General",
            ),
            "subcategory": analysis.get(
                "subcategory",
                "General",
            ),
            "priority": analysis.get(
                "priority",
                "P3",
            ),
            "requested_for": "Employee",
        }

        servicenow_result = create_request(
            payload
        )

    result = {
        "message": message,
        "analysis": analysis,
        "servicenow": servicenow_result,
    }

    try:

        save("tickets", result)

    except Exception as exc:

        print(
            "Store error:"
        )

        print(
            str(exc)
        )

    return result


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "name": (
            "AI ITSM Helpdesk "
            "Automation Platform"
        ),
        "status": "running",
        "version": "1.0.0",
        "llm": settings.hf_model,
        "architecture": [
            "ITSM Classification",
            "RAG",
            "FAISS",
            "Sentence Transformers",
            "Open-Source LLM",
            "Automation",
            "ServiceNow",
            "MongoDB",
        ],
    }
