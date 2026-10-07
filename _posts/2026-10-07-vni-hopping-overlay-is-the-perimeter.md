---
title: "Sending an Ethernet Frame Through a VXLAN Endpoint"
description: "A UDP packet reached a Linux VXLAN interface without peer authentication. Blocking the sender stopped it. Disabling MAC learning didn't."
date: 2026-10-07
tags: [infrasec, network-security, vxlan, geneve, overlay, cloud]
type: blog
---

## The Setup

I wanted to check what a VXLAN endpoint actually accepts from a sender outside the overlay.

Small setup. Two Linux network namespaces connected by a veth pair. No internet connection, no cloud account, no other workloads. The receiver had one VXLAN interface:

```text
Receiver: 192.0.2.1
Sender:   192.0.2.2
VNI:      5000
UDP port: 4789
```

The sender didn't even have a VXLAN interface. Just a UDP socket.

*Lab results added October 8, 2026. Kernel: `7.0.0-34-generic`.*

## The Packet

VXLAN carries an Ethernet frame inside UDP. The **VNI**, a 24-bit number in the VXLAN header, tells the receiver which overlay segment the frame belongs to.

```text
[ Outer IP ][ UDP ][ VXLAN header ][ Inner Ethernet frame ]
              |          |
            4789      VNI 5000
```

The test packet contained a synthetic Ethernet frame with a text marker. Nothing complicated inside it. Experimental EtherType `0x88b5`, a source MAC, and enough text to find it in the capture.

Sent it to `192.0.2.1:4789`.

**The inner frame appeared on `vx5000`.**

No peer-authentication step in this setup. The receiver accepted the encapsulated frame from the UDP sender.

That's consistent with [RFC 7348](https://www.rfc-editor.org/rfc/rfc7348.html#section-7): base VXLAN doesn't provide authentication or encryption. Those protections have to come from the deployment around it.

## Changing the VNI

Next packet: same receiver, same port, VNI changed to `5001`.

Nothing on `vx5000`.

The packet reached the underlay interface, but VNI 5001 wasn't configured. It wasn't delivered to the VNI 5000 interface.

This is where the claim in my earlier draft was too broad. Reaching UDP/4789 doesn't automatically put you into any tenant you name. The endpoint's configured VNIs and acceptance rules still matter. Also, a VNI identifies a segment; one tenant can have several.

## The Filter

Added an nftables rule blocking UDP/4789 from the sender's address. Sent another frame to VNI 5000.

```text
Underlay capture:  packet present
Firewall counter:  1 packet dropped
vx5000 capture:    no matching frame
```

Removed the rule. Sent again.

The frame came through.

That gave the test a working control: delivery stopped when the source was blocked and returned when the rule was removed.

## What About MAC Learning?

With learning enabled, the receiver had added the inner source MAC to its forwarding database:

```text
02:00:00:00:00:02 dst 192.0.2.2 self
```

Then learning was disabled with `nolearning`, and the next frame used a fresh source MAC: `02:00:00:00:00:03`.

The new MAC wasn't learned. **The frame still arrived.**

So `nolearning` did what it was supposed to do. It stopped that forwarding-table update. It didn't reject the injected frame. Those are separate controls, and treating one as a replacement for the other leaves the listener exposed.

Each case sent one marked frame with a 400 ms observation window. This was an interface-delivery test. There was no tenant application behind it, and no attempt to establish a return connection or redirect someone else's traffic.

## Where This Shows Up in Practice

Docker's [April 2023 Swarm advisory](https://github.com/moby/moby/security/advisories/GHSA-vwm3-crmr-xfxw) describes administrators potentially exposing the VXLAN port because the port documentation lacked sufficient warnings. An exposed listener can become an entry point for injected Ethernet frames.

The part worth reading twice is the encrypted-overlay case.

Swarm uses **IPsec ESP transport mode** for encrypted overlay traffic. That doesn't require opening raw UDP/4789 at the perimeter. Leaving the raw UDP path open can add exposure alongside the encrypted transport. The advisory explicitly warns against exposing it to untrusted traffic, even with an encrypted overlay.

The lab above didn't run Swarm or IPsec. It tested the simpler Linux receive path.

Geneve has a similar deployment concern, documented in [RFC 8926's security section](https://www.rfc-editor.org/rfc/rfc8926.html#section-6). It wasn't tested here either.

## The Fix

For this setup, blocking the sender before decapsulation worked. In an actual deployment, restrict tunnel traffic to the intended peers and check whether workloads can spoof those peers' source addresses.

If authenticated transport is required, test the raw, unauthenticated path too. It should fail. Keep the VNI mappings, MAC-learning configuration, and workload policies in the review, but don't stop there because the diagram shows separate segments.

The packet that matters is the one an unauthorized sender can actually get through.
