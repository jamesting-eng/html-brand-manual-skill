# Common Pitfalls in HTML Brand Manual Production

## Real-World Bug Catalog with Root Cause Analysis

Every entry below was encountered during actual production of a 41-chapter, ~15,000-line interactive brand manual. Learn from these mistakes.

---

## Pitfall #1: SVG Logo Disappears (Severity: CRITICAL)

**Symptom:** Brand wordmark visible in design tool but completely invisible or 1-2px tall in browser render.

**Root Cause:** SVG symbol has `viewBox` with negative Y coordinates (from font-to-SVG conversion). Using `height: auto` causes browser to calculate near-zero height.

**Fix:** Always set explicit `width` + `height` on SVG elements referencing symbols with negative-coordinate viewBox. Add `overflow: visible` as attribute, inline style, AND CSS rule.

**Iterations to fix:** 10 rounds across versions v6.5 → v7.5

---

## Pitfall #2: CJK Text Not Filling Container Width (Severity: HIGH)

**Symptom:** Chinese paragraph text leaves 20-40% empty space on right side of container. User reports "文字没有铺满底框".

**Root Cause:** Global `word-break: keep-all` applied to ALL elements including `<p>` tags. Keep-all prevents mid-sentence breaks, causing browser to push entire phrases to next line.

**Fix:** Use `word-break: normal` for body text; reserve `keep-all` for headings only.

**Iterations to fix:** 6+ rounds — kept oscillating between too-much-breaking and not-enough-breaking

---

## Pitfall #3: Headings Breaking After Punctuation (Severity: MEDIUM)

**Symptom:** Section titles like "色彩、字体与排版规范" break after the 、enumeration comma.

**Root Cause:** `word-break: keep-all` protects CJK characters but punctuation marks are still valid break points. Without `white-space: nowrap`, browser breaks at punctuation.

**Fix:** Add `white-space: nowrap` to known-short heading classes (`.section-title`, `.subsection-title`, `.section-number`). Do NOT add to generic `h1-h6` selector (long headings would overflow).

---

## Pitfall #4: Contradictory CSS Safety Nets (Severity: CRITICAL)

**Symptom:** Typography behavior is unpredictable — sometimes works, sometimes doesn't. Changes seemingly randomly between page loads.

**Root Cause:** Multiple CSS rules fighting each other:
```css
/* Rule A somewhere in file */
* { word-break: keep-all !important; overflow-wrap: normal !important; }

/* Rule B added later for "fix" */
* { overflow-wrap: break-word !important; }  /* SILENTLY OVERRIDES Rule A! */
```

Plus JS safety net doing something different yet again:
```javascript
el.style.overflowWrap = 'break-word';  // Different from both CSS rules!
```

**Fix:** Establish ONE source of truth. CSS safety net + JS safety net must agree. Audit ALL occurrences of `word-break` and `overflow-wrap` in file before adding new rules. Use `grep -n` to find every instance.

---

## Pitfall #5: Nav Bar Elements Overlapping (Severity: HIGH)

**Symptom:** Logo wordmark overlaps with subtitle text ("BRAND MANUAL"). No amount of margin/padding fixes it consistently.

**Root Cause:** Combination of factors:
1. Flex container `justify-content: center` pushes child elements toward each other
2. `gap: 3px` too small for content
3. Wordmark SVG height varies (auto vs fixed), changing layout box
4. `align-items: flex-end` pulls wordmark down into subtitle area

**Fix:**
```css
.nav-logo-text-col {
  justify-content: flex-start;  /* NOT center */
  gap: 0;                       /* Precise control via margins */
}
.nav-logo-wordmark svg {
  height: 16px;                 /* Fixed, NOT auto */
}
.nav-logo-sub {
  margin-top: 4px;              /* Explicit spacing */
}
```

**Iterations to fix:** 10+ rounds — each "fix" created a new problem

---

## Pitfall #6: Inline max-width on Paragraphs (Severity: MEDIUM)

**Symptom:** Some paragraphs are narrower than surrounding content, creating visual misalignment.

**Root Cause:** During initial content creation, individual `<p>` tags got inline styles like `max-width: 700px`. These were probably copy-pasted from a template and never cleaned up.

**Detection:** Search for pattern `<p style="[^"]*max-width:\d+px`.

**Fix:** Remove all inline `max-width` from content paragraphs. If width constraint is needed, apply at parent container level.

**Scale found:** 20+ instances scattered across multiple chapters (brand story, audience description, philosophy sections, etc.)

