"""
ACL Security Analysis (Feature 4).

Given a set of ACL rules and a user complaint about blocked traffic
(source -> destination), checks whether an explicit DENY rule explains it.
"""

from dataclasses import dataclass
from app.models.schemas import AclRule


@dataclass
class AclFinding:
    issue_detected: bool
    blocking_rule: str = ""
    confidence: float = 0.0
    suggested_action: str = ""


def analyze_acl(rules: list[AclRule], source: str, destination: str) -> AclFinding:
    for rule in rules:
        if (
            rule.action.upper() == "DENY"
            and rule.source.lower() == source.lower()
            and rule.destination.lower() == destination.lower()
        ):
            return AclFinding(
                issue_detected=True,
                blocking_rule=f"DENY {rule.source} -> {rule.destination}",
                confidence=95.0,
                suggested_action=(
                    f"Modify or remove the ACL rule denying {rule.source} -> "
                    f"{rule.destination}, or add an explicit PERMIT rule above it."
                ),
            )

    return AclFinding(
        issue_detected=False,
        suggested_action="No explicit DENY rule found for this traffic pattern; "
        "check implicit deny-all at the end of the ACL, or route/firewall config instead.",
    )


if __name__ == "__main__":
    rules = [AclRule(action="DENY", source="Faculty", destination="Server")]
    print(analyze_acl(rules, source="Faculty", destination="Server"))
