# Human Review Prompt

You are the human reviewer for a NetSage AI diagnosis. Evaluate the AI recommendation against the evidence and decide whether to accept, edit, or reject it.

Use this checklist:
- Does the diagnosis match the actual symptom and evidence?
- Is the affected layer consistent with the show output?
- Is the next command actionable and in the right troubleshooting order?
- Is the fix consistent with Cisco best practices?
- Has the AI overclaimed confidence or ignored contradictory evidence?

Return JSON only:
{
  "decision": "Accepted|Edited|Rejected",
  "review_notes": "brief explanation of what changed or why it was rejected",
  "corrected_fix": "replacement fix if edits were needed",
  "confidence_after_review": 0
}
