"""
VLAN Configuration Analyzer (Feature 1).

Deterministic diff between configured VLANs and expected VLANs, plus
trunk-allowed-VLAN checks. No AI needed here — this is the layer that
should catch the majority of VLAN misconfiguration cases before any
LLM call is made.
"""

from dataclasses import dataclass, field
from app.models.schemas import VlanConfig


@dataclass
class VlanFinding:
    issue_detected: bool
    missing_vlans: dict[int, str] = field(default_factory=dict)
    extra_vlans: dict[int, str] = field(default_factory=dict)
    missing_from_trunk: list[int] = field(default_factory=list)
    summary: str = ""


def analyze_vlan_config(config: VlanConfig) -> VlanFinding:
    missing = {
        vid: name
        for vid, name in config.expected_vlans.items()
        if vid not in config.configured_vlans
    }
    extra = {
        vid: name
        for vid, name in config.configured_vlans.items()
        if vid not in config.expected_vlans
    }
    missing_from_trunk = [
        vid
        for vid in config.expected_vlans
        if vid not in config.trunk_allowed_vlans and vid in config.configured_vlans
    ]

    issue_detected = bool(missing or extra or missing_from_trunk)

    summary_parts = []
    if missing:
        names = ", ".join(f"VLAN {vid} ({name})" for vid, name in missing.items())
        summary_parts.append(f"Missing VLAN(s): {names}")
    if missing_from_trunk:
        summary_parts.append(
            f"VLAN(s) not allowed on trunk: {missing_from_trunk}"
        )
    if extra:
        names = ", ".join(f"VLAN {vid} ({name})" for vid, name in extra.items())
        summary_parts.append(f"Unexpected VLAN(s) present: {names}")

    return VlanFinding(
        issue_detected=issue_detected,
        missing_vlans=missing,
        extra_vlans=extra,
        missing_from_trunk=missing_from_trunk,
        summary="; ".join(summary_parts) if summary_parts else "No VLAN issues detected.",
    )


if __name__ == "__main__":
    # Example matching the project brief: Faculty VLAN 20 missing
    example = VlanConfig(
        device="SW1",
        configured_vlans={10: "Students", 30: "Guests"},
        expected_vlans={10: "Students", 20: "Faculty", 30: "Guests"},
        trunk_allowed_vlans=[10, 30],
    )
    print(analyze_vlan_config(example))
