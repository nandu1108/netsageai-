# Responsible AI Review Log

This log records the cases where the AI diagnosis was corrected by a human reviewer. The log includes at least five examples to demonstrate human oversight and accountability.

## 1. CASE-003 — VLAN missing on trunk
- AI diagnosis: "Missing VLAN 20 on the access switch"
- Human correction: The AI identified the symptom but missed that the trunk on the distribution switch was also blocking VLAN 20.
- Why corrected: The evidence showed `show interfaces trunk` allowed VLANs 10,30 only, and the switchport on the server VLAN was missing the route summary.
- Final verdict: Edited

## 2. CASE-009 — Wrong default gateway
- AI diagnosis: "DHCP lease issue"
- Human correction: The evidence showed the PC had a valid DHCP address but was assigned the wrong gateway in a different subnet.
- Why corrected: `show ip interface brief` and `ping 192.168.30.1` failed immediately because the gateway was not in the same subnet as the client.
- Final verdict: Rejected and replaced with a Layer 3 gateway mismatch diagnosis.

## 3. CASE-014 — ACL deny rule on the wrong direction
- AI diagnosis: "ACL deny on server access"
- Human correction: The AI identified an ACL issue but recommended the wrong direction and missed the implicit deny on the return path.
- Why corrected: The evidence showed the deny was applied inbound on the LAN interface, and the return traffic was blocked by the same ACL.
- Final verdict: Edited

## 4. CASE-020 — OSPF adjacency down
- AI diagnosis: "IP mismatch"
- Human correction: The AI focused on IP mismatch while the actual fault was an OSPF neighbor down caused by a passive-interface and missing network statement.
- Why corrected: The evidence showed the interfaces were in the same subnet but the OSPF neighbor table was empty.
- Final verdict: Edited

## 5. CASE-027 — NAT overload misconfigured
- AI diagnosis: "ACL filter issue"
- Human correction: The AI missed the fact that the outside interface was not configured with the correct NAT overload pool.
- Why corrected: `show ip nat translations` had no translations; the unsupported pool or missing `ip nat inside source list` rule was the true cause.
- Final verdict: Edited

## 6. CASE-031 — Wireless guest isolation misapplied
- AI diagnosis: "Basic DHCP issue"
- Human correction: The guest users were receiving an address and could ping each other, but the real issue was a guest isolation policy violation.
- Why corrected: The evidence showed that the guest VLAN was incorrectly mapped to the corporate SSID and the security policy allowed internal hosts.
- Final verdict: Rejected
