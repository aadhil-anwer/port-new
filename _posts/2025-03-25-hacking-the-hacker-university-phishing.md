---
title: "I Reverse-Engineered a Live Phishing Operation Targeting My University"
description: "A credential harvesting campaign hit LPU from the inside. I traced the kill chain, broke into the attacker's Telegram C2, and found hundreds of compromised accounts."
date: 2025-03-25
tags: [security, phishing, incident-response, threat-hunting]
type: blog
---

## The Email

I was going through my student inbox at LPU when an email marked **Urgent** caught my eye. Sent from what appeared to be a legitimate LPU email address, warning that inactive accounts would be "permanently closed" and urging immediate login through a link.

![Phishing email sent from a compromised LPU account]({{ '/images/blog/phishing-email.png' | relative_url }})

Standard phishing playbook. But the sender wasn't a random Gmail or spoofed domain. **It was sent from an actual LPU email address** - an account that had already been compromised and was being weaponized to phish others from inside the trust boundary. LPU email addresses pass SPF, DKIM, and DMARC. They don't get flagged. Students trust them by default.

## The Phish

Pulled the email headers, extracted the link. A near-pixel-perfect clone of the Microsoft Outlook login portal.

![Fake Outlook login page - French localization]({{ '/images/blog/phishing-login-page.png' | relative_url }})

One mistake: **the page was in French**. "Se connecter," "Suivant," "Besoin d'aide?" - the kit wasn't localized for the target.

The form's `action` didn't POST to Microsoft. It posted to an attacker-controlled backend.

## The C2

Traced the exfiltration flow. Credentials were being piped into a **Telegram bot**. The bot token and chat ID were embedded in the page's JavaScript. Plaintext. No obfuscation.

```javascript
var token = "7XXXXXXXXX:AAHXXXXXXXXXXXXXXXXXXXXXXXXXXXXX";
var chat_id = "XXXXXXXXXX";
```

Queried the bot's message history via Telegram Bot API:

```
https://api.telegram.org/bot<token>/getUpdates
```

Full database of stolen credentials came back.

![Telegram C2 bot receiving stolen credentials in real time]({{ '/images/blog/phishing-c2-data.png' | relative_url }})

- **Hundreds of compromised LPU accounts** - students and staff
- Login attempts from multiple geographic locations
- Compromised accounts already being used to send more phishing emails - self-propagating chain
- Credentials from **far beyond LPU** sitting in the same C2 channel - the **French Ministry of National Education** (education.gouv.fr), major French electronics retailers, other `.edu` institutions, and multiple South Asian universities

The forwarding metadata tagged an account named **"adamo"**. The French login page, the French government and retail credentials in the same bot, the sheer spread of targets - this wasn't just an attack on LPU. It was a multi-target, multi-country operation, and LPU was one node in a much larger campaign.

## The Attack Chain

```
1. Attacker compromises initial LPU email account
2. Uses it to phish all contacts from a trusted address
3. Victim enters credentials on cloned Outlook page
4. Credentials exfiltrated to Telegram bot in real time
5. New credentials used to compromise more accounts
6. Self-propagating loop
```

## The Response

I reported the findings to every affected domain I could identify from the C2 data - the French ministry, the retailers, the other universities. Most responded and acted on it.

LPU's dean's response: *"It's just student data, not staff data."*

Didn't hear the full issue out. Hundreds of compromised accounts, an active self-propagating chain, credentials from French government ministries and retailers in the same C2 - and the man said "just student data."

I'm sure the attacker appreciated the extra time.
