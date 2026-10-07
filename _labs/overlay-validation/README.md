# Linux VXLAN and VLAN lab — 8 October 2026 (IST)

## Scope and topology

Executed against Linux `7.0.0-34-generic`, iproute2 `6.1.0`, nftables `1.0.9`, Python `3.12.3`.
The final run's machine timestamp is `2026-10-07T19:18:09Z` (8 October, 00:48 IST).

Two disposable network namespaces share a veth pair:

```text
sender namespace                         receiver namespace
192.0.2.2/24 --- veth ------------------- 192.0.2.1/24
raw Ethernet / UDP sender                 |-- vx5000: VNI 5000, UDP 4789
                                          |-- vlan20: VLAN ID 20
```

Neither namespace has a default route or a connection to a physical interface.
The script first creates a user/network namespace and verifies it differs from the caller's network namespace. All interface and firewall changes happen there. The child namespace process is terminated in cleanup; remaining namespace resources disappear when the script exits. No Docker containers or cloud resources were created.

## Observations

Each case sends one uniquely marked frame. AF_PACKET sockets capture on the underlay, VXLAN interface, and VLAN interface, with a 400 ms observation window. All eleven markers appeared on the underlay.

| Case | Markers at target interface | Interpretation |
|---|---:|---|
| VNI 5000, no source filter | 1 | Configured VXLAN endpoint accepted the injected frame |
| VNI 5001, not configured | 0 | No delivery to the configured VXLAN interface |
| VNI 5000, source blocked by nftables | 0 | Filter prevented observed decapsulation; counter recorded one dropped packet |
| Same VNI after removing filter | 1 | Delivery resumed |
| VNI 5000 with `nolearning`, new inner source MAC | 1 | Injection still worked; new MAC was absent from FDB |
| VLAN 20 | 1 | Positive control reached vlan20 |
| VLAN 30 | 0 | Wrong VLAN did not reach vlan20 |
| VLAN 0 only | 0 | Priority tag alone did not select VLAN 20 |
| Untagged | 0 | Untagged traffic did not reach vlan20 |
| VLAN 0 followed by VLAN 20 | 1 | Linux processed the stack and delivered to vlan20 |
| VLAN 0 followed by VLAN 30 | 0 | Wrong inner VLAN did not reach vlan20 |

With learning enabled, the FDB acquired `02:00:00:00:00:02 dst 192.0.2.2`. With learning disabled, a frame with inner source `02:00:00:00:00:03` was still received, but that MAC was not learned. This tests learning of a crafted inner source, not spoofing of the outer IP or successful traffic redirection.

## Unexpected result and rerun

The first complete run expected stacked 0/20 tags not to reach vlan20. They did. That run, including its failed expectation, remains in `results-initial/`. The script was then updated to reflect the observation and add untagged and 0/30 controls. The confirming run is in `results/`. Passing assertions mean the observations match the updated expectations; they do not mean a product passed a security certification.

Earlier setup attempts stopped on a firewall syntax error and a namespace-unaware sysfs lookup. Those harness issues were fixed before the complete runs. They are not network-security findings.

## Evidence and reproduction

- `run.py`: complete harness; requires Linux, unshare, nsenter, ip, bridge, nft, Python 3, and permitted unprivileged user namespaces.
- `results/results.json`: environment, interface configuration, firewall counter, per-case observations and FDB snapshots.
- `results/commands.json`: commands and output, including exact transmitted packet bytes.
- `results/{underlay,vx5000,vlan20}.pcap`: interface captures; independently decoded with tcpdump.
- `results-initial/`: first complete run and original failed expectation.

Run `python3 _labs/overlay-validation/run.py` from the repository root. It overwrites `results/`, so copy that directory first if preserving another run. No sudo is required where user namespaces are permitted. Do not bypass local namespace restrictions merely to run this script.

Captures use userspace receipt timestamps. Linux VLAN acceleration may remove tags from the bytes delivered to AF_PACKET; this harness does not reconstruct auxiliary VLAN metadata. Use the sender's recorded frame bytes to establish intended tag stacks, and the target-interface marker to establish delivery. Synthetic frames use experimental EtherType 0x88b5 and may be shorter than a physical Ethernet minimum: these are virtual-interface tests, not wire-equivalence tests.

## What this does not establish

No physical switch, vendor image, switch access-port policy, RA Guard, DHCP snooping, DAI, or LLC/SNAP filter was tested. The VLAN result is ordinary receive-path behavior in this topology, not reproduction of VU#855201 and not evidence of crossing an enforced VLAN boundary.

No Geneve, Docker Swarm, IPsec, WireGuard, EVPN, cross-tenant application connection, return path, MAC redirection, scan speed, or hardware offload behavior was tested. A received synthetic frame proves interface delivery, not application acceptance. Negative cases mean no matching packet within the observation window; positive controls and the firewall counter strengthen those observations but do not prove all possible traffic is blocked.
