---
name: html-brand-manual
description: Create production-grade interactive Brand Visual Manuals as single-file HTML with embedded CSS/JS/SVG. Covers CJK typography system, SVG logo vector architecture, nav bar layout, color palette design, component library, version management, and iterative refinement workflow. Use when building or refining any brand guidelines / VI手册 / 品牌视觉手册 in HTML format, especially for CJK (Chinese/Japanese/Korean) content.
agent_created: true
---

# HTML Brand Visual Manual — Complete Production Skill

## Overview

Build professional single-file interactive Brand Visual Manuals (VI手册/品牌视觉手册) as self-contained HTML files with embedded CSS, JavaScript, inline SVG assets, and full interactivity (navigation sidebar, section scrolling, dark mode support). This skill encapsulates **hard-won lessons from 20+ versions of real-world iterative refinement (v1.0 → v7.5)**, covering: CJK typography pitfalls, SVG rendering quirks, layout anti-patterns, font licensing traps, competitor color collision prevention, brand story tone calibration, systematic debugging workflows, and large-scale CSS architecture decisions. See `references/common-pitfalls.md` for the complete 20-pitfall catalog with version timeline.

## When to Use This Skill

- User asks to "create a brand manual", "build a VI handbook", "make a brand guide", "制作品牌手册", "写VI手册"
- User has an existing brand manual HTML that needs typography/layout/SVG fixes
- User needs a brand guideline document with interactive navigation, dark mode, or responsive layout
- Any task involving CJK (Chinese/Japanese/Korean) text rendering in HTML/CSS
- SVG logo systems with multiple variants (icon, wordmark, slogan, full combinations)

## Core Workflow

```
1. Architecture Setup → 2. Logo/SVG System → 3. Color & Typography → 4. Content Structure → 5. Component Build → 6. CJK Typography → 7. Nav/Layout Polish → 8. Safety Net → 9. Iterate → 10. Package
```

---

## Phase 1: File Architecture

### Single-File HTML Structure

A brand manual should be a **single self-contained `index.html`** file (~10,000–20,000 lines). No external dependencies except web fonts.

```
index.html
├── <head>
│   ├── Meta tags (charset, viewport, description)
│   ├── Web Font imports (Google Fonts CDN — prefer SIL OFL fonts)
│   └── <style> block (ALL CSS — see Phase 3)
├── <body>
│   ├── <nav> (sidebar navigation)
│   ├── <main> (content sections)
│   │   ├── Cover Page
│   │   ├── Part I–V Dividers
│   │   └── Chapters 01–NN (each = one <section>)
│   └── <svg> block (ALL symbol definitions — hidden)
├── <script> (JS — navigation + safety nets)
└── Version History table (last section)
```

### Critical Rules

1. **No external CSS/JS files** — everything inline in `<style>` and `<script>` blocks
2. **SVG symbols defined ONCE** at end of `<body>` in a `<svg display="none">` block
3. **Web fonts only via CDN** (Google Fonts) — use fonts with clear licensing (SIL OFL preferred)
4. **All images relative paths** (`assets/image.jpg`) or base64 data URIs for small icons

---

## Phase 2: SVG Logo Vector System

### The Symbol + Use Pattern

Define logo variants as `<symbol>` elements, then reference with `<use href="#symbol-id">`. This is the most robust approach for single-file HTML:

