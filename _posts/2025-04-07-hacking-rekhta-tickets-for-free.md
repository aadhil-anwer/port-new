---
title: "Buying Rekhta Tickets Worth INR 1499 for Free"
description: "How I found a critical parameter tampering vulnerability in Jashn-e-Rekhta's payment flow — where the backend blindly trusted the frontend."
date: 2025-04-07
tags: [security, bug-bounty, web-security, parameter-tampering]
type: blog
---

## The Setup

I was sitting in yet another painful DevOps class — the kind where phrases like "pipelines" and "infrastructure" get thrown around so aggressively that your brain starts to dissociate. I needed something, *anything*, to keep myself from falling asleep.

That's when I stumbled upon **Jashn-e-Rekhta** — a massive 3-day Urdu/Hindi literary festival featuring names like Kailash Kher and Javed Akhtar. The kind of event you hear about and immediately know you *have* to be there.

The problem? Concert passes were priced at **INR 1499**. And as a student running on hostel food and borrowed Wi-Fi, that wasn't happening. But the security engineer in me had a different question: *how well does their payment system actually work?*

## Reconnaissance

I fired up **Burp Suite**, configured my browser's proxy, and started mapping the application. The first thing I always do when testing an e-commerce or ticketing flow is trace the entire purchase lifecycle — from item selection to payment confirmation. You'd be surprised how many applications have their most critical logic flaws sitting right in the checkout pipeline.

The Rekhta ticketing site had a fairly standard flow:

1. Select your ticket tier
2. Fill in personal details (name, phone, email)
3. Hit "Pay" — which triggers a payment gateway

I watched the HTTP traffic as I walked through the flow. Most of the requests were unremarkable — static assets, session tokens, the usual noise. But one request caught my attention.

## The Vulnerability

When you clicked the payment button, the frontend fired a **POST request** to an endpoint:

```
POST /api/createorder
```

The request body looked something like this:

```json
{
  "name": "Aadhil Anwar",
  "phone": "+91XXXXXXXXXX",
  "email": "xxxxx@gmail.com",
  "ticketType": "concert",
  "amount": 1499
}
```

That `amount` field. Sitting right there in the request body. Client-controlled. Unsigned. Unvalidated.

This is what's known as a **parameter tampering** vulnerability — specifically, a **price manipulation** flaw. The architecture assumed that whatever the frontend sent was gospel truth. There was no server-side validation cross-referencing the `amount` against the actual ticket price in the database. The backend was blindly trusting the client.

Now, any developer reading this might think: *"Surely the payment gateway would catch this?"* Here's the thing — payment gateways like Razorpay process whatever amount they receive in the order creation call. They don't know or care what the "correct" price is. That's the merchant's responsibility. If the merchant's backend says "create an order for INR 2," Razorpay creates an order for INR 2. The trust boundary was broken at the application layer, not the gateway layer.

## The Exploit

I intercepted the request in Burp Suite's **Intercept** tab, modified the `amount` parameter:

```json
{
  "name": "Aadhil Anwar",
  "phone": "+91XXXXXXXXXX",
  "email": "xxxxx@gmail.com",
  "ticketType": "concert",
  "amount": 2
}
```

Forwarded the request. The server accepted it without flinching and returned a valid Razorpay order object with `amount: 200` (Razorpay uses paise, so INR 2 = 200 paise). A UPI payment request for **INR 2** popped up on my phone.

I paid it.

**And just like that — I had a confirmed ticket to Jashn-e-Rekhta.**

The payment confirmation email came through within seconds. The pass was delivered to my WhatsApp and email. A fully valid concert ticket, for the price of a candy bar.

![Payment confirmation showing INR 2 paid successfully]({{ '/images/blog/rekhta-payment-confirmation.png' | relative_url }})

![Jashn-e-Rekhta payment successful page with pass confirmation]({{ '/images/blog/rekhta-ticket-success.png' | relative_url }})

## Why This Matters

This isn't just a "fun hack." This is a textbook case of a broken trust boundary between the client and the server.

**The root cause:** The backend used the `amount` value from the frontend request to create the payment order, instead of looking up the actual ticket price from its own database. The server essentially said, *"Whatever the user says they owe, that's what they owe."*

In a properly designed system, the flow should look like this:

```
Frontend sends: { ticketType: "concert" }
Backend looks up: concert → INR 1499
Backend creates order: amount = 1499 (from DB, not from client)
```

The client should never have authority over pricing. The only thing the frontend should send is a **ticket identifier** — the backend should resolve everything else. The `amount` field in the request body should have never existed.

**The impact** was significant — any attacker could purchase tickets at any arbitrary price (including INR 0 if the gateway allowed it), effectively bypassing the entire payment system. For a festival of this scale, the potential revenue loss could have been massive.

## The Fix

A proper remediation for this class of vulnerability involves:

1. **Server-side price resolution** — the backend should map ticket types to prices using its own data store, never accepting price from the client
2. **Order integrity verification** — before processing payment confirmation, verify the paid amount matches the expected amount
3. **Signed payloads** — use HMAC signatures on order parameters so tampering is detectable
4. **Post-payment reconciliation** — compare the amount received (from payment gateway webhook) against the expected amount before issuing the ticket

## Did I Go to the Concert?

No. I didn't.

Let's just say the thrill of the hack was enough for me.

---

*This vulnerability was responsibly reported to the Rekhta team and has been patched. No tickets were used, no financial damage was caused. Always hack responsibly.*
