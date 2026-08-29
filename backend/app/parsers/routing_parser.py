"""
Routing Problem Detection (Feature 3).

Checks a supplied list of expected inter-VLAN/network routes against
what's actually present in the routing table, flagging missing routes.
"""

from dataclasses import dataclass, field
from app.models.schemas import RouteEntry


@dataclass
class RoutingFinding:
    issue_detected: bool
    missing_routes: list[str] = field(default_factory=list)
    summary: str = ""


def analyze_routes(routes: list[RouteEntry]) -> RoutingFinding:
    missing = [r.destination_network for r in routes if not r.exists]

    return RoutingFinding(
        issue_detected=bool(missing),
        missing_routes=missing,
        summary=(
            f"No route(s) exist to: {', '.join(missing)}. "
            "Configure inter-VLAN routing or a static/dynamic route for the missing network(s)."
            if missing
            else "All expected routes are present."
        ),
    )


if __name__ == "__main__":
    example = [
        RouteEntry(destination_network="VLAN10 -> VLAN40 (Server Network)", exists=False),
    ]
    print(analyze_routes(example))