```html
<!-- Symbol definitions (at bottom of body, inside hidden svg) -->
<svg xmlns="http://www.w3.org/2000/svg" display="none">
  <!-- Icon-only variant -->
  <symbol id="brand-icon" viewBox="0 0 581 641">
    <path d="...icon path data..."/>
  </symbol>

  <!-- Wordmark (text-as-paths, generated via opentype.js from TTF font) -->
  <symbol id="brand-wordmark" viewBox="-8.6 -85.4 456.0 91.0">
    <path d="...wordmark path data..."/>
  </symbol>

  <!-- Slogan (custom/artistic font converted to paths) -->
  <symbol id="brand-slogan" viewBox="-4.0 -4.0 412.8 102.5">
    <path d="...slogan path data..."/>
  </symbol>

  <!-- Full combo: icon + wordmark stacked -->
  <symbol id="brand-full" viewBox="0 0 601.0 848.4">
    <use href="#brand-icon" x="10" y="0"/>
    <use href="#brand-wordmark" x="82.0" y="745.4"/>
  </symbol>

  <!-- Full with slogan -->
  <symbol id="brand-full-slogan" viewBox="0 0 601.0 974.9">
    <use href="#brand-full" x="0" y="0"/>
    <use href="#brand-slogan" x="94" y="870"/>
  </symbol>
</svg>
```

### ⚠️ CRITICAL: viewBox With Negative Coordinates

**This is the #1 SVG rendering pitfall encountered in practice.**

When converting fonts to SVG paths via tools like opentype.js, the output often contains **negative coordinate values** in viewBox (e.g., `viewBox="-8.6 -85.4 456.0 91.0"`).

#### The Problem

| Approach | Result |
|----------|--------|
| `height: auto` on SVG element | Browser calculates height from viewBox ratio BUT may produce near-zero visible height due to negative origin |
| `height: 14px` fixed | Content gets clipped — negative coordinates extend outside the bounding box and `overflow: hidden` (default on SVG) crops them |
| No explicit dimensions | Unpredictable rendering across browsers |

#### The Solution

```css
/* For wordmarks with negative-coordinate viewBox */
.brand-wordmark svg {
  width: 70px;          /* Fixed width */
  height: 16px;         /* Fixed height — NEVER use auto */
  overflow: visible;    /* Show content beyond viewBox bounds */
  display: block;
}
```

**Rules for SVG with negative-coordinate viewBox:**
1. ALWAYS set explicit `width` AND `height` — never rely on `auto`
2. ALWAYS set `overflow: visible` on the SVG element
3. Test in multiple browsers — Chrome/Firefox/Edge handle this differently
4. Prefer `overflow: visible` as an SVG attribute AND inline style (belt-and-suspenders)

### Color Inheritance with currentColor

Use `color` property + `currentColor` for automatic theme switching:

```html
<!-- Light background: dark logo -->
<svg style="color: #1A3268"><use href="#brand-wordmark"/></svg>

<!-- Dark background: light logo -->
<svg style="color: #ffffff"><use href="#brand-wordmark"/></svg>
```

Inside symbols, all path fills/strokes should use `currentColor`:
```xml
<symbol id="brand-wordmark" ...>
  <path d="..." fill="currentColor"/>  <!-- NOT a hardcoded color -->
</symbol>
```

---

## Phase 3: CSS Architecture

### CSS Custom Properties (Variables) System

Organize ALL colors as CSS variables with semantic naming + numeric scale:

```css
:root {
  /* Primary palette — 50-900 scale (matching Tailwind conventions) */
  --primary-50: #E8EEF8;
  --primary-100: #C5D4E8;
  /* ... */
  --primary-900: #0B1B3A;

  /* Secondary palette */
  --secondary-50: #F0F9FF;
  /* ... */
  --secondary-900: #0C4A6E;

  /* Accent palette */
  --accent-50: #FFF8EB;
  /* ... */
  --accent-900: #7A4400;

  /* Neutrals */
  --gray-50: #F9FAFB;
  /* ... */
  --gray-900: #111827;

  /* Spacing scale */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
  --space-3xl: 64px;

  /* Border radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
  --radius-xl: 24px;

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 250ms ease;
}
```

### CSS Organization Order

