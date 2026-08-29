"""
IP Address and DHCP Validation (Feature 2).

Checks whether a device's gateway lives in the same subnet as its IP,
catches obviously malformed addressing, and flags duplicate IPs when
given a batch of devices.
"""

import ipaddress
from dataclasses import dataclass
from app.models.schemas import DeviceIpConfig


@dataclass
class IpFinding:
    issue_detected: bool
    problem: str = ""
    layer: str = "Layer 3"
    suggested_fix: str = ""


def analyze_ip_config(config: DeviceIpConfig) -> IpFinding:
    try:
        network = ipaddress.ip_network(
            f"{config.ip_address}/{config.subnet_mask}", strict=False
        )
        gateway_ip = ipaddress.ip_address(config.gateway)
    except ValueError as e:
        return IpFinding(
            issue_detected=True,
            problem=f"Malformed IP/subnet/gateway: {e}",
            suggested_fix="Verify the IP, subnet mask, and gateway are valid addresses.",
        )

    if gateway_ip not in network:
        # Suggest the "obvious" fix: same host bits as the device's own subnet,
        # gateway typically .1 -- this is a heuristic, not a guarantee.
        corrected_gateway = list(network.hosts())[0] if network.num_addresses > 2 else None
        fix = (
            f"Change gateway to {corrected_gateway} (or the correct gateway for "
            f"subnet {network})."
            if corrected_gateway
            else f"Assign a gateway within subnet {network}."
        )
        return IpFinding(
            issue_detected=True,
            problem=(
                f"Gateway {config.gateway} belongs to a different subnet than "
                f"device IP {config.ip_address}/{config.subnet_mask} (network {network})."
            ),
            suggested_fix=fix,
        )

    return IpFinding(issue_detected=False, problem="No IP/gateway issues detected.")


def find_duplicate_ips(configs: list[DeviceIpConfig]) -> list[str]:
    seen: dict[str, str] = {}
    duplicates = []
    for c in configs:
        if c.ip_address in seen:
            duplicates.append(
                f"Duplicate IP {c.ip_address}: assigned to both {seen[c.ip_address]} and {c.device}"
            )
        else:
            seen[c.ip_address] = c.device
    return duplicates


if __name__ == "__main__":
    example = DeviceIpConfig(
        device="Student-PC1",
        ip_address="192.168.20.15",
        subnet_mask="255.255.255.0",
        gateway="192.168.30.1",
    )
    print(analyze_ip_config(example))
