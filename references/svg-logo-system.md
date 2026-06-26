# SVG Logo Vector System for Brand Manuals

## Deep Dive: Architecture, Implementation, and Pitfalls

---

## 1. Why SVG Symbols?

For a single-file HTML brand manual, the `<symbol>` + `<use>` pattern provides:

- **Single source of truth** — define logo once, reference everywhere
- **Automatic theming** — `currentColor` inherits from parent `color` property
- **Small file size** — symbol definitions are cached by browser, `<use>` is tiny
- **Scalable** — render at any size without quality loss
- **No external dependencies** — no PNG/SVG files to manage

## 2. The Symbol Definition Pattern

### File Structure

```html
<!-- Place at END of <body>, just before </body> -->
<svg xmlns="http://www.w3.org/2000/svg" display="none">
  <!-- All symbols defined here, invisible on page -->

  <!-- Variant 1: Icon only (graphical mark) -->
  <symbol id="brand-icon" viewBox="0 0 581 641">
    <path d="M...path data..."/>
  </symbol>

  <!-- Variant 2: Wordmark (brand name as paths) -->
  <symbol id="brand-wordmark" viewBox="-8.6 -85.4 456.0 91.0">
    <path d="M...font-to-svg path data..."/>
  </symbol>

  <!-- Variant 3: Slogan/tagline (custom font as paths) -->
  <symbol id="brand-slogan" viewBox="-4.0 -4.0 412.8 102.5">
    <path d="M...slogan path data..."/>
  </symbol>

  <!-- Variant 4: Icon + Wordmark stacked -->
  <symbol id="brand-full" viewBox="0 0 601.0 848.4">
    <use href="#brand-icon" x="10" y="0" width="250" height="280"/>
    <use href="#brand-wordmark" x="82.0" y="745.4" width="380" height="80"/>
  </symbol>

  <!-- Variant 5: Full + Slogan -->
  <symbol id="brand-full-slogan" viewBox="0 0 601.0 974.9">
    <use href="#brand-full" x="0" y="0"/>
    <use href="#brand-slogan" x="94" y="870" width="350" height="90"/>
  </symbol>
</svg>
```

### Usage

```html
<!-- Anywhere in the document: -->
<svg style="width:60px; color:#0B1B3A"><use href="#brand-icon"/></svg>
<svg style="width:200px; color:#0B1B3A"><use href="#brand-wordmark"/></svg>
<svg style="color:#fff"><use href="#brand-full"/></svg> <!-- Auto sizes from viewBox -->
```

## 3. Converting Fonts to SVG Paths

### Using opentype.js

When your brand uses a custom font for the wordmark or slogan that isn't available via web fonts:

```javascript
// Node.js script to convert TTF/OTF font to SVG path data
const opentype = require('opentype.js');
const font = loadFont('BRAND-FONT.TTF');

// Get glyph paths for each character
const text = 'BrandName';
const fontSize = 100;
const path = font.getPath(text, 0, 0, fontSize);

// Output SVG path data
console.log(path.toSVG(fontSize));
```

### Important Notes About Font Conversion

1. **Output often has NEGATIVE coordinates** in viewBox because fonts use a coordinate system where baseline is Y=0 and ascenders go negative (into negative Y space)

2. **Kerning may be lost** — convert the full word at once, not individual characters

3. **License check required** — embedding font outlines in SVG may require specific font license permissions

4. **Path complexity** — converted fonts produce complex path data with many commands; file size impact is usually acceptable (< 10KB per wordmark)

## 4. THE CRITICAL ISSUE: Negative Coordinate viewBox

### What Happens

When you convert a font with opentype.js, the output looks like:

```xml
<symbol id="brand-wordmark" viewBox="-8.6 -85.4 456.0 91.0">
<!--           ^^^^^^  ^^^^^^                    -->
<!--           X origin is slightly negative       -->
<!--           Y origin is DEEPLY negative (-85.4) -->
```

The actual visible content spans from approximately Y=-85 to Y=+6 (a ~91 unit tall area), but it's positioned mostly in NEGATIVE Y space.

### Why This Breaks Rendering

| Method | What Browser Does | Result |
|--------|------------------|--------|
| `height: auto` | Calculates from viewBox ratio, but negative origin confuses some engines | Height ≈ 0–2px (invisible!) |
| No explicit size | Uses CSS default (usually 300×150) | Logo might be tiny or wrong aspect |
| `height: 14px` fixed | Renders into 14px tall box | Content clipped because it extends beyond box bounds |
| Default `overflow: hidden` on SVG | Clips anything outside viewBox | Negative-coordinate content INVISIBLE |

### The Fix (Proven After 10+ Iterations)