---

## Pitfall #7: Emoji Rendering as Boxes (Severity: MEDIUM)

**Symptom:** Unicode emoji (especially Unicode 12+, 2019+) display as □ tofu boxes on Windows browsers.

**Root Cause:** Windows font fallback chain doesn't include a font supporting newer emoji. Characters like 🧠🧹🤖🤝🪨🧪🤲🧭🦶🧑 show as boxes.

**Fix:** Replace all emoji with inline SVG icons. Create a simple SVG icon set for common brand manual icons (brain, tools, robot, handshake, etc.). For ZWJ sequences (family emoji 👨‍👩‍👧‍👦 → 👪), also replace with SVG.

**Scope:** 23 emoji replacements in a single manual.

---

## Pitfall #8: Gauge/Chart Direction Reversed (Severity: MEDIUM)

**Symptom:** Data visualization gauge shows pointer pointing to RED zone when value is 85 (should be GREEN/good).

**Root Cause:** Arc drawing direction confusion. SVG arc path `M 20 100 A 80 80 0 0 1 180 100` draws from left to right. If color zones were defined left=green/right=red, but the semantic expectation is left=bad(right)/right=good(green), colors appear backwards.

**Fix:**
- Define zones in correct semantic order: **Left = Red (bad) → Center = Yellow (caution) → Right = Green (good)**
- Verify needle angle matches the value (85% should be at ~right side of arc)
- Place value TEXT below the pivot point, away from needle path
- Draw needle AFTER (after in DOM = painted on top of) colored arcs

**Correct structure:**
```html
<svg>
  <!-- 1. Background arc (gray) -->
  <!-- 2. Red zone (left, 0-50%) -->
  <!-- 3. Yellow zone (center, 50-80%) -->
  <!-- 4. Green zone (right, 80-100%) -->
  <!-- 5. Needle line (on top) -->
  <!-- 6. Center circle (on top of needle base) -->
  <!-- 7. Value text (below everything) -->
</svg>
```

---

## Pitfall #9: Inconsistent Device Mockup Sizes (Severity: LOW)

**Symptom:** Two phone mockup frames in an App UI section have different heights/sizes.

**Root Cause:** One uses `min-height: 740px`, other uses `min-height: 680px`. Content length differences cause visible size mismatch.

**Fix:** Standardize ALL device mockups to identical dimensions:
```css
.device-frame {
  width: 375px;
  height: 740px;      /* Fixed, NOT min-height */
  /* ... */
}
.device-screen {
  min-height: 680px;  /* Inner scrollable area */
  overflow-y: auto;
}
```

---

## Pitfall #10: Version Record Table Overflow (Severity: LOW)

**Symptom:** Version history table content overflows its white background container.

**Root Cause:** Long change descriptions in table cells push beyond container bounds. No `table-layout: fixed` or `overflow: hidden`.

**Fix:**
```css
.version-table {
  table-layout: fixed;
  width: 100%;
}
.version-table td {
  overflow: hidden;
  text-overflow: ellipsis;
}
.version-table-container {
  overflow: hidden;
}
```
Set column widths: Version (50px), Date (80px), Changes (flex).

---

## Pitfall #11: CSS Specificity Wars (Severity: HIGH)

**Symptom:** Style changes don't take effect despite being present in file. DevTools shows rule being crossed out.

**Root Cause:** In a 15,000-line CSS block, multiple rules target same selector with different specificity. Later rules may override earlier ones, and `!important` declarations create un-overridable rules that can't be fixed by adding more CSS.

**Prevention:**
1. Organize CSS in clear order (Base → Layout → Components → Utilities → Safety Nets)
2. Use `!important` ONLY in the Safety Net section (last in file)
3. Never use `!important` in component-level CSS
4. When debugging, use browser DevTools Computed panel to see which rule wins
5. Search ENTIRE file before adding any property to check for conflicts

---

## Pitfall #12: Chapter Renumbering Cascade (Severity: MEDIUM)

**Symptom:** After inserting/deleting a chapter, navigation links point to wrong sections, part dividers show incorrect subtitles, cross-references broken.

**Root Scope of a single chapter insert:**
1. Section ID (`id="chXX-slug"`)
2. Section number display (`XX — Part Name`)
3. Navigation sidebar link (`href="#chXX-slug"`)
4. Part divider subtitle (if crossing part boundary)
5. Any cross-references ("see Chapter XX")
6. Version history entry

