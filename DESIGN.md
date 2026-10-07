---
name: Aadhil Anwar — Quiet Authority
description: Dark, dense, terminal-adjacent portfolio for a security engineer. Substance over decoration.
colors:
  bg-primary: "#0c0c0e"
  bg-secondary: "#141418"
  bg-card: "#18181c"
  bg-elevated: "#1e1e24"
  bg-code: "#161619"
  text-primary: "#ededef"
  text-secondary: "#a0a0ab"
  text-muted: "#5c5c6a"
  accent: "#6e56cf"
  accent-hover: "#7c66d4"
  link: "#8a8fff"
  link-hover: "#a0a4ff"
  border: "#23232b"
  divider: "#1c1c22"
  button-bg: "#ededef"
  button-text: "#0c0c0e"
  button-hover: "#d4d4d8"
  success: "#45c882"
  warning: "#e5a93d"
  error: "#e5534b"
typography:
  display:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    fontSize: "2.5rem"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.03em"
  headline:
    fontFamily: "Inter, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Inter, sans-serif"
    fontSize: "1.05rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Inter, sans-serif"
    fontSize: "0.925rem"
    fontWeight: 400
    lineHeight: 1.7
    letterSpacing: "normal"
  label:
    fontFamily: "'JetBrains Mono', 'Fira Code', monospace"
    fontSize: "0.7rem"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "0.08em"
rounded:
  xs: "4px"
  sm: "6px"
  md: "8px"
  lg: "12px"
spacing:
  xs: "0.5rem"
  sm: "0.85rem"
  md: "1.25rem"
  lg: "2rem"
  section: "4rem"
components:
  button-primary:
    backgroundColor: "{colors.button-bg}"
    textColor: "{colors.button-text}"
    rounded: "{rounded.sm}"
    padding: "0.55rem 1.15rem"
  button-primary-hover:
    backgroundColor: "{colors.button-hover}"
    textColor: "{colors.button-text}"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.sm}"
    padding: "0.55rem 1.15rem"
  social-btn:
    backgroundColor: "{colors.bg-card}"
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.sm}"
    padding: "0.4rem 0.85rem"
  card:
    backgroundColor: "{colors.bg-card}"
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.md}"
    padding: "1.5rem"
---

# Design System: Aadhil Anwar — Quiet Authority

## 1. Overview

**Creative North Star: "The Terminal Notebook"**

This is the workspace of someone who reads syslogs for a living and writes things down precisely. Near-black surfaces, small dense type, a single restrained violet that almost never appears. The design reads like a well-configured terminal and a careful engineer's notes: nothing is loud, everything is legible, and the substance (a CVSS number, a root-cause sentence, a CVE credit) is what carries weight. The interface is deliberately quiet so the work reads first.

Density is the signature. Type runs small (body at ~0.925rem, headings rarely past 2.5rem), tracking is tight on display sizes, and the layout favors information over whitespace theatrics. This is not minimalism-as-emptiness; it is minimalism-as-restraint. The four-tier near-black elevation system creates depth without a single drop shadow.

It explicitly rejects the security-category reflex (green-on-black hacker cosplay, glitch text, skull/lock iconography), the SaaS landing template (gradient-text heroes, identical feature-card grids, tracked-uppercase eyebrows on every section, big-number hero-metric blocks), and editorial-magazine affectation (display-serif italics, drop caps). Quiet authority, computer-scientist vibe, zero generic-AI tells.