```css
/* ===== 1. RESET & BASE ===== */
/* ===== 2. CUSTOM PROPERTIES (:root) ===== */
/* ===== 3. TYPOGRAPHY SYSTEM ===== */
/* ===== 4. LAYOUT GRID ===== */
/* ===== 5. NAVIGATION ===== */
/* ===== 6. COVER PAGE ===== */
/* ===== 7. SECTIONS & CHAPTERS ===== */
/* ===== 8. COMPONENT LIBRARY ===== */
/* ===== 9. DARK MODE ===== */
/* ===== 10. RESPONSIVE ===== */
/* ===== 11. SAFETY NETS (highest specificity) ===== */
```

---

## Phase 4: CJK Typography System

**This is the most critical and error-prone area.** See `references/cjk-typography.md` for exhaustive detail. Below is the essential reference.

### The Core Problem

CJK (Chinese/Japanese/Korean) text has fundamentally different line-breaking rules than English:

| Property | Effect on CJK | Effect on English |
|----------|--------------|-------------------|
| `word-break: normal` | Breaks at ANY CJK character boundary (can split phrases mid-sentence) | Breaks only at spaces/hyphens |
| `word-break: keep-all` | Keeps CJK phrases together (no mid-phrase breaks) | Same as normal for English |
| `overflow-wrap: break-word` | Allows breaking ANYWHERE when needed (overrides keep-all!) | Allows long words to break |
| `overflow-wrap: normal` | Respects word-break rules | Only breaks at normal break points |
| `white-space: nowrap` | Prevents ALL line breaks | Prevents ALL line breaks |

### The Golden Rule: Separate Body Text from Headings

```
BODY TEXT (p, div, span, li, td):
  word-break: normal      ← Allow natural CJK wrapping
  overflow-wrap: normal   ← Don't force arbitrary breaks
  ← NO white-space: nowrap
  ← NO text-align: justify (CJK looks bad with justification)

HEADINGS (h1-h6, .section-title, etc.):
  word-break: keep-all    ← Keep CJK phrases intact
  overflow-wrap: normal   ← Don't override
  white-space: nowrap     ← Short titles: don't break at all
  ← Long titles MAY need to allow natural wrapping
```

### Anti-Patterns That Will Break Your Layout

❌ **NEVER do this:**
```css
/* ANTI-PATTERN: Global keep-all kills paragraph flow */
* { word-break: keep-all !important; }
/* Result: Paragraphs won't fill container width,
   right side has huge whitespace gaps */
```

❌ **NEVER do this:**
```css
/* ANTI-PATTERN: Contradictory rules */
* { word-break: keep-all !important; overflow-wrap: break-word !important; }
/* Result: break-word OVERRIDES keep-all — complete chaos */
```

❌ **NEVER do this:**
```css
/* ANTI-PATTERN: justify on CJK text */
p { text-align: justify; }
/* Result: Ugly uneven character spacing in Chinese text */
```

### Correct Implementation

```css
/* Body text: natural CJK flow */
body, p, li, td, th, div, span, blockquote, strong, em {
  word-break: normal !important;
  overflow-wrap: normal !important;
}

/* Headings: phrase protection */
h1, h2, h3, h4, h5, h6,
.section-title, .subsection-title, .section-number {
  word-break: keep-all !important;
  overflow-wrap: normal !important;
  /* NOTE: Don't add nowrap globally to h1-h6 — long headings will overflow */
  /* Add nowrap only to KNOWN-short heading classes like .section-title */
}

.section-title, .subsection-title, .section-number, .part-divider-title {
  white-space: nowrap !important;  /* These are always short enough */
}
```

### Text Width: Never Constrain Content Paragraphs

❌ **Anti-pattern:**
```html
<p style="max-width: 700px;">Long brand story text...</p>
```
Result: Right side of container has large empty space while content below fills full width.

✅ **Correct:** Let paragraphs fill their container naturally. If width constraint is needed, apply it at the **container level** (the parent `.section-content` or card), not on individual `<p>` tags.

---

## Phase 5: Navigation Sidebar

### Layout Structure

