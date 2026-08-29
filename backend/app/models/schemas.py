"""Pydantic request/response models for the NetSage AI API."""

from typing import Optional
from pydantic import BaseModel, Field


class VlanConfig(BaseModel):
    device: str
    configured_vlans: dict[int, str] = Field(
        default_factory=dict, description="VLAN ID -> name, as currently configured"
    )
    expected_vlans: dict[int, str] = Field(
        default_factory=dict, description="VLAN ID -> name, as it should be"
    )
    trunk_allowed_vlans: list[int] = Field(default_factory=list)


class DeviceIpConfig(BaseModel):
    device: str
    ip_address: str
    subnet_mask: str = "255.255.255.0"
    gateway: str


class RouteEntry(BaseModel):
    destination_network: str
    next_hop: Optional[str] = None
    exists: bool = True


class AclRule(BaseModel):
    action: str  # "PERMIT" or "DENY"
    source: str
    destination: str


class TroubleshootRequest(BaseModel):
    """Top-level request: user complaint + whatever supporting data they have."""

    problem_description: str
    vlan_config: Optional[VlanConfig] = None
    ip_config: Optional[DeviceIpConfig] = None
    routes: Optional[list[RouteEntry]] = None
    acl_rules: Optional[list[AclRule]] = None
    raw_logs: Optional[str] = None


class Diagnosis(BaseModel):
    issue: str
    affected_layer: str
    root_cause: str
    confidence: float  # 0-100
    recommended_fix: str
    verification_steps: list[str]
    source_snippets: list[str] = Field(
        default_factory=list, description="Knowledge base chunks used for grounding"
    )


class FeedbackRequest(BaseModel):
    diagnosis_id: str
    problem_description: str
    ai_prediction_summary: str
    confidence: float
    verdict: str  # "Correct" | "Partially Correct" | "Wrong"
