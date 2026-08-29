"""API routes for NetSage AI."""

import csv
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.models.schemas import TroubleshootRequest, Diagnosis, FeedbackRequest
from app.parsers.vlan_parser import analyze_vlan_config
from app.parsers.ip_dhcp_parser import analyze_ip_config
from app.parsers.routing_parser import analyze_routes
from app.parsers.acl_parser import analyze_acl
from app.rag.reasoner import generate_diagnosis

router = APIRouter()

FEEDBACK_LOG = Path(__file__).resolve().parents[2] / "data" / "feedback_log.jsonl"
CASES_CSV = Path(__file__).resolve().parents[2] / "data" / "cases.csv"


def _case_summary() -> dict:
    issue_types: dict[str, int] = {}
    severity: dict[str, int] = {}
    if CASES_CSV.exists():
        with CASES_CSV.open("r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                concept = (row.get("concept") or "Unknown").strip()
                issue_types[concept] = issue_types.get(concept, 0) + 1
                sev = (row.get("severity") or "Unknown").strip()
                severity[sev] = severity.get(sev, 0) + 1
    return {"issue_type_breakdown": issue_types, "severity_breakdown": severity}


@router.post("/troubleshoot", response_model=Diagnosis)
def troubleshoot(request: TroubleshootRequest) -> Diagnosis:
    """
    Runs the deterministic parsers over whatever data the user supplied,
    then passes findings + problem description to the RAG reasoning layer
    for a final structured diagnosis.
    """
    findings: dict = {}

    if request.vlan_config:
        findings["vlan"] = analyze_vlan_config(request.vlan_config)

    if request.ip_config:
        findings["ip"] = analyze_ip_config(request.ip_config)

    if request.routes:
        findings["routing"] = analyze_routes(request.routes)

    if request.acl_rules:
        # Attempt to infer source/destination from the problem description is
        # non-trivial; for the scaffold, check the first rule pair supplied.
        # In a fuller implementation, parse source/dest out of the complaint.
        if request.acl_rules:
            first = request.acl_rules[0]
            findings["acl"] = analyze_acl(
                request.acl_rules, source=first.source, destination=first.destination
            )

    if not findings and not request.raw_logs:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one of: vlan_config, ip_config, routes, "
            "acl_rules, or raw_logs so the parsers have something to analyze.",
        )

    try:
        diagnosis = generate_diagnosis(request.problem_description, findings)
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return diagnosis


@router.post("/feedback")
def submit_feedback(feedback: FeedbackRequest):
    """Logs human validation of a diagnosis for future eval/improvement."""
    FEEDBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **feedback.model_dump(),
    }
    with open(FEEDBACK_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return {"status": "logged", "id": entry["id"]}


@router.get("/dashboard")
def dashboard_stats():
    """Aggregate stats for the dashboard: case themes, severity, and human review agreement."""
    summary = _case_summary()
    verdicts: dict[str, int] = {}
    total = 0
    if FEEDBACK_LOG.exists():
        with open(FEEDBACK_LOG, encoding="utf-8") as f:
            for line in f:
                total += 1
                entry = json.loads(line)
                v = entry.get("verdict", "Unknown")
                verdicts[v] = verdicts.get(v, 0) + 1

    accepted = verdicts.get("Correct", 0)
    edited = verdicts.get("Partially Correct", 0)
    rejected = verdicts.get("Wrong", 0)
    agreement_rate = (accepted + edited) / total if total else 0

    return {
        "total_diagnoses": total,
        "verdict_breakdown": verdicts,
        "issue_type_breakdown": summary["issue_type_breakdown"],
        "severity_breakdown": summary["severity_breakdown"],
        "ai_vs_human_agreement": {
            "accepted": accepted,
            "edited": edited,
            "rejected": rejected,
            "agreement_rate": round(agreement_rate, 2),
        },
    }