**Fix:** After any chapter reorganization, run global search-and-replace for the affected number range. Better: use a script or systematic approach rather than manual editing.

---

## Prevention Checklist

### Typography
- [ ] Search all `word-break` declarations — no contradictions
- [ ] Search all `overflow-wrap` declarations — no contradictions  
- [ ] Body text: `normal`; Headings: `keep-all`
- [ ] No inline `max-width` on content `<p>` tags
- [ ] No `text-align: justify` on CJK text
- [ ] Short titles have `white-space: nowrap`

### SVG / Logo
- [ ] All logo SVGs with negative-coord viewBox have explicit dimensions
- [ ] All logo SVGs have `overflow: visible` (3 places)
- [ ] All symbol paths use `currentColor` (not hardcoded colors)
- [ ] Nested SVGs use `<use>` + transform, not nested `<svg>`
- [ ] No `height: auto` on nav bar logo

### Layout
- [ ] Nav bar: flex-start alignment, explicit gaps/margins
- [ ] Device mockups: identical dimensions
- [ ] Tables: fixed layout + overflow handling
- [ ] Dark mode sections: same typography as light mode

### Content
- [ ] All chapters numbered correctly (sequential, no gaps)
- [ ] Nav sidebar links match section IDs
- [ ] Part dividers match their chapter ranges
- [ ] Version history updated
- [ ] No emoji above Unicode 11 (2018)
- [ ] All images use relative paths or data URIs

### Safety Nets
- [ ] CSS safety net matches JS safety net (same properties, same values)
- [ ] No contradictory `!important` rules
- [ ] Safety net placed at END of CSS/JS blocks

---

## Pitfall #13: Logo Format Migration — PNG to SVG (Severity: CRITICAL)

**Symptom:** Logo在不同缩放级别下模糊、锯齿、或颜色无法随深/浅背景自动切换。

**Root Cause（v2.3前）:** 使用PNG图片作为Logo，导致缩放失真、无法CSS切换颜色、每种场景需单独导出PNG、变体管理混乱。

**Fix（v2.3重大架构升级，#19字体许可陷阱关联）:**
全部Logo替换为**内联SVG矢量系统**：图标→`<symbol>`+path / 品牌字体→opentype.js从TTF提取路径 / Slogan→同样转路径 / 组合变体→`<use>`嵌套。5个Symbol变体：icon/wordmark/slogan/full/full-slogan。

**迭代轮次:** v2.3引入后经历了v2.4→v2.9共**6轮调优**

---

## Pitfall #14: Secondary Color Collision with Competitor (Severity: HIGH)

**Symptom:** 品牌副色与主要竞品主色几乎一致，像"竞品的子品牌"。

**Root Cause（v3.2-v3.5）:** 选色前未做竞品配色审计。初选某青色，后发现主要竞品主色调也是青色系。

**修复过程（3轮替换！）：**

| 轮次 | 副色 | 结果 |
|------|------|------|
| v3.3 | Violet紫罗兰 #8B5CF6 | 用户不喜欢 |
| v3.4 | RoseRed/Lime/Sky/CoralRose候选 | 全部否决 |
| v3.5最终 | 天空蓝 #0EA5E9 | ✅ 通过 |

**预防：** 先做11+竞品色彩审计 → 主色+副色组合必须独特可辨识 → 撞车提供3-4组备选 → grep确认零残留(≈40处)

---

## Pitfall #15: Brand Story Tone Mismatch (Severity: MEDIUM)

**Symptom（v6.2第4版重写）:** 用户反馈品牌故事中"门外汉/局外人/笨功夫"等表述让人感觉不专业，**增加信任成本而非降低**。

**Fix:** 彻底重写叙事角度——删除示弱表述 → 替换为"被问题打动、全力以赴" → 核心金句："最好的答案，来自最认真的倾听"

**教训：** B2C硬件产品的信任建立靠专注和专业，不是谦卑示弱

---

## Pitfall #16: CSS Syntax Errors Silent Failure (Severity: HIGH)

**Symptom（v2.9审查）:** 大段CSS完全不生效但浏览器无报错。原因：`position:relative:overflow:visible`（冒号代替分号），浏览器静默跳过整个声明块。15000行CSS中极难发现。同次还发现Windows不支持Unicode 12+ emoji需替换。

---

## Pitfall #17: overflow:hidden Silently Clipping Content (Severity: CRITICAL)

