---
title: "Hello World — Why I'm Starting This Blog"
description: "First post. Why I'm writing, what to expect, and what I'm working on."
date: 2026-04-05
tags: [meta, security]
type: blog
---

## Why write?

I've spent the last few years breaking things, building things, and learning more than I thought possible about how systems actually work under the hood. But I've mostly kept that knowledge in my head or scattered across private notes.

This blog is where I'll start sharing it.

## What to expect

- **Security research** — vulnerability analysis, exploitation techniques, defense strategies
- **Networking deep dives** — packet-level analysis, protocol internals, infrastructure design
- **Tool breakdowns** — how I use Wireshark, Burp Suite, Splunk, and other tools in real workflows
- **CTF walkthroughs** — detailed writeups from competitions
- **Systems thinking** — how things fail, and how to design them so they don't

## The format

Posts will be technical but readable. I'll include code, packet captures, and diagrams where they help. No fluff — just the interesting parts.

```python
# like this
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("target.local", 80))
s.send(b"GET / HTTP/1.1\r\nHost: target.local\r\n\r\n")
print(s.recv(4096).decode())
```

Let's go.