```html
<nav class="nav-sidebar">
  <div class="nav-logo">
    <div class="nav-logo-icon"><!-- SVG icon use --></div>
    <div class="nav-logo-text-col">
      <div class="nav-logo-wordmark"><!-- SVG wordmark use --></div>
      <div class="nav-logo-sub">BRAND MANUAL</div>
    </div>
  </div>
  <ul class="nav-chapters">
    <!-- Part group headers + chapter links -->
  </ul>
</nav>
```

### CSS That Actually Works

After 10+ iterations of fixing overlap/disappearing/misalignment issues, this is the proven configuration:

```css
.nav-logo {
  display: flex;
  align-items: center;
  gap: 10px;           /* Space between icon and text column */
  margin-bottom: var(--space-xl);
  padding-bottom: var(--space-lg);
  border-bottom: 1px solid var(--primary-700);
  min-height: 52px;
}

.nav-logo-text-col {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;  /* NOT center — prevents vertical drift */
  gap: 0;                       /* Tight control over spacing */
  min-width: auto;
  overflow: visible;
}

.nav-logo-wordmark {
  line-height: 1;
  overflow: visible;
  min-height: 18px;             /* Ensure space for SVG */
}

.nav-logo-wordmark svg {
  width: 70px;
  height: 16px;                 /* FIXED — never auto for negative-coord viewBox */
  overflow: visible;            /* Always show full SVG content */
  display: block;
}

.nav-logo-sub {
  font-size: 9px;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  white-space: nowrap;
  line-height: 1;
  margin-top: 4px;              /* Precise gap between wordmark and sub */
}
```

### Key Lessons

1. **`gap` in flex containers matters more than margins** for controlling spacing between logo elements
2. **Never use `justify-content: center`** on the text column if you have two elements (wordmark + sub) — it causes them to drift together
3. **Fixed height on SVG > height:auto** when viewBox has negative coordinates
4. **`min-height` on wordmark container** prevents collapse when SVG renders unexpectedly small
5. **Test with actual browser rendering** — DevTools preview can be misleading

---

## Phase 6: Content Structure

### Part-Based Organization

Structure the manual into 5 logical parts:

| Part | Focus | Example Chapters |
|------|-------|-----------------|
| I | Brand Soul | Philosophy, Story, Audience, Tone, Competition |
| II | Visual Foundation | Colors, Logo, Typography, Iconography, Accessibility |
| III | Product Strategy | Naming, Hardware, AI/Ethics, Sustainability |
| IV | Application | Marketing, Social Media, Packaging, Apparel, Signage, Data Viz, Motion |
| V | Operations | Assets, Release Notes, Glossary |

### Chapter Numbering Convention

- Format: `XX — Chapter Name` (e.g., `01 — Philosophy`)
- Section IDs: `ch01-philosophy`, `ch02-brand-story`, etc.
- Part dividers are NOT numbered chapters — they're visual separators
- When adding/moving chapters, update: section IDs, nav links, part subtitles, cross-references, version history

### Section Template

Every chapter follows this consistent structure:

```html
<section id="chXX-slug" class="content-section">
  <div class="section-number">XX — PART NAME</div>
  <h2 class="section-title">Chapter Title</h2>
  <div class="section-desc">One-line description of what this chapter covers.</div>

  <!-- Subsections with h3 headings -->
  <h3>Subsection Topic</h3>
  <p>Content...</p>

  <!-- Visual examples using component classes -->
  <div class="demo-card">...</div>
  <div class="do-dont-grid">...</div>
</section>
```

---

## Phase 7: Component Library

### Essential Reusable Components

Implement these CSS classes for consistent visual presentation:

```css
/* Colored info/callout box */
.info-card { background: var(--primary-50); border-left: 4px solid var(--secondary-500); padding: var(--space-md); border-radius: var(--radius-md); }

/* Do's and Don'ts comparison grid */
.do-dont-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md); }
.do-card { border: 2px solid var(--green-500); background: var(--green-50); }
.dont-card { border: 2px solid var(--red-500); background: var(--red-50); }

/* Color swatch grid */
.color-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: var(--space-sm); }
.color-swatch { aspect-ratio: 1; border-radius: var(--radius-md); display: flex; align-items: flex-end; padding: var(--space-sm); }

/* Typography scale demo */
.type-scale-demo { display: flex; flex-direction: column; gap: var(--space-md); }

/* Icon preview grid */
.icon-preview-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: var(--space-md); }

/* Table styling (for specs/comparisons) */
.spec-table { width: 100%; border-collapse: collapse; }
.spec-table th { background: var(--gray-100); font-weight: 600; }
.spec-table td, .spec-table th { padding: var(--space-sm); border-bottom: 1px solid var(--gray-200); }

/* Dark background section (for contrast demos) */
.dark-demo { background: var(--primary-900); color: #fff; padding: var(--space-xl); border-radius: var(--radius-lg); }

/* Phone/device mockup frame */
.device-frame { width: 375px; height: 740px; background: #fff; border-radius: 40px; border: 8px solid var(--gray-900); overflow: hidden; position: relative; }
.device-notch { width: 150px; height: 28px; background: var(--gray-900); border-radius: 0 0 20px 20px; margin: 0 auto; }
```

---

## Phase 8: JavaScript Safety Nets

### Why You Need JS Safety Nets

CSS rules can be overridden by browser defaults, user stylesheets, or conflicting rules elsewhere in a large file. A JS safety net runs after DOM load to FORCE-correct styles programmatically.

### Implementation Pattern

Place this at the END of your HTML file, just before `</body>`:

```html
<!-- ============================================ TYPOGRAPHY SAFETY NET ============================================ -->
<style>
/* CSS safety net — highest specificity override */
body, p, li, td, th, div, span, blockquote, strong, em { word-break: normal !important; overflow-wrap: normal !important; }
h1, h2, h3, h4, h5, h6, .section-title, .subsection-title, .section-number { word-break: keep-all !important; overflow-wrap: normal !important; }
</style>
<script>
(function() {
  var applyRules = function() {
    // Body text: allow natural CJK wrapping
    document.querySelectorAll('p, li, td, th, div, span, blockquote, strong, em').forEach(function(el) {
      el.style.wordBreak = 'normal';
      el.style.overflowWrap = 'normal';
    });
    // Headings: protect from mid-phrase breaks
    document.querySelectorAll('h1, h2, h3, h4, h5, h6, .section-title, .subsection-title').forEach(function(el) {
      el.style.wordBreak = 'keep-all';
      el.style.overflowWrap = 'normal';
    });
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyRules);
  } else {
    applyRules();
  }
})();
</script>
```

### ⚠️ Safety Net Rules

1. **CSS safety net and JS safety net must agree** — contradictory rules = chaos
2. **JS safety net runs AFTER DOM ready** — it overrides anything else
3. **Don't put `white-space: nowrap` in JS for generic h1-h6** — only for known-short classes
4. **Keep safety net minimal** — only fix typography, don't touch layout

---

## Phase 9: Iterative Refinement Workflow

When user reports visual issues via screenshots:

### Systematic Debugging Process

1. **Read each screenshot carefully** — note the EXACT visual problem (not your interpretation)
2. **Identify the root CSS/HTML cause** — not the symptom
3. **Check for conflicting rules** — search entire file for same property
4. **Fix with minimal change** — one issue = one targeted fix
5. **Verify fix doesn't break other sections** — grep for side effects
6. **Update version number AND changelog** — every fix is a version bump
7. **Present file for user review** — always let user verify visually