**Symptom（v2.8/v3.0多次出现）:** 某些区域内容被神秘裁剪（文字/SVG/装饰线看不到但DOM存在）。实际受影响：Visual Templates Roll-up被吞、包装盒Logo截断、封面标题裁切。

**Fix:** 全文搜索所有overflow:hidden逐个评估 → 不必要的改为visible

---

## Pitfall #18: Version History Table Structural Corruption (Severity: MEDIUM)

**Symptom（v2.7/v2.9）:** 版本记录表嵌套tr、缺失版本号、幽灵空行。根因：最频繁修改区域，复制粘贴带入旧结构、误删标签、多轮协作产生重复条目。

---

## Pitfall #19: Font Licensing Trap (Severity: HIGH)

**Symptom（贯穿v2.x-v3.x）:** Logo使用付费商业字体(Eras Bold ITC ~$41/台)，Web加载违反许可。
**解法：** Logo/Slogan→SVG路径嵌入(不需Web许可) + 正文标题→SIL OFL免费字体(Space Grotesk/Inter/Noto Sans SC)

---

## Pitfall #20: Large-Scale CSS Variable Rename Cascade (Severity: HIGH)

**Symptom（v3.3→v3.5）:** 更换副色时全局重命名CSS变量(--aqua-*→--violet-*→--sky-*)，遗漏任何一处样式不一致。
**规模：** ≈40处/轮 × 3轮 = 120+处修改
**Fix：** IDE全局重命名(F2) + grep旧名确认零残留

---

## Full Version Experience Map (v1.0 → v7.5)

```
v1.0   ─── 初始版本：基础VI手册骨架
v2.0   ─── 新增：品牌语调/辅助图形/版式网格 + 增强色彩(CMYK/Pantone/WCAG)
v2.1   ─── 新增：邮件与通知设计系统
v2.2   ─── 新增：发布会演示 + 官网增强
v2.3 ⭐ [重大] Logo PNG→SVG矢量系统重构 (#13+#19)
v2.4   ─── SVG精确路径重新生成(opentype.js) (#1 首次暴露)
v2.5   ─── 全面审查修复(SVG比例/居中/Footer)
v2.6 ⭐ [重要] Slogan字体切换(#19 字体许可)
v2.7   ─── 全面审查(#18 版本表损坏)
v2.8   ─── 封面精调(#17 overflow裁切)
v2.9 ⭐ [重要] 通篇审查(#16 CSS语法/#7 Emoji/#17)
v3.0   ─── 再次通篇审查(emoji替换/overflow/SVG尺寸)
v3.1   ─── 封面最终精调(Companion图标对齐)
v3.2 ⭐ [重要] Nav Bar修复 + 竞品审计(#14 发现撞车!)
v3.3 ⭐ [重要] 副色Aqua→Violet (#20 第1次变量重命名)
v3.4   ─── test-symbols同步修复
v3.5 ⭐ [最终] 副色Violet→Sky Blue (#20 第2次,用户否决前两轮)
v4.0 ⭐ [重大] 新增6策略章节 + 导航重组 + 11品牌竞品审计
v5.0   ─── 全面排版修复(CSS类/编号/清除残留)
v6.0   ─── 修复乱码+emoji+逻辑重组(5分区架构确定)
v6.1   ─── 排版修复(封面/CSS类/Do-Don冲突/Part分隔器)
v6.2 ⭐ [重大] 品牌故事第4版重写(#15 语气调整)
v6.3   ─── [MASCOT]吉祥物章节 + 图片本地化
v6.4   ─── 导航栏重写 + 产品图确认
v6.5   ─── 导航栏裁切修复 + 产品效果图恢复
       ↓ ←──── SKILL.md 覆盖范围起点 ──→
v7.x   ─── CJK排版定型 / Nav Bar 10轮优化 / 批量截图修复
v7.5   ─── ✅ 最终验收版
```
⭐ = 关键决策点　# = 对应Pitfall条目

---

## Debugging Workflow When User Reports Issues

1. **Screenshot first** — look at what user sees, don't guess
2. **Identify exact element** — use browser DevTools if possible, otherwise search by text content
3. **Find ALL rules affecting that element** — grep for class name, tag name, inline style
4. **Check for conflicting rules** — same property, different values
5. **Check parent/container constraints** — max-width, overflow, display type
6. **Apply minimal fix** — one specific change targeting root cause
7. **Search for side effects** — did this fix break anything else?
8. **Update version** — bump number, document change
9. **Present for review** — let user verify visually
