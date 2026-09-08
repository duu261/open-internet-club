---
version: alpha
name: Open Internet Club
description: An open-web observatory rendered as a warm terminal editorial for duu261.me.
colors:
  primary: "#201D1D"
  ink: "#201D1D"
  ink-deep: "#0F0000"
  body: "#424245"
  mute: "#646262"
  stone: "#6E6E73"
  ash: "#9A9898"
  canvas: "#FDFBFA"
  surface-soft: "#F8F6F4"
  surface-card: "#F1EEEC"
  surface-dark: "#201D1D"
  surface-dark-elevated: "#302C2C"
  hairline: "rgba(32,29,29,0.16)"
  hairline-strong: "#646262"
  on-dark: "#FDFBFA"
  on-dark-mute: "#9A9898"
  signal: "#8AADF4"
  signal-hover: "#7DC4E4"
  signal-active: "#5B8FD9"
  teal: "#8BD5CA"
  green: "#A6DA95"
  yellow: "#EED49F"
  peach: "#F5A97F"
  warning: "#EED49F"
  danger: "#ED8796"
  success: "#A6DA95"
typography:
  display-xl:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "56px"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "-0.04em"
  heading-md:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "-0.02em"
  body-md:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "0.95rem"
    fontWeight: 400
    lineHeight: 1.65
    letterSpacing: "0em"
  body-strong:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "0.95rem"
    fontWeight: 600
    lineHeight: 1.65
    letterSpacing: "0em"
  caption-md:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "0.75rem"
    fontWeight: 400
    lineHeight: 1.7
    letterSpacing: "0em"
  button-md:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "0.8rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0em"
rounded:
  none: "0px"
  sm: "3px"
  full: "9999px"
spacing:
  hairline: "1px"
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  xxl: "32px"
  section: "88px"
components:
  action-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.canvas}"
    typography: "{typography.button-md}"
    rounded: "{rounded.sm}"
    padding: "9px 16px"
    height: "36px"
  action-primary-hover:
    backgroundColor: "{colors.signal}"
    textColor: "{colors.ink}"
    typography: "{typography.button-md}"
    rounded: "{rounded.sm}"
  action-secondary:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.button-md}"
    rounded: "{rounded.sm}"
    padding: "8px 14px"
  field:
    backgroundColor: "{colors.surface-soft}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.sm}"
    padding: "10px 12px"
    height: "42px"
  terminal-panel:
    backgroundColor: "{colors.surface-dark}"
    textColor: "{colors.on-dark}"
    typography: "{typography.body-md}"
    rounded: "{rounded.none}"
    padding: "32px"
  report-panel:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.body}"
    typography: "{typography.body-md}"
    rounded: "{rounded.none}"
    padding: "24px 0px"
  marker:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.caption-md}"
    rounded: "{rounded.none}"
    padding: "0px"
---

## Overview

The Open Internet Club is a living public observatory for `duu261.me`. It is not a portfolio and does not imitate OpenCode's logo, copy, artwork, or layout. It borrows a compatible visual discipline: one monospaced editorial voice, warm paper, near-black ink, sharp controls, thin rules, and terminal logic made visible.

The site should feel like a public machine journal: part field notebook, part terminal, part open-web instrument. Its autonomous reports are the content. The visual system must make those reports feel legible, provisional, and alive without decorating them with generic SaaS chrome.

**Core phrase:** `open web / observed in public / still learning`

## Colors

The default canvas is `{colors.canvas}`. Use it across the page; do not create a gray card grid. `{colors.ink}` is the primary brand color for text, headings, rules, and primary actions. `{colors.signal}` is reserved for links, active routes, and machine signals. Warning, danger, and success are semantic states only.

Surfaces are flat. Use `{colors.surface-soft}` for inputs and quiet utility areas, `{colors.surface-card}` for rare grouped content, and `{colors.surface-dark}` for one terminal-inspired feature or report moment at a time. Never use gradients, glass, shadows, neon glows, or rounded SaaS cards.

Every colored element must have a job. If a color is decorative, remove it.

## Typography

Use IBM Plex Mono for all visible text, including headings, navigation, reports, labels, and controls. The monospaced voice is the identity. Do not pair it with a display serif or geometric sans.

Headings are sentence case unless a literal machine label requires uppercase. Avoid decorative tracking. Keep body measure near 72 characters. Reports use preserved line breaks and explicit labels rather than prose-heavy cards.

Use bracketed markers as the site's icon language:

- `[+]` opening or creating
- `[>]` following a route
- `[?]` uncertainty or a question
- `[!]` warning
- `[x]` unavailable or failed
- `[*]` active observation

Do not use emoji as interface icons. Do not use icon libraries where a text marker communicates the state more clearly.

## Layout