### Common Issue → Fix Mapping

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Text not filling container width | `max-width` on `<p>` tag or `word-break:keep-all` on body text | Remove max-width; change to `word-break:normal` |
| Heading breaks after punctuation (、/，) | Missing `word-break:keep-all` OR missing `white-space:nowrap` on short titles | Add keep-all + nowrap for known-short titles |
| SVG logo invisible/disappearing | `height:auto` with negative-coordinate viewBox | Set explicit width+height + `overflow:visible` |
| Nav elements overlapping | Flex `gap` too small + `justify-content:center` pushing together | Increase gap; use `flex-start`; set fixed heights |
| Text overflowing container | `white-space:nowrap` on long heading | Remove nowrap; use `keep-all` only (allows natural wrap at container edge) |
| Inconsistent phone/mockup sizes | Different `height`/`min-height` values | Standardize to identical dimensions |
| Gauge/chart pointer wrong position/color | Arc drawing direction reversed; needle angle miscalculated | Verify arc math (left=bad/right=good convention); recalculate angle |
| Emoji showing as boxes | Unicode 12+ emoji on Windows without supporting font | Replace with inline SVG icons |

### Version Management

Maintain a version history table at the end of the file:

```html
<table class="spec-table">
  <tr><th>Version</th><th>Date</th><th>Changes</th></tr>
  <tr><td>v1.0</td><td>2024-01-01</td><td>Initial release</td></tr>
  <!-- Each fix/addition gets a new row -->
</table>
```

Rules:
- Bump version (minor) for every batch of fixes
- Describe changes specifically (not "various fixes")
- Date format: YYYY-MM-DD

---

## Phase 10: Data Desensitization Checklist (for Open-Sourcing)

When preparing a brand manual skill or template for open-source distribution, ensure removal of:

### Must Remove (PII / Proprietary)
- [ ] Brand name (every occurrence)
- [ ] Product name and category description
- [ ] Founder/executive names
- [ ] Slogan/tagline text
- [ ] Specific geographic markets
- [ ] Target customer demographics specific to the brand
- [ ] Competitor company names
- [ ] Pricing/revenue information
- [ ] Internal code names
- [ ] Mascot/character names and backstories
- [ ] Actual logo SVG path data (replace with placeholder rects/circles)
- [ ] Custom font file references (use generic alternatives)

### Replace With Placeholders
- `[BRAND]` — brand name placeholder
- `[PRODUCT]` — product name placeholder
- `[SLOGAN]` — tagline placeholder
- `#0B1B3A` / `--primary-*` — example color values (clearly marked as examples)
- Generic chapter content (structural examples, not actual brand copy)

### Safe to Keep (Generic Knowledge)
- ✅ CJK typography techniques
- ✅ SVG symbol+use patterns
- ✅ CSS architecture patterns
- ✅ Layout component code
- ✅ Navigation implementation
- ✅ Safety net patterns
- ✅ Debugging workflow
- ✅ Anti-pattern documentation
- ✅ Version management approach

---

## Resources

### references/
- **`cjk-typography.md`** — Exhaustive CJK typography reference with browser compatibility tables, test cases, and migration guides
- **`svg-logo-system.md`** — Deep dive into SVG symbol architecture, opentype.js font-to-path conversion, viewBox math, and color theming
- **`common-pitfalls.md`** — Catalog of **20 real-world bugs** found during production (v1.0→v7.5), with root cause analysis, prevention, and full version experience timeline map

### scripts/
- **`validate-manual.py`** — Automated QA checker for common issues (missing alt text, broken refs, contrast ratios, CJK property conflicts)

---

## Quick Start: Minimal Manual Template

For a minimal viable brand manual, implement these in order:

1. HTML skeleton with `<style>` block containing CSS variables and reset
2. SVG symbol definitions (at minimum: icon + wordmark)
3. Cover page with brand mark + title + subtitle
4. Navigation sidebar with chapter list
5. 3 core chapters: Colors, Logo Usage, Typography
6. CJK typography safety net (CSS + JS)
7. Test in browser → iterate based on screenshots
