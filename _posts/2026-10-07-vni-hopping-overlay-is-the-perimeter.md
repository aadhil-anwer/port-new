---
title: "VNI Hopping: VLAN Hopping Grew Up and Moved to the Data Center"
description: "VXLAN and Geneve rebuilt the VLAN as a 24-bit tag inside a UDP packet with no authentication by design. One packet to UDP/4789 on a VTEP drops a frame into any tenant you name."
date: 2026-10-07
tags: [infrasec, network-security, vxlan, geneve, overlay, cloud]
type: blog
---

Last post I said L2 adjacency isn't a security boundary. The place that bites hardest is the overlay - the thing every data center and Kubernetes cluster runs on now.

VXLAN and Geneve took the VLAN, stretched the tag to 24 bits, and wrapped it in UDP so it rides over any L3 fabric. In the process they kept every trust assumption 802.1Q ever made and quietly added one more: that nobody untrusted can land a packet on the transport. On a flat fabric, a shared hypervisor, or a cloud VPC, that assumption is wrong all the time. And when it's wrong, the hop is cleaner than anything you can pull off with 802.1Q.

## What's on the wire

A VXLAN frame is a whole Ethernet frame stuffed inside UDP:

```
+-------------------------------------------------------------+
| Outer Eth | Outer IP | Outer UDP | VXLAN hdr | Inner Eth... |
+-------------------------------------------------------------+
                          dst=4789        |
                   +-------------------------------------+
                   | Flags(8) | Reserved(24)             |
                   | VNI (24 bits)        | Reserved(8)  |
```

The **VNI** is the tenant tag - the VLAN ID's replacement, now 24 bits, so roughly 16.7 million segments instead of 4094. Destination UDP port 4789. Whatever Ethernet frame is inside gets dropped into that VNI like it showed up natively.

Read RFC 7348's security section and it just tells you: **no authentication, no encryption.** The design leans entirely on the transport being trusted and on "traditional layer 2 security" keeping rogue hosts off the VTEPs. Geneve (RFC 8926, UDP/6081) adds variable TLV options and the same shrug - a receiver can't tell whether a TLV came from a real sender or an attacker. The tag got 2048 times bigger and lost the one thing a trunk port at least pretended to have: a physical edge.

## The attack is one UDP packet

Decap is unauthenticated, so that's the entire attack. Send a datagram to 4789 on a VTEP, pick your VNI, put an Ethernet frame inside. The VTEP strips the outer headers and injects your frame into that tenant, and it looks exactly like something a real workload sent. ERNW showed this at TROOPERS back in 2019 - no checks, no auth, wrapped frames decapsulated straight into the internal network.

Three things fall out of that one move.

**You cross tenants.** Anything that can get a packet to UDP/4789 on a VTEP can drop a frame into any VNI it names. On a shared hypervisor or a flat management fabric, a popped workload reaches the host's VTEP and steps into a neighbor's overlay - the one thing the overlay was sold to prevent. No tag-stripping dance, no one-way limit like double tagging. Full frame, right into the segment.

**You enumerate.** 24 bits sounds like a lot until you remember you can spray it at line rate. Sweep VNIs, watch for ICMP unreachables, timing differences, FDB reactions, and you've mapped which tenants live on that VTEP in a couple of minutes. The width they sold as scalability is a recon surface.

**You spoof the VTEP.** VTEPs learn inner-MAC to remote-VTEP-IP mappings from the data plane - from the outer source IP. Forge that outer source to match a real VTEP and the receiver happily binds your chosen inner MAC to it, then tunnels future traffic for that MAC wherever you aimed it. It's ARP spoofing again, one layer down, against the overlay's own learning.

Same bug as the last post, every time: a device trusting a tag it never bothered to verify. Just a wider tag, a routed transport, and a blast radius you measure in tenants instead of ports. The Docker Swarm advisory (GHSA-vwm3-crmr-xfxw) is the dumb version of this - leave 4789 exposed at the edge and your overlay becomes an injection API for the internet.

## What actually holds

There's no `tag native` move here. The protocol has no field to authenticate, so you can't config the trust back in. Everything is about rebuilding the edge the encapsulation threw away.

- **The underlay ports are the real boundary.** ACL them: 4789 and 6081 only from known VTEP source IPs, drop everything else, and do it on the physical interface before the VXLAN stack ever sees the packet. Highest-value control and the one people skip.
- **Never put 4789/6081 at a perimeter**, encrypted or not. A firewall that accepts overlay ports from untrusted space is handing out an unauthenticated frame-injection API.
- **Authenticate the transport.** MACsec on the underlay, IPsec around the UDP (ESP transport mode keeps the outer IP so you don't lose ECMP or offload), or go full WireGuard-mode like Cilium and leave no unauthenticated decap path at all.
- **Kill data-plane learning.** Drive the FDB from a control plane (EVPN/BGP) or pin it static with `nolearning`, and a spoofed outer source has nothing left to poison.
- **uRPF and anti-spoofing** so forged outer source IPs die at the first hop.

Every isolation primitive that carries tenancy in an unauthenticated tag is the same bet: safe exactly as long as nobody untrusted can reach the device that honors the tag. Overlays didn't fix that bet. They made the tag bigger, routed it across the whole data center, and moved the stakes from a VLAN to a tenant. Put the auth and the ACLs on the transport, because the tag was never going to carry it.
