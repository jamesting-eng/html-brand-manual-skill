# CJK Typography for HTML Brand Manuals

## Complete Reference Guide

This document covers everything you need to know about rendering Chinese/Japanese/Korean text correctly in single-file HTML brand manuals.

---

## 1. Understanding CJK Line Breaking

### How Browsers Break CJK Text

CJK languages (Chinese, Japanese, Korean) do NOT use spaces between words. Each character is conceptually a "word," but characters form **phrases** (词组) that should ideally stay together.

```
English:  The quick brown fox jumps over the lazy dog
          ↑ spaces define word boundaries → break only at spaces

Chinese:  品牌视觉手册是企业形象的核心资产
          ↑ NO spaces → browser can break at ANY character boundary
          ↑ But "品牌视觉" is a phrase — breaking here looks wrong
```

### The CSS Properties That Control This

| Property | Values | What It Does |
|----------|--------|-------------|
| `word-break` | `normal` / `keep-all` / `break-all` / `break-word` | Controls where line breaks are ALLOWED |
| `overflow-wrap` | `normal` / `break-word` / `anywhere` | What happens when content overflows container |
| `white-space` | `normal` / `nowrap` / `pre` / etc. | Whether whitespace collapsing and wrapping happen |
| `line-break` | `auto` / `loose` / `normal` / `strict` | Punctuation-level break rules (East Asian) |

---

## 2. The Correct Configuration

### For Body Paragraphs

```css
p, li, td, th, div, span, blockquote, strong, em {
  word-break: normal;      /* Allow breaks at CJK character boundaries */
  overflow-wrap: normal;   /* Don't force artificial breaks */
  /* NO white-space rule    Let it wrap naturally */
  /* NO text-align: justify  CJK justification creates ugly gaps */
}
```

**Result:** Chinese text fills the container width naturally, breaking at phrase boundaries when possible.

**Example output:**
```
[BRAND] 的核心受众是注重品质的城市专业人士——
他们重视美学，但忙碌的日程让他们难以跟上
最新的设计趋势。
```
↑ Each line fills to near the container edge. Natural-looking.

### For Section Titles & Headings

```css
h2.section-title, h3.subsection-title, .section-number,
.part-divider-title {
  word-break: keep-all;     /* Keep CJK phrases together */
  overflow-wrap: normal;
  white-space: nowrap;       /* Don't break at all — these are short */
}
```

**Result:** Titles like "品牌视觉识别系统" stay on one line.

### For Generic h1-h6 (Variable Length)

```css
h1, h2, h3, h4, h5, h6 {
  word-break: keep-all;     /* Don't split CJK phrases */
  overflow-wrap: normal;
  /* NO nowrap — long headings need to wrap eventually */
}
```

**Why no `nowrap`:** Some chapter titles are long:
- ✅ Short: `"Logo 规范"` → fits one line, keep-all prevents bad breaks anyway
- ⚠️ Medium: `"色彩对比度与无障碍规范"` → might need to wrap
- ❌ Long: `"社交媒体内容策略与平台运营指南"` → MUST wrap, nowrap would overflow

`keep-all` alone ensures that IF it wraps, it won't split in the middle of a CJK phrase.

---

## 3. Anti-Patterns Catalog

### Anti-Pattern A: Global Keep-All

```css
/* WRONG */
* { word-break: keep-all !important; }
```

**What goes wrong:**
- Body paragraphs treat entire sentences as unbreakable units
- Browser pushes whole sentence/phrase to next line
- Right side of paragraph has massive empty space (20-40% of width)
- User sees "文字没有铺满底框" and reports as bug

**Visual example of the damage:**
```
Container: [========================================]

With keep-all:
品牌视觉手册是企业形象建设的核心工具，
它统一了品牌在各种媒介上的视觉表现，
确保了一致性和专业性。

Without keep-all (correct):
品牌视觉手册是企业形象建设的核心工具，它统
一了品牌在各种媒介上的视觉表现，确保了
一致性和专业性。           ↑ Fills to edge!
```