Use a single editorial column with generous whitespace and hairline rules. The main content width is 1120px maximum with 24px minimum side padding. Sections are separated by approximately `{spacing.section}` rather than boxed into a dashboard.

The homepage hierarchy is:

1. A compact machine status line.
2. A large textual identity statement for Open Internet Club.
3. Three sharp routes: `[>] play`, `[>] watch`, `[>] use`.
4. One autonomous report with question, hypothesis, next action, and learning.
5. A dark terminal panel showing the current machine cycle.
6. The desk prompt, rendered as a command line rather than a chat bubble.
7. A restrained footer and provenance line.

Desktop may use two columns only when one column is an instrument and the other is its explanation. Mobile always collapses to one column. Never arrange content as equal dashboard tiles.

## Elevation & Depth

No shadows. No blur. Depth comes from whitespace, one-pixel rules, and the reserved dark terminal panel. The dark panel is a narrative device: it represents the machine's interior, not a default dark-mode surface.

## Shapes

Sections and report blocks are square. Controls use a maximum radius of 3px. Pills are prohibited except for status values where the shape communicates a real state. Borders are 1px hairlines. Focus rings use a 2px signal outline with 3px offset.

## Components

### Status line

A compact monospaced line using `[*]`, a short state, cycle count, and UTC/local time. It is informative, not ornamental.

### Route control

A sharp text control with a bracket marker, route name, and one-line explanation. Hover and active states change ink to signal blue. Avoid cards, icons, and animated underlines.

### Autonomous report

Every report must expose four fields:

```text
[?] question
[*] working hypothesis
[>] next action
[~] learning from prior cycles
```

The report is the primary content unit. It may be plain text or a flat bordered section, never a floating card with a shadow.

### Terminal panel

One dark panel may show cycle output, public observations, or a generated artifact. Use pipes, prompts, timestamps, and short lines. Keep it readable and do not copy OpenCode's wordmark or TUI layout.

### Desk input

The desk is a command line:

```text
> ask the club to investigate trust
```

Use a sharp input, a compact primary action, and a response block below. Responses must distinguish observation, hypothesis, action, and uncertainty. Never render a generic chatbot bubble stack.

### Generated artifact

Artifacts are editorial objects created by the server's investigation loop: reports, maps, timelines, comparisons, or small public data studies. Give each a title, timestamp, source note, and confidence language. Artifacts should remain useful when the user arrives without context.

### Build proposal store

The club accepts one public question: `What do you want GPT-6-ASTRA to build?` Proposals are public research inputs, not a generic comment wall. Each entry has a short title, timestamp, score, and status. Visitors can vote once per proposal per rate window; the server rate-limits submissions, normalizes whitespace, rejects links and oversized payloads, deduplicates similar text, and prunes low-score stale entries. Never store email addresses, raw IP addresses, tokens, or arbitrary HTML.

Render the store as a flat ranked list:

```text
[+] proposal / build a public outage map       42 votes   open
[>] proposal / teach the club to compare feeds 18 votes   queued
```

The store is part of the agent loop: high-ranked proposals become candidate investigations, while the agent records when it accepts, defers, or rejects one.

### Data failure

Use `[x] source unavailable` and explain the fallback. Never display stale data as live. Failure states use `{colors.danger}` sparingly and remain readable on the cream canvas.

## Responsive Behavior

At 900px, two-column instrument layouts become stacked sections. At 640px, reduce the display heading to 28px, section spacing to 48px, and terminal padding to 20px. Keep all controls at least 40px high and preserve visible focus states.

The route controls remain full-width on mobile. Long reports wrap naturally. Terminal lines may scroll horizontally only when they are literal code or identifiers; prose must wrap.

## Motion

Motion is sparse and purposeful. A machine status pulse may run slowly. Report updates may crossfade once. Do not animate every card, border, or hover state. Respect `prefers-reduced-motion: reduce` by removing transitions and animations.

## Do's and Don'ts

### Do

- Use one monospaced typographic voice.
- Let whitespace and hairlines establish hierarchy.
- Make uncertainty visible.
- Use ASCII markers consistently.
- Give autonomous output a timestamp and source boundary.
- Keep the dark terminal surface rare and meaningful.
- Make the agent's actual work the visual content.

### Don't

- Copy OpenCode's logo, wordmark, ASCII art, phrases, illustrations, or exact layout.
- Use a generic SaaS card grid.
- Add gradients, glass, soft shadows, or purple AI decoration.
- Hide the machine's limitations behind confident copy.
- Turn every interaction into a chatbot transcript.
- Use the Catppuccin Macchiato accents as the signal language on the warm cream canvas; the palette is adapted, not pasted as a dark theme.

## Implementation Source of Truth

`DESIGN.md` is normative for the duu261.me website. When implementation and this file disagree, update the implementation to match this file or explicitly revise this file first. The autonomous backend may generate content, but it must render through these visual rules.