```css
/* For ANY SVG element whose symbol has negative coordinates in viewBox */
.brand-logo svg {
  width: 70px;           /* Explicit, reasonable width */
  height: 16px;          /* Explicit, reasonable height — NOT auto */
  overflow: visible;     /* CRITICAL: show beyond-bounds content */
  display: block;        /* Remove inline spacing */
}
```

And in the HTML:
```html
<svg width="70" height="16" viewBox="-8.6 -85.4 456.0 91.0"
     overflow="visible" role="img" aria-label="[BRAND]"
     style="display:block; overflow:visible;">
  <use href="#brand-wordmark"/>
</svg>
```

### Belt-and-Suspenders Approach

Apply `overflow: visible` in THREE places for maximum reliability:

1. As an **SVG attribute**: `<svg overflow="visible">`
2. As an **inline style**: `style="overflow:visible"`
3. In the **CSS rule**: `.brand-logo svg { overflow: visible }`

## 5. Color Theming with currentColor

### Automatic Light/Dark Switching

```html
<!-- Light background → dark logo -->
<div class="logo-light">
  <svg style="color: #1A3268"><use href="#brand-wordmark"/></svg>
</div>

<!-- Dark background → light logo -->
<div class="logo-dark">
  <svg style="color: #ffffff"><use href="#brand-wordmark"/></svg>
</div>
```

In the symbol definition, all fills must be `currentColor`:

```xml
<symbol id="brand-wordmark" viewBox="...">
  <path d="..." fill="currentColor"/>   <!-- NOT #0B1B3A or any fixed color -->
</symbol>
```

### ⚠️ Common Mistake

If you hardcode colors inside the symbol:

```xml
<!-- WRONG — always renders dark regardless of parent -->
<path d="..." fill="#0B1B3A"/>
```

The `currentColor` inheritance chain is:
```
Parent element `color` property
  ↓ inherited by
SVG element (implicit)
  ↓ inherited by (if fill="currentColor")
<path> elements inside <use> shadow DOM
```

### Gradient Text Effect (Slogans)

For artistic slogan rendering with gradient fill:

```css
.slogan-artistic {
  font-family: '[CUSTOM-FONT]', sans-serif;
  letter-spacing: 2px;
  background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.7) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

Note: This requires the text to be actual text (not SVG paths). For SVG-path slogans, apply gradient to the path `fill` attribute instead.

## 6. Sizing Guide

### Recommended Sizes by Context

| Context | Width | Height | Notes |
|---------|-------|--------|-------|
| Navigation sidebar wordmark | 60–70px | 14–18px | Fixed height! See Section 4 |
| Footer logo | 100–140px | auto | Footer has more vertical space |
| Cover page large logo | 200–300px | auto | Hero display, auto OK here |
| Section header small icon | 36px | 36px | Icon only, square |
| Comparison table example | 28–40px | auto | Small reference |
| Favicon / touch icon | 180×180 | 180×180 | Export separately |
| Social media avatar | 400×400 | 400×400 | Export separately |

## 7. Nested SVG Anti-Pattern

### The Problem

When building diagrams that contain logos (e.g., clear space specification diagram):

```html
<!-- FRAGILE — nested <svg> inside parent <svg> -->
<svg viewBox="0 0 300 300">
  <rect x="50" y="50" width="200" height="200" fill="none" stroke="#ccc"/>

  <!-- Nested SVG for logo — PROBLEMS AHEAD -->
  <svg x="80" y="80" width="80" height="auto">  <!-- height:auto fails here! -->
    <use href="#brand-icon"/>
  </svg>
</svg>
```

**Issues with nested SVG:**
1. `height: auto` doesn't work predictably inside another SVG
2. Coordinate systems don't compose intuitively
3. `overflow: hidden` on outer SVG can clip inner content

### The Solution

Use `<use>` directly with positioning:

```html
<svg viewBox="0 0 300 300">
  <rect x="50" y="50" width="200" height="200" fill="none" stroke="#ccc"/>

  <!-- Direct <use> with transform for positioning -->
  <g transform="translate(110, 75)">
    <use href="#brand-icon" width="80" height="88"/>
  </g>
</svg>
```

Or calculate exact position and set explicit dimensions on the `<use>` element.

## 8. Export Variants

For asset packages, provide these export formats:

```
assets/
├── logo-primary.svg        # Full color (light bg)
├── logo-reverse.svg         # Full color (dark bg)
├── logo-icon.svg            # Icon only
├── logo-wordmark.svg        # Wordmark only
├── logo-horizontal.svg      # Icon + wordmark horizontal
├── logo-stacked.svg         # Icon + wordmark stacked
├── favicon.ico              # Multi-size ICO
├── apple-touch-icon.png     # 180×180 PNG
└── og-image.png             # Open Graph preview image
```

Each exported SVG should be a standalone file (symbols expanded, no `<use>` references).
