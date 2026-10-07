---
title: "VLAN Hopping Past the Textbook: Parser Confusion at Layer 2"
description: "Switch spoofing and double tagging are the boring ones. The VLAN hops that still work bypass DAI, RA Guard, and DHCP snooping by making the switch and the host parse the same frame differently."
date: 2026-10-08
tags: [infrasec, network-security, layer2, vlan, 802.1Q]
type: blog
---

Everyone cites switch spoofing and double tagging. Both are 20 years old, both die to one line of config, and both attack *forwarding* logic. The hops that still land attack *parsing* logic - the gap between how a switch's security engine reads a frame and how the destination NIC reads the same frame. When those disagree, DAI, DHCP snooping, RA Guard, and IP Source Guard all pass traffic they were deployed to drop.

## The tag

One 4-byte structure drives every attack here. The 802.1Q tag, inserted after the source MAC:

```
 6 bytes   6 bytes    4 bytes          2 bytes
+--------+--------+--------------+--------------+----------
|  DMAC  |  SMAC  | 802.1Q TAG   |  EtherType   | payload
+--------+--------+--------------+--------------+----------
                        |
          +-------------------------------+
          | TPID = 0x8100 |      TCI      |
          +-------------------------------+
                          | PCP | DEI |  VID (12 bits)  |
```

**TPID** (0x8100 for 802.1Q, 0x88a8 for QinQ) tells a parser a tag follows. **VID** is the 12-bit VLAN. Nothing in the tag says *how many tags follow* - a parser keeps reading as long as it sees a TPID it knows, and where it stops is an implementation choice. That choice is the attack surface.

## The two you already know

**Switch spoofing** abuses DTP. A port on `dynamic auto` negotiates a trunk if you ask. Send DTP, become a trunk, receive every VLAN:

```bash
modprobe 8021q
ip link add link eth0 name eth0.20 type vlan id 20
ip addr add 10.0.20.66/24 dev eth0.20 && ip link set eth0.20 up
```

Killed by `switchport mode access` + `nonegotiate`.

**Double tagging** abuses the native VLAN, which crosses a trunk untagged. If your access VLAN equals the trunk native, stack two tags:

```
Send:        [ outer VID=1 ][ inner VID=20 ][ IP ... ]
Switch A:    native VLAN 1 egresses untagged -> strips outer tag
On trunk:    [ inner VID=20 ][ IP ... ]
Switch B:    delivers to VLAN 20
```

Strictly one-way - no return tag path, so it's injection, not a session. Killed by a dedicated unused native VLAN, or `vlan dot1q tag native`.

Both are table stakes. If that were the whole attack surface, VLAN hopping would be solved. It isn't.

## The real class: parser differential

Etienne Champetier reported this in 2021 as **VU#855201** - **CVE-2021-27853/27854/27861/27862**, confirmed on Cisco, Arista, and Juniper. Not really a product bug. A design flaw in how L2 inspection was ever supposed to work.

DAI, RA Guard, IP Source Guard, DHCP snooping all do the same thing: parse the frame, find the L3 header, read a field, decide to drop. Sound only if the switch parses the frame **exactly** how the host will. Make them disagree and the switch inspects the wrong bytes while the host acts on bytes that were never inspected. Two primitives force the disagreement.

### VLAN 0 tags

A VID-0 tag is legal. Per 802.1Q it's a *priority tag* - carries PCP, asserts no VLAN membership, host treats the frame as the port's native VLAN and keeps parsing inward. The host stack honors it. Plenty of switch security engines don't expect it stacked ahead of a real tag and either stop inspecting or mis-locate the L3 header.

```
[ TPID 0x8100 | VID=0 ][ TPID 0x8100 | VID=20 ][ IPv6 RA ... ]
       priority tag            target VLAN
```

Host unwinds both tags, processes the RA in VLAN 20. RA Guard saw a priority tag and a structure it didn't classify as an RA, and passed it. Rogue default router, straight into the segment RA Guard existed to protect.