### Anti-Pattern B: Contradictory Rules

```css
/* WRONG — these two fight each other */
* { word-break: keep-all !important; }
p { overflow-wrap: break-word !important; }  /* OVERRIDES keep-all! */
```

**What goes wrong:** `overflow-wrap: break-word` takes precedence in the browser's line-breaking algorithm, making `word-break: keep-all` meaningless. Result: unpredictable behavior that changes based on container width.

### Anti-Pattern C: Justify on CJK

```css
/* WRONG */
p { text-align: justify; }
```

**What goes wrong:** Justification adds space BETWEEN CJK characters (which are all monospace-width). Result:

```
正  常: 品牌视觉手册是企业的核心资产
对  齐: 品 牌 视 手 册 是 企 业 的 核 心 资 产
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
         Ugly uneven spacing between every character!
```

### Anti-Pattern D: max-width on Content Paragraphs

```html
<!-- WRONG -->
<p style="max-width: 700px;">Long brand story text...</p>
```

**Problem:** The parent section container might be 1200px wide. The `<p>` at 700px leaves 500px of empty space on the right. Content BELOW the paragraph (cards, grids, tables) fills 1200px. Visual mismatch → user thinks it's a bug.

**Rule:** If you need width constraints, apply them at the **container level**, not individual paragraphs.

---

## 4. Punctuation Break Prevention

### Problem: Breaking After 、or ，

Chinese titles often contain enumeration commas (、) or regular commas (，):

```
"色彩、字体与排版规范"
     ↑ Browser may break HERE, leaving "字体与排版规范" on next line
```

### Solution Hierarchy (in order of preference)

1. **`white-space: nowrap`** on known-short title elements (best for fixed UI)
2. **`word-break: keep-all`** (prevents most mid-phrase breaks)
3. **Non-breaking space entities** `&nbsp;` around punctuation (manual, fragile)

For the brand manual context, solution #1 + #2 combined works best:

```css
.section-title {
  word-break: keep-all;
  white-space: nowrap;   /* Section titles are always short enough */
}

.subsection-title {
  word-break: keep-all;
  white-space: nowrap;   /* Subsection titles too */
}

h3[style*="font-size"] {  /* Inline-styled h3 subheadings */
  word-break: keep-all;
  white-space: nowrap;
}
```

---

## 5. Browser Compatibility Notes

| Browser | `keep-all` support | Known Quirks |
|---------|-------------------|--------------|
| Chrome 90+ | Full | Handles CJK correctly by default |
| Firefox 88+ | Full | Same as Chrome |
| Safari 14+ | Full | May handle `overflow-wrap` slightly differently |
| Edge (Chromium) | Full | Same as Chrome |

**Practical note:** All modern browsers (2024+) handle these properties correctly. The issues arise from **conflicting CSS rules within the same file**, not browser bugs.

---

## 6. Testing Checklist

After implementing typography rules, verify:

- [ ] Long Chinese paragraph fills container width (no large right margin gap)
- [ ] Short section title stays on one line
- [ ] Medium-length heading wraps at word boundary, not mid-CJK-phrase
- [ ] Title doesn't break after 、/，/、 punctuation
- [ ] English words within Chinese text don't create overflow
- [ ] Dark mode sections have same typography behavior
- [ ] Mobile/narrow viewport: text still readable, no horizontal scroll
- [ ] Tables: text inside cells follows same rules
- [ ] Lists (`<ul>`/`<ol>`): list items fill available width

---

## 7. Migration Guide

### If You Have an Existing Manual With Typography Issues

1. Search file for ALL `word-break` declarations: `grep -n "word-break" index.html`
2. Search for ALL `overflow-wrap` declarations: `grep -n "overflow-wrap" index.html`
3. Identify conflicting rules (same property with different values at different specificity levels)
4. Apply the Phase 8 Safety Net pattern (CSS + JS) as a baseline fix
5. Remove or update old conflicting rules
6. Remove inline `max-width` from `<p>` tags
7. Test in browser with actual content
