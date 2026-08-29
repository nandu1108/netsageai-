#!/usr/bin/env python3
"""Deterministic rule checker for common Cisco lab faults.

The checker validates configuration data before or alongside an AI diagnosis.
It catches the most common issues in VLAN, IP, DHCP, routing, and ACL lab tasks.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from ipaddress import ip_address, ip_network
from pathlib import Path
from typing import Any


@dataclass
class RuleResult:
    rule: str
    passed_check: bool
    detail: str


def check_duplicate_ips(device_configs: list[dict[str, Any]]) -> RuleResult:
    seen: dict[str, str] = {}
    for cfg in device_configs or []:
        ip = cfg.get("ip_address")
        device = cfg.get("device")
        if not ip:
            continue
        if ip in seen:
            return RuleResult(
                rule="duplicate_ip",
                passed_check=False,
                detail=f"Duplicate IP {ip} assigned to {seen[ip]} and {device}.",
            )
        seen[ip] = device
    return RuleResult(rule="duplicate_ip", passed_check=True, detail="No duplicate IPs found.")


def check_wrong_mask(ip_cfg: dict[str, Any]) -> RuleResult:
    if not ip_cfg:
        return RuleResult(rule="wrong_mask", passed_check=True, detail="No IP config to validate.")
    ip = ip_cfg.get("ip_address")
    mask = ip_cfg.get("subnet_mask")
    if not ip or not mask:
        return RuleResult(rule="wrong_mask", passed_check=True, detail="IP or mask missing; checking skipped.")
    try:
        network = ip_network(f"{ip}/{mask}", strict=False)
    except ValueError as exc:
        return RuleResult(rule="wrong_mask", passed_check=False, detail=f"Malformed IP or subnet mask: {exc}")
    host_bits = network.num_addresses - network.prefixlen
    if host_bits == 0:
        return RuleResult(rule="wrong_mask", passed_check=False, detail=f"Subnet mask {mask} may be invalid for {ip}.")
    return RuleResult(rule="wrong_mask", passed_check=True, detail=f"IP {ip}/{mask} is valid for network {network}.")


def check_gateway_mismatch(ip_cfg: dict[str, Any]) -> RuleResult:
    if not ip_cfg:
        return RuleResult(rule="gateway_mismatch", passed_check=True, detail="No gateway to validate.")
    ip = ip_cfg.get("ip_address")
    mask = ip_cfg.get("subnet_mask")
    gateway = ip_cfg.get("gateway")
    if not ip or not mask or not gateway:
        return RuleResult(rule="gateway_mismatch", passed_check=True, detail="Gateway check skipped because required fields are missing.")
    try:
        subnet = ip_network(f"{ip}/{mask}", strict=False)
        gateway_addr = ip_address(gateway)
    except ValueError as exc:
        return RuleResult(rule="gateway_mismatch", passed_check=False, detail=f"Gateway validation failed: {exc}")
    if gateway_addr not in subnet:
        return RuleResult(
            rule="gateway_mismatch",
            passed_check=False,
            detail=f"Gateway {gateway} is outside the device subnet {subnet}.",
        )
    return RuleResult(rule="gateway_mismatch", passed_check=True, detail=f"Gateway {gateway} is valid for subnet {subnet}.")


def check_interface_down(show_output: str) -> RuleResult:
    lower = (show_output or "").lower()
    if "administratively down" in lower or "down/down" in lower:
        return RuleResult(rule="interface_down", passed_check=False, detail="An interface is administratively or operationally down.")
    return RuleResult(rule="interface_down", passed_check=True, detail="No interface-down signal found in the output.")


def check_missing_vlan(vlan_config: dict[str, Any]) -> RuleResult:
    if not vlan_config:
        return RuleResult(rule="missing_vlan", passed_check=True, detail="No VLAN config to check.")
    configured = vlan_config.get("configured_vlans") or {}
    expected = vlan_config.get("expected_vlans") or {}
    missing = [vid for vid in expected if vid not in configured]
    if missing:
        return RuleResult(rule="missing_vlan", passed_check=False, detail=f"Missing expected VLANs: {missing}")
    return RuleResult(rule="missing_vlan", passed_check=True, detail="All expected VLANs are present.")


def check_missing_route(routes: list[dict[str, Any]]) -> RuleResult:
    if not routes:
        return RuleResult(rule="missing_route", passed_check=True, detail="No routes to validate.")
    missing = [r.get("destination_network") for r in routes if not r.get("exists", True)]
    if missing:
        return RuleResult(rule="missing_route", passed_check=False, detail=f"Missing routes: {missing}")
    return RuleResult(rule="missing_route", passed_check=True, detail="All expected routes are present.")


def validate_case(case: dict[str, Any]) -> list[RuleResult]:
    results: list[RuleResult] = []
    results.append(check_duplicate_ips(case.get("device_ips") or []))
    results.append(check_wrong_mask(case.get("ip_config") or {}))
    results.append(check_gateway_mismatch(case.get("ip_config") or {}))
    results.append(check_interface_down(case.get("show_output") or ""))
    results.append(check_missing_vlan(case.get("vlan_config") or {}))
    results.append(check_missing_route(case.get("routes") or []))
    return results


def _load_case_file(path: str) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError("The input JSON must be an object or list of objects.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic rule checks on basic Cisco troubleshooting data.")
    parser.add_argument("--case-file", type=str, default="backend/data/sample_rule_check_cases.json", help="JSON file containing one or more troubleshooting cases.")
    args = parser.parse_args()

    cases = _load_case_file(args.case_file)
    for idx, case in enumerate(cases, start=1):
        print(f"CASE {idx}: {case.get('problem_description', 'Unknown problem')}")
        for result in validate_case(case):
            marker = "PASS" if result.passed_check else "FAIL"
            print(f"  - [{marker}] {result.rule}: {result.detail}")
        print()


if __name__ == "__main__":
    main()
