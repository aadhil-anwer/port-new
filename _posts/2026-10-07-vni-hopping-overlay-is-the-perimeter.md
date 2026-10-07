---
title: "VNI Hopping: VLAN Hopping Grew Up and Moved to the Data Center"
description: "VXLAN and Geneve rebuilt the VLAN as a 24-bit tag inside a UDP packet with no authentication by design. One packet to UDP/4789 on a VTEP injects a frame into any tenant you name."
date: 2026-10-07
tags: [infrasec, network-security, vxlan, geneve, overlay, cloud]
type: blog
---

L2 adjacency isn't a security boundary. Nowhere does ignoring that cost more than in the overlays every data center and Kubernetes cluster now runs on. VXLAN and Geneve took the VLAN, stretched the tag to 24 bits, and wrapped it in UDP so it rides any L3 fabric. They kept every trust assumption of 802.1Q and added one: that nobody untrusted can put a packet on the transport. On a flat fabric, a shared hypervisor, or a cloud VPC, that's often false - and when it's false, the hop is cleaner than any 802.1Q trick.

## VXLAN on the wire

A VXLAN frame is a whole Ethernet frame tunneled in UDP:

```
+-------------------------------------------------------------+
| Outer Eth | Outer IP | Outer UDP | VXLAN hdr | Inner Eth... |
+-------------------------------------------------------------+
                          dst=4789        |
                   +-------------------------------------+
                   | Flags(8) | Reserved(24)             |
                   | VNI (24 bits)        | Reserved(8)  |
```

The **VNI** is the tenant tag - the VLAN ID's successor, now 24 bits (~16.7M segments). UDP dst 4789. The inner frame gets delivered into that VNI as if it arrived natively.

RFC 7348's own security section is blunt: **no authentication, no encryption.** It leans on the transport being trusted and "traditional layer 2 security" keeping rogue endpoints off the VTEPs. Geneve (RFC 8926, UDP/6081) adds variable TLV options and the same posture - a receiver can't verify a TLV came from a legitimate sender. The tag got 2048x bigger and lost the one thing a trunk port at least nominally had: a physical boundary.

## The attack is one UDP packet

Decapsulation is unauthenticated, so the whole attack is: send a datagram to 4789 on a VTEP, set the VNI, put your Ethernet frame inside. The VTEP strips the outer headers and injects your frame into that tenant, indistinguishable from a real workload's. That's the TROOPERS 2019 VXLAN result in one line - no checks, no auth, wrapped frames decapsulated straight into the internal network.

Three capabilities fall out of that one primitive.

**Cross-tenant injection.** Any host that reaches UDP/4789 on a VTEP injects a frame into any VNI it names. On a shared hypervisor or flat management fabric, a compromised workload hits the host's VTEP and crosses into a neighbor's overlay - exactly what the overlay was sold to prevent. No tag-strip trick, no one-way limit like double tagging. Full frame into the segment.

**VNI enumeration.** 24 bits sounds large until you probe it at line rate. Sweep VNIs, watch for ICMP unreachables, timing deltas, or FDB-driven responses, and you map the live tenant segments on a VTEP. Full scan of the space finishes in minutes. The width sold as scalability is a recon surface.

**VTEP source spoofing.** VTEPs learn inner-MAC to remote-VTEP-IP from the data plane - from the outer source IP. Forge the outer source to match a real VTEP and the receiver binds your chosen inner MAC to that source, then tunnels future unicast for that MAC wherever you point it. ARP spoofing one layer down, against the overlay's own learning.

Same bug as 802.1Q: a device trusting a tag it never verifies. Bigger tag, routed transport, blast radius in tenants instead of ports. The Docker Swarm advisory GHSA-vwm3-crmr-xfxw is the mundane version - expose 4789 at a perimeter and the overlay is an internet-facing injection endpoint.

## What holds

No `tag native` equivalent here - the protocol has no field to authenticate, so you can't config the tag trust away. Everything is about restoring the boundary the encapsulation threw out.

- **Underlay ports are the real boundary.** Infra ACLs: UDP/4789 and /6081 only from known VTEP source IPs, default drop, enforced on the physical interface before the VXLAN stack sees the packet. Highest-value control, most often missing.
- **Never expose 4789/6081 at a perimeter**, encrypted or not. A firewall taking overlay ports from untrusted space is an unauthenticated frame-injection API.
- **Authenticate the transport.** MACsec on underlay links, IPsec around the UDP (ESP transport mode keeps the outer IP for ECMP/offload), or WireGuard-mode encryption like Cilium does - authenticated encryption, no unauthenticated decap path left.
- **Kill data-plane learning.** FDB from a control plane (EVPN/BGP) or static with `nolearning`, so a spoofed outer source has nothing to poison. Removes the third capability outright.
- **uRPF and anti-spoofing** so forged outer source IPs die at the first hop.

Every isolation primitive that carries tenancy in an unauthenticated tag is the same bet: secure only while no untrusted party can reach the device honoring the tag. Overlays widened the tag, routed it across the data center, and raised the stakes from a VLAN to a tenant. Put the auth and the ACLs on the transport. The tag was never going to carry it.

## Sources

- [RFC 7348 - VXLAN](https://datatracker.ietf.org/doc/html/rfc7348) (Section 6, Security Considerations)
- [RFC 8926 - Geneve](https://datatracker.ietf.org/doc/html/rfc8926)
- [TROOPERS19 - VXLAN Security / Injection (ERNW)](https://troopers.de/downloads/troopers19/TROOPERS19_AR_VXLAN_Security.pdf)
- [VXLAN and Geneve Overlay Network Security](https://www.systemshardening.com/articles/network/vxlan-geneve-overlay-security/)
- [Docker moby advisory GHSA-vwm3-crmr-xfxw](https://github.com/moby/moby/security/advisories/GHSA-vwm3-crmr-xfxw)
