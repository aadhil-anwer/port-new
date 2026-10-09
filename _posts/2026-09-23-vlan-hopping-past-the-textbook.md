---
title: "VLAN Hopping Past the Textbook: Parser Confusion at Layer 2"
description: "Switch spoofing and double tagging are the boring ones. The VLAN hops that still work bypass DAI, RA Guard, and DHCP snooping by making the switch and the host disagree about the same frame."
date: 2026-09-23
tags: [infrasec, network-security, layer2, vlan, 802.1Q]
type: blog
---

Every VLAN hopping writeup stops at the same two attacks, and both have been dead for a decade if you spent ten seconds on the config. Switch spoofing dies to one command. Double tagging dies to another. People memorize them for the exam and move on believing VLANs are a boundary.

They're not. The hops that still land don't touch forwarding at all. They break the parser.

## The tag

Everything here is a fight over one 4-byte structure, so start there. The 802.1Q tag sits right after the source MAC:

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

**TPID** says "a tag follows" - 0x8100 for 802.1Q, 0x88a8 for QinQ. **VID** is the 12-bit VLAN. Here's the part that matters: nothing in the tag says how many tags come after it. A parser keeps reading as long as it keeps seeing a TPID it recognizes, and *where it decides to stop is an implementation choice, not a rule.* That one gap is the whole attack surface.

## The two everyone cites

**Switch spoofing.** A port left on `dynamic auto` will form a trunk if you ask it to. Send DTP, become a trunk, get every VLAN:

```bash
modprobe 8021q
ip link add link eth0 name eth0.20 type vlan id 20
ip addr add 10.0.20.66/24 dev eth0.20 && ip link set eth0.20 up
```

Gone the second someone types `switchport mode access` and `switchport nonegotiate`.

**Double tagging.** Native VLAN crosses a trunk untagged. If your access VLAN is the trunk's native, you stack two tags and let the first switch peel one off for you:

```
You send:    [ outer VID=1 ][ inner VID=20 ][ IP ... ]
Switch A:    native VLAN 1 egresses untagged -> strips outer tag
On trunk:    [ inner VID=20 ][ IP ... ]
Switch B:    delivers to VLAN 20
```

One direction only. There's no tag path back, so it's injection, never a session. Gone the moment the native VLAN is a dedicated unused ID, or `vlan dot1q tag native` is set.

If this were the whole story we could stop. It isn't, because both of these are *forwarding* tricks. The interesting bugs are in *parsing*.

## Where it actually breaks

Etienne Champetier dropped this one in 2021 - **VU#855201**, four CVEs (27853, 27854, 27861, 27862), confirmed on Cisco, Arista and Juniper. Calling it a product bug undersells it. It's a flaw in the whole idea of inspecting L2 for security.

Think about what DAI, RA Guard, IP Source Guard and DHCP snooping actually do. Each one parses the frame, finds the L3 header, reads a field, and decides to drop. That's only sound if the switch parses the frame **exactly the way the destination host will.** The second they disagree, the switch inspects one set of bytes while the host acts on another, and the "security control" is inspecting a frame that was never on the wire.

Two cheap ways to force that disagreement.

### VLAN 0

A tag with VID 0 is completely legal. It's a *priority tag* - carries an 802.1p class, claims no VLAN membership, and the host is supposed to treat the frame as belonging to the port's native VLAN and keep parsing inward. Host stacks honor it. Plenty of switch security engines don't expect it sitting in front of a real tag, so they either quit inspecting or read the L3 header from the wrong offset.

```
[ TPID 0x8100 | VID=0 ][ TPID 0x8100 | VID=20 ][ IPv6 RA ... ]
       priority tag            target VLAN
```

The host unwinds both and processes a Router Advertisement in VLAN 20. RA Guard looked, saw a priority tag and something it couldn't classify as an RA, and waved it through. You just put a rogue default router into the exact segment RA Guard was deployed to protect.

### LLC and SNAP

This one's older and dirtier. Two framing modes are live on every switch you own. **Ethernet II**: the field after the MAC header is an EtherType (0x0600 and up). **802.3**: that same field is a *length* (1500 and under), and the real protocol gets named inside an 802.2 LLC header, optionally a SNAP block - `AA AA 03 <OUI> <EtherType>`.

Same protocol, two completely different frames, real EtherType buried at a different offset. An engine that only speaks Ethernet II reads the length field, finds nothing that looks like an EtherType, and never sees the IPv6 or ARP it was told to filter. The host speaks 802.2/SNAP and decodes it without blinking.

```
[ VID=0 ][ len=0x00?? ][ AA AA 03 | OUI 000000 | 0x86DD ][ IPv6 RA ... ]
            802.3 length    LLC      SNAP        real EtherType
```

CVE-2021-27861 pushes it further with an *invalid* LLC length. Make the declared length and the true offset disagree and the length-trusting parser walks straight to the wrong byte while the host reassembles fine. VLAN 0 plus LLC/SNAP is 27853. Run it across an Ethernet-to-WiFi bridge - an AP translating 802.3 to 802.11, yet another parser with its own assumptions - and you're at 27854 and 27862.

Strip away the specifics and it's one move: **you don't beat the rule, you blind the decoder.** The rule never fires because the engine is reading bytes that mean something different to it than to the victim. It's request smuggling, one layer down. And like smuggling, it generalizes - any two parsers in a path that disagree on where a frame ends, the stricter one loses.

## Voice VLAN still works

One of the old attacks never died, because it leans on neither DTP nor the native VLAN. An "access + voice" port runs untagged data for the workstation and a tagged voice VLAN for the phone, and it hands the phone that voice VLAN ID over CDP or LLDP-MED with nothing checking whether you're actually a phone.

So be a phone:

1. Listen for CDP/LLDP-MED, or send a spoofed Network Policy TLV claiming to be an IP phone.
2. Read the VVID out of the reply.
3. Bring up a subinterface on the VVID and DHCP into the voice subnet.

VoIP Hopper does all of this for Cisco, Avaya, Alcatel and Nortel. Trunking can be off - the voice VLAN is a separate feature, and the port is *built* to accept one tagged VLAN. Shut it down with 802.1X, kill CDP/LLDP toward hosts, and don't hand a voice VLAN to ports that have no phone on them.

## What actually holds

The old attacks need config. The new ones need patches.

- **Forwarding tricks:** `access` + `nonegotiate`, a dedicated native VLAN, `vlan dot1q tag native`. Table stakes, assume they're already done.
- **Parser tricks:** patch for VU#855201. You can't config a decoder bug away. Where patching lags, stop trusting adjacency - push auth down to 802.1X/MACsec so an unauthenticated port's frame never reaches the segment in the first place.
- **Voice VLAN:** 802.1X and no discovery protocols facing endpoints.

The thing worth keeping: DAI, RA Guard and DHCP snooping are not access controls. They're parsers with an opinion, inspecting the frame they *think* is on the wire. The frame that's actually on the wire is whatever the host's decoder will accept, and that set is always bigger than what your switch models. Stacked tags, VID 0 and LLC/SNAP are just the three cheapest ways to pry the two apart. Treat L2 inspection as hardening. Never as a wall.
