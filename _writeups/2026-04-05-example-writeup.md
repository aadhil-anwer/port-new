---
title: "Example CTF Writeup — Web Challenge"
description: "Walkthrough of a web exploitation challenge involving IDOR and privilege escalation."
date: 2026-04-05
tags: [ctf, web, idor]
type: writeup
---

## Challenge Overview

- **Name:** Broken Access
- **Category:** Web
- **Difficulty:** Medium
- **Points:** 300

## Reconnaissance

The application is a simple user dashboard. After creating an account, I noticed the profile endpoint:

```
GET /api/user/profile?id=1042
```

The `id` parameter is a sequential integer. Classic IDOR surface.

## Exploitation

Changing the `id` to `1` returned the admin user's profile, including their API key:

```json
{
  "id": 1,
  "username": "admin",
  "role": "admin",
  "api_key": "flag{br0k3n_4cc3ss_c0ntr0l}"
}
```

No authorization check on the endpoint — the server only validates that the session is authenticated, not that the user owns the requested resource.

## Remediation

The fix is straightforward: validate that `request.user.id == params.id` before returning the data, or scope queries to the authenticated user's session.

## Takeaway

Always test for horizontal privilege escalation. Sequential IDs are a red flag, but even UUIDs aren't safe if the authorization logic is missing.
