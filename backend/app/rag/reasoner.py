"""
AI Reasoning Layer.

Combines the user's problem description, the deterministic parser findings,
and retrieved knowledge base context into a prompt, then calls the LLM
(Gemini by default) to produce a structured diagnosis.
"""

import json
import os
from pathlib import Path

import google.generativeai as genai
from dotenv import find_dotenv, load_dotenv

from app.rag.retriever import retrieve_context
from app.models.schemas import Diagnosis


def _load_local_env() -> None:
    """Load project-level .env values before checking for API keys."""
    candidates = [
        Path(__file__).resolve().parents[2] / ".env",
        Path(__file__).resolve().parents[3] / ".env",
    ]
    for candidate in candidates:
        if candidate.exists():
            load_dotenv(candidate, override=False)
    load_dotenv(find_dotenv(usecwd=True), override=False)


_load_local_env()

SYSTEM_INSTRUCTIONS = """\
You are NetSage AI, an expert Cisco network troubleshooting assistant.
You are given:
1. A user's plain-language problem description.
2. Findings already computed by deterministic network config parsers.
3. Relevant excerpts from Cisco networking documentation.

Using ONLY this information, respond with a single JSON object with exactly
these fields:
{
  "issue": "short issue title",
  "affected_layer": "e.g. Layer 2 / Layer 3 / Application",
  "root_cause": "explanation of the root cause",
  "confidence": <number 0-100>,
  "recommended_fix": "concrete fix",
  "verification_steps": ["step 1", "step 2", ...]
}

Do not include any text outside the JSON object. Base your confidence score
on how directly the parser findings and documentation support the diagnosis —
do not overstate certainty when the data is ambiguous or incomplete.
"""


def _get_model_candidates() -> list[str]:
    preferred = os.environ.get("GEMINI_MODEL")
    candidates = []
    if preferred:
        candidates.append(preferred)
    candidates.extend([
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
    ])

    seen = set()
    ordered = []
    for name in candidates:
        if name and name not in seen:
            seen.add(name)
            ordered.append(name)
    return ordered


def _configure_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)


def generate_diagnosis(
    problem_description: str,
    parser_findings: dict,
) -> Diagnosis:
    """
    parser_findings: dict of whatever the parsers in app/parsers/ returned,
    e.g. {"vlan": VlanFinding(...), "ip": IpFinding(...), ...}
    Pass only the findings relevant to the data the user actually supplied.
    """
    _configure_gemini()

    retrieval_query = f"{problem_description} {json.dumps(parser_findings, default=str)}"
    context_chunks = retrieve_context(retrieval_query, k=4)
    context_block = "\n---\n".join(context_chunks)

    prompt = f"""\
{SYSTEM_INSTRUCTIONS}

## User Problem
{problem_description}

## Parser Findings
{json.dumps(parser_findings, default=str, indent=2)}

## Retrieved Documentation
{context_block}
"""

    last_error = None
    for model_name in _get_model_candidates():
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            # Strip markdown code fences if the model added them despite instructions.
            if raw_text.startswith("```"):
                raw_text = raw_text.strip("`")
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]

            parsed = json.loads(raw_text)
            parsed["source_snippets"] = context_chunks
            return Diagnosis(**parsed)
        except Exception as exc:
            last_error = exc
            if "404" in str(exc) or "not found" in str(exc).lower():
                continue
            raise

    raise RuntimeError(
        f"Unable to generate diagnosis with any supported Gemini model. "
        f"Last error: {last_error}"
    )
