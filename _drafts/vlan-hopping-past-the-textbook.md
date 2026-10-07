---
title: "A VLAN 0 Tag Didn't Stop Linux From Reading the Next Tag"
description: "Stacked VLAN 0/20 tags reached a Linux VLAN 20 interface. The first test expected rejection. Here's the result, the controls, and why it wasn't a VLAN escape."
date: 2026-10-07
tags: [infrasec, network-security, layer2, vlan, 802.1Q]
type: blog
---

## The Test

The frame had two VLAN tags:

```text
[ VLAN 0 ][ VLAN 20 ][ payload ]
```

The receiver had a VLAN 20 subinterface. The first test expected the stacked frame not to reach it.

It did.

The marker was there in the capture, on `vlan20`, after the tags had been processed.

Before calling that a VLAN escape, though: the sender was connected directly to the receiver through a veth pair. No managed switch. No access-port restriction. No RA Guard. There was a configured VLAN interface, and Linux delivered a frame to it.

That's the result. The interesting part is what it tells us about parsing, and where the security claim needs more evidence.

*Lab results added October 8, 2026. Kernel: `7.0.0-34-generic`.*

## Checking It Again

The lab used two isolated network namespaces with no external route. Each packet carried a different text marker, so delivery could be checked without relying on a reply.

A plain VLAN 20 frame worked. VLAN 30 didn't reach the VLAN 20 interface. Neither did VLAN 0 alone.

The confirming run added untagged traffic and a stacked `0/30` frame:

```text
Tags sent           Seen on vlan20
20                  yes
30                  no
0                   no
untagged            no
0, then 20          yes
0, then 30          no
```

One frame per case, with a 400 ms capture window. The first run's failed expectation was kept alongside the confirming run and packet captures.

**The outer VLAN 0 tag didn't stop Linux from processing the inner VLAN 20 tag.** Changing that inner tag to 30 didn't deliver the marker to `vlan20`.

VLAN 0 is a *priority tag*. It carries priority information without specifying VLAN membership. It isn't a request to join a network called VLAN zero.

## Where the Tag Sits

An 802.1Q tag adds four bytes after the source MAC address:

```text
[ Destination MAC ][ Source MAC ][ TPID ][ TCI ][ EtherType ][ Payload ]
                                2 bytes  2 bytes
                                         |
                                  PCP | DEI | VID
                                   3     1    12 bits
```

The **VID** is the 12-bit VLAN ID. The switch's port configuration and forwarding behavior determine what happens to it. Sending a tag doesn't, by itself, establish that you've crossed a security boundary.

That distinction gets lost when every unusual tagged frame gets described as VLAN hopping.

## The Usual VLAN Hops

**Switch spoofing** depends on trunk negotiation. A Cisco port that permits DTP negotiation may let an endpoint establish a trunk and reach the VLANs allowed on it.

One mistake in my earlier draft: the Linux `ip link` command creates a VLAN subinterface. It doesn't send DTP. Preparing a host to use tagged traffic and persuading a switch to give it a trunk are different steps.

**Double tagging** relies on a forwarding path that removes the outer tag and leaves the inner one for another switch:

```text
Sent:          [ outer VID=1 ][ inner VID=20 ][ payload ]
After removal:               [ inner VID=20 ][ payload ]
Next switch: sees VLAN 20
```

The classic attack depends on native VLAN handling and the sender's access to that VLAN. It generally provides one-way injection, not a return path for a session.

Explicit access-port configuration, disabling negotiation where supported, and keeping endpoint traffic off the trunk's native VLAN address those conditions. Native VLAN tagging can also help where supported. The actual platform behavior still needs checking.

## The Inspection Bug

[CERT/CC VU#855201](https://www.kb.cert.org/vuls/id/855201/) describes a different problem. Reported by Etienne Champetier and published in September 2022, it covers Layer 2 inspection bypasses involving VLAN 0 and LLC/SNAP headers.

LLC/SNAP is another way of identifying the protocol inside an Ethernet frame. A vulnerable filter can fail to recognize traffic wrapped in those headers while the destination still processes it.

The advisory lists four CVEs:

- **CVE-2021-27853:** VLAN 0 and LLC/SNAP combinations.
- **CVE-2021-27854:** combinations involving Ethernet/Wi-Fi conversion.
- **CVE-2021-27861:** invalid LLC/SNAP lengths, optionally with VLAN 0.
- **CVE-2021-27862:** invalid lengths with Ethernet/Wi-Fi conversion.

A rogue Router Advertisement getting past RA Guard can affect a victim in its existing segment. It doesn't need to move the victim or attacker into another VLAN.

The Linux test above didn't have that filter. It didn't send LLC/SNAP traffic either. **It wasn't a reproduction of these CVEs.** It checked the receiving stack's handling of a particular tag sequence.

## What Still Needs Testing

To reproduce the inspection bypass, the next lab needs an affected implementation, its filtering policy, and captures before and after the device. A crafted frame reaching the receiver despite the blocking policy would establish the bypass. The software version matters; [Arista's advisory](https://www.arista.com/en/support/advisories-notices/security-advisory/16276-security-advisory-0080) and the vendor responses in the CERT note give the relevant scope.

Keep RA Guard, DHCP snooping, and ARP inspection enabled, and apply the relevant vendor fixes. Authentication through 802.1X doesn't repair their parsers; an authenticated endpoint can still be compromised.

Also check voice VLANs separately. A phone/workstation port can intentionally accept tagged voice traffic with trunk negotiation disabled.

For this run, the finding stays narrow: Linux accepted `0/20` for a configured VLAN 20 interface. The capture supports that. A claim that it defeated switch isolation would need a different lab.