**Key Characteristics:**
- Dark-only, four-tier near-black elevation (#0c0c0e → #1e1e24), no shadows.
- Small, dense, tightly-tracked type. Information density over whitespace.
- A muted violet accent (#6e56cf) used on ≤10% of any screen.
- Inter for everything visible; JetBrains Mono reserved for labels, dates, and code.
- Motion is a brief, one-time entrance fade; never scroll-triggered decoration.

## 2. Colors

A near-monochrome dark palette: five tiers of near-black, three tiers of off-white text, and a single muted violet that earns its rare appearances.

### Primary
- **Muted Violet** (#6e56cf): The one accent. Reserved for focus rings, the contact icon, selection highlight, and small in-content emphasis. Its scarcity is the entire point; it never fills a surface. Hover lifts to #7c66d4.

### Secondary
- **Blue-Violet Link** (#8a8fff): In-content links only, kept deliberately distinct from the accent violet so a link never reads as decoration. Hover brightens to #a0a4ff.

### Neutral
- **Void** (#0c0c0e): The page background. Tier 0 of the elevation system.
- **Raised** (#141418) / **Card** (#18181c) / **Elevated** (#1e1e24): Tiers 1-3. Depth is conveyed by getting lighter, never by shadow. **Code** (#161619) is the inline/block code surface.
- **Bright Ink** (#ededef): Primary text and headings. Also the primary-button fill (an inversion: light button on dark page).
- **Muted Ink** (#a0a0ab): Body copy and secondary text. Hits AA on every background tier.
- **Faint Ink** (#5c5c6a): Timestamps, metadata, captions. Decorative/non-essential only — it does NOT clear AA 4.5:1 on the darkest backgrounds, so it is forbidden for body-length reading text.
- **Hairline** (#23232b) / **Divider** (#1c1c22): Borders and section rules. One pixel, never a colored stripe.

### Status
- **Success** (#45c882) / **Warning** (#e5a93d) / **Error** (#e5534b): Indicators and state only. Never decorative.

### Named Rules
**The One Voice Rule.** The violet accent appears on ≤10% of any given screen. If a comp has violet in three places above the fold, two of them are wrong.

**The No-Stripe Rule.** Color never arrives as a `border-left` accent bar. Emphasis comes from the ink ramp, a full hairline border, or a background tier shift — never a side stripe.

## 3. Typography

**Display / Body Font:** Inter (with -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif)
**Label / Mono Font:** JetBrains Mono (with 'Fira Code', 'SF Mono', Consolas, monospace)

**Character:** One humanist-grotesque sans carries the whole interface through weight and tightness rather than a second display face. JetBrains Mono is the engineer's tell — used only where mono *means* something (timestamps, tags, code, kickers), never as costume. The pairing is contrast-by-function, not contrast-by-decoration.

### Hierarchy
- **Display** (700, 2.5rem, 1.15, -0.03em): The hero name. The single largest type on the site; deliberately restrained, never a fluid clamp that shouts.
- **Headline** (700, 1.75rem, 1.2, -0.02em): Page titles on inner pages.
- **Title** (700, 1.05rem, 1.3, -0.01em): Section headings (`h2`). Small for a heading — density is intentional.
- **Body** (400, 0.925rem, 1.7): Prose. Generous 1.7 line-height earns the small size its readability. Cap measure at 65–75ch (`--max-width-prose: 800px`).
- **Label** (500, 0.7rem, 0.08em, mono): Kickers, tags, dates. The only place wide tracking and (occasionally) caps are allowed.

### Named Rules
**The Mono-Means-Something Rule.** JetBrains Mono is reserved for content that is literally code, data, or metadata (timestamps, CVE ids, tags). Never set prose or marketing copy in mono to look "technical" — that is the costume the brand rejects.

**The Quiet Ceiling Rule.** Display type stops at ~2.5rem. The page states; it does not shout. No `clamp()` max above 3rem.

## 4. Elevation

Flat by doctrine. The system uses **zero box-shadows**. Depth is communicated entirely by a four-tier tonal ramp of near-blacks (#0c0c0e → #141418 → #18181c → #1e1e24): a surface that needs to read as "raised" gets a lighter background, optionally a 1px hairline border (#23232b). This is the terminal/IDE model of depth, not the material-card model.

### Named Rules
**The No-Shadow Rule.** Surfaces are flat. If a comp introduces a drop shadow or a glassmorphic blur to separate layers, it is wrong — shift the background tier or add a hairline instead.

## 5. Components

### Buttons
- **Shape:** Gently rounded (6px / `{rounded.sm}`).
- **Primary:** Inverted — bright ink fill (#ededef) on dark page, near-black text (#0c0c0e). Padding 0.55rem 1.15rem, weight 600, size 0.825rem, tracking -0.01em. Used sparingly for the single most important action.
- **Hover:** Fill dims to #d4d4d8 over 150ms. No transform, no glow.
- **Secondary / Ghost:** Transparent fill, 1px `--border` outline, bright-ink text. Hover fills to `--bg-elevated` and the border lifts to `--text-muted`.

### Social buttons / Chips
- **Style:** Card-background (#18181c) pill, 6px radius, secondary-ink text + 18px icon. Padding 0.4rem 0.85rem, size 0.825rem.
- **State:** Hover shifts background up the tier ramp and ink toward primary; icon brightens. Tags (CVE/tech) are mono, 0.675rem, 4px radius, subtle background.

### Cards / Containers
- **Corner Style:** 8px (`{rounded.md}`); the hero image uses 12px.
- **Background:** #18181c (card tier) on the #0c0c0e page.
- **Shadow Strategy:** None. See Elevation — depth is tonal.
- **Border:** Optional 1px #23232b hairline.
- **Internal Padding:** 1.5rem.
- **Nesting:** Forbidden. Never a card inside a card.

### Navigation
- Top bar, mono/sans mix, brand at 1.05rem/700 tight-tracked. Links are secondary ink, hover to primary. Mobile: hamburger toggle with outside-click close (`js/main.js`). Active state is a color shift, not an underline bar.

### Motion
- **Entrance only.** Sections fade in (`fadeIn`, 0.3s ease-out, translateY(6px)). The hero staggers its children at 60ms intervals (kicker → name → tagline → bio → links). This is a one-time page-load choreography, not scroll-triggered.
- **Reduced motion:** All entrance animation is gated behind `@media (prefers-reduced-motion: no-preference)`, so it is absent (instant, content visible) for users who opt out. Content is never gated on a transition firing.
- **Transitions:** 150ms (fast) / 200ms (base), plain `ease`. State feedback only — color and background shifts, no transforms.

## 6. Do's and Don'ts

### Do:
- **Do** keep the violet accent (#6e56cf) on ≤10% of any screen — focus rings, one icon, selection, rare emphasis.
- **Do** convey depth by stepping up the near-black tier ramp (#0c0c0e → #1e1e24) and using 1px hairlines, never shadows.
- **Do** reserve JetBrains Mono for real code, data, timestamps, and tags.
- **Do** keep type small and dense with tight tracking on display sizes; let 1.7 line-height carry readability.
- **Do** let specifics carry credibility — a CVSS score, a named tool, a root-cause sentence — not adjectives.
- **Do** gate every animation behind `prefers-reduced-motion` and keep entrances to a single page-load fade.
- **Do** keep body text on `--text-secondary` (#a0a0ab) or brighter to hold WCAG AA 4.5:1.

### Don't:
- **Don't** do hacker/terminal cosplay: green-on-black, matrix rain, glitch text, skull/lock/binary iconography, "h4ck3r" theatrics.
- **Don't** build the SaaS landing template: gradient-text heroes, identical icon+heading+text feature-card grids, tracked-uppercase eyebrows above every section, big-number hero-metric blocks.
- **Don't** drift into editorial-magazine affectation: display-serif italic headlines, drop caps, broadsheet column rules.
- **Don't** use `background-clip: text` gradient text anywhere — emphasis is weight and size, in one solid color.
- **Don't** use a `border-left`/`border-right` greater than 1px as a colored accent stripe; rewrite with a full border, a tier shift, or a leading mono label.
- **Don't** introduce drop shadows or decorative glassmorphism to fake depth.
- **Don't** set `--text-muted` (#5c5c6a) on body-length reading text; it fails AA on the dark backgrounds. It is for non-essential metadata only.
- **Don't** nest cards, or push display type past ~2.5rem. Quiet, not loud.
