# Product

## Register

brand

## Users

Three audiences, in priority order:

1. **Security hiring managers and senior engineers** evaluating Aadhil for roles or collaboration. They arrive from LinkedIn, a referral, or a CVE/writeup credit. They skim fast and are allergic to inflated claims; they want evidence of depth, not adjectives.
2. **Peers in the security/infosec community** who found a writeup, talk, or bug report and want to know who wrote it. They care about technical substance and credibility signals (CVEs, certs, THM rank).
3. **Recruiters and the generally curious** doing a first-pass scan. They need the one-line "who is this and what do they do" within seconds.

Context: almost always a quick, intent-driven visit, often on mobile, often a single page deep. The site is a credibility instrument, not a destination people linger in.

## Product Purpose

A personal portfolio for Aadhil Anwar, security engineer at GoDaddy. It exists to establish technical credibility and let the work speak: blog posts on networks and security, vulnerability writeups, certifications, talks, and a reading list. Success is a visitor leaving with an accurate, high impression of competence — "this person clearly knows what they're doing" — without the site ever having to say so explicitly.

## Brand Personality

Quiet authority. The vibe of a serious computer scientist, not a hacker-cosplay or a SaaS marketing page. Three words: **understated, precise, credible.**

- Voice is factual and confident. It states what is true and stops. No self-narration ("I'm passionate about..."), no hype, no teaching the reader.
- Depth is *inferred from specifics*, never claimed. A CVSS score, a concrete root-cause sentence, a named tool — these carry the weight. Superlatives do not.
- Calm and dark by disposition. The design recedes so the substance reads. Restraint here is intentional voice, not absence of effort.
- Writing style: concise, no em dashes, Arpit Bhayani register — direct sentences, no filler.

## Anti-references

- **Hacker/terminal cosplay.** Green-on-black, matrix rain, glitch effects, skull/lock/binary iconography, "h4ck3r" theatrics. The security-category reflex. This site is a security *engineer's*, not a costume.
- **SaaS landing-page template.** Gradient-text heroes, identical icon+heading+text feature-card grids, tracked-uppercase eyebrows above every section, the big-number hero-metric block.
- **Generic AI slop.** Anything where a viewer could say "an AI made this" — cream/beige warm-neutral defaults, reflex font pairings, fade-in-on-scroll for every section, decorative glassmorphism.
- **Loud / maximalist.** Heavy motion, accent color everywhere, anything attention-grabbing. Counter to quiet authority.
- **Editorial-magazine affectation.** Display-serif italic headlines, drop caps, broadsheet column rules. The "tasteful" AI lane; wrong register for an engineer's site.
- **Inflated self-presentation.** Claimed expertise, buzzword stacks, "rockstar/ninja/guru" framing.

## Design Principles

1. **Show, don't tell.** Credibility comes from specifics (a CVSS number, a root cause, a named system), never from adjectives about skill. If a claim isn't backed by an artifact, cut it.
2. **The design recedes.** Restraint is the point. The interface should never compete with the substance; quiet is a deliberate stance, not blandness.
3. **Practice what you preach.** A security engineer's site should itself be correct, fast, accessible, and free of sloppy tells. Craft is part of the argument.
4. **Earned distinctiveness over safe defaults.** Avoiding AI slop means having a real POV, not retreating to neutral. The "computer scientist" character must be felt, not generic-minimal.
5. **Respect the visitor's time.** Most visits are fast and intent-driven. Get the who/what across immediately; let depth reward those who scroll.

## Accessibility & Inclusion

Target: **WCAG 2.1 AA**, enforced as a hard constraint.

- Body text ≥ 4.5:1 contrast against its background; large/bold text ≥ 3:1. Watch muted grays on the near-black backgrounds.
- Full keyboard navigability with visible `:focus-visible` states.
- `prefers-reduced-motion` honored on every animation (crossfade or instant fallback).
- Semantic HTML and meaningful alt text; alt text written in the site's voice, not as an afterthought.
- Dark-only theme: verify each text/background pairing in the elevation system individually rather than assuming the ramp is safe.