### LLC/SNAP re-encapsulation

Two framing modes are live on every switch. **Ethernet II**: the field after the MAC header is an EtherType (>= 0x0600). **802.3**: that same field is a *length* (<= 1500), and the real protocol is named inside an 802.2 LLC header, optionally SNAP: `AA AA 03 <OUI> <EtherType>`.

Same protocol, two wire formats, real EtherType buried at a different offset. An engine that only models Ethernet II reads the length field, finds no EtherType, and never sees the IPv6 or ARP it filters. The host does 802.2/SNAP and decodes it fine.

```
[ VID=0 ][ len=0x00?? ][ AA AA 03 | OUI 000000 | 0x86DD ][ IPv6 RA ... ]
            802.3 length    LLC      SNAP        real EtherType
```

**CVE-2021-27861** adds an *invalid* LLC length - get the declared length and the real offset to disagree, and the length-trusting parser walks to the wrong byte while the host reassembles correctly. VLAN 0 + LLC/SNAP is **-27853**. Across an Ethernet-to-WiFi translation boundary (an AP bridging 802.3 to 802.11, another parser with its own assumptions) it's **-27854** and **-27862**.

One idea underneath all of it: **you don't defeat the rule, you blind the decoder.** The rule never matches because the engine is reading bytes that mean something different to it than to the victim. L2 request smuggling. It generalizes the same way - any two parsers in a path that disagree on frame boundaries, the stricter one gets blinded.

## Voice VLAN, still alive

One classic-era hop never died, because it needs neither DTP nor the native VLAN. An "access + voice" port runs untagged data for the workstation and a tagged voice VLAN for the phone, and the VVID is handed over CDP or LLDP-MED with nothing authenticating the phone.

Impersonate the phone, get told the VVID, tag into it:

1. Sniff CDP/LLDP-MED, or send a spoofed Network Policy TLV claiming to be an IP phone.
2. Read the VVID from the reply.
3. Bring up a subinterface on the VVID, DHCP into the voice subnet.

VoIP Hopper automates this across Cisco, Avaya, Alcatel, Nortel. Works with trunking fully off - voice VLAN is a separate feature, the port is deliberately willing to take one tagged VLAN. Kill it with 802.1X, drop CDP/LLDP toward hosts, and don't provision voice on ports with no phones.

## What holds

- **Forwarding-era (spoofing, double tagging):** `access` + `nonegotiate`, dedicated native VLAN, `vlan dot1q tag native`.
- **Parser-era (VLAN 0 / LLC / SNAP):** patch per VU#855201. Not configurable away - it's a decoder fix. Where patching lags, push auth down to 802.1X/MACsec so an unauthenticated port's frame never reaches the segment.
- **Voice VLAN:** 802.1X, no discovery protocols toward endpoints.

DAI, RA Guard, and DHCP snooping aren't access controls. They're parsers with an opinion, inspecting the frame they think is on the wire. The frame on the wire is whatever the host's decoder accepts, and that set is bigger than what the switch models. Stacked tags, VID 0, and LLC/SNAP are just the three cheapest ways to split the two. Treat L2 inspection as hardening, never a boundary.

## Sources

- [VU#855201 - L2 network security controls can be bypassed using VLAN 0 stacking and/or 802.3 headers](https://www.kb.cert.org/vuls/id/855201)
- [Cisco Security Advisory: Vulnerabilities in Layer 2 Network Security Controls (VU855201)](https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-VU855201-J3z8CKTX)
- [CVE-2021-27853](https://www.cvedetails.com/cve/CVE-2021-27853/), [CVE-2021-27861](https://www.cvedetails.com/cve/CVE-2021-27861/), [CVE-2021-27854](https://cve.report/CVE-2021-27854)
- [IEEE 802.1ad (QinQ)](https://en.wikipedia.org/wiki/IEEE_802.1ad)
- [VoIP Hopper](https://voiphopper.sourceforge.net/features.html), [CDP spoofing](https://en.wikipedia.org/wiki/CDP_spoofing)
