#!/usr/bin/env python3
"""
Brand Manual HTML Validator
Validates common issues in single-file HTML brand manuals.

Usage:
  python validate-manual.py path/to/index.html

Exit codes: 0 = pass, 1 = warnings, 2 = errors
"""

import re
import sys
import html as html_module
from pathlib import Path


class ValidationResult:
    def __init__(self):
        self.errors = []   # Critical issues that WILL break rendering
        self.warnings = [] # Issues that MAY cause problems
        self.info_list = []     # Informational findings

    def error(self, msg, line=None):
        loc = f" (line {line})" if line else ""
        self.errors.append(f"[ERROR]{loc}: {msg}")

    def warn(self, msg, line=None):
        loc = f" (line {line})" if line else ""
        self.warnings.append(f"[WARN]{loc}: {msg}")

    def info_msg(self, info_msg, line=None):
        loc = f" (line {line})" if line else ""
        self.info_list.append(f"[INFO]{loc}: {info_msg}")

    @property
    def has_errors(self):
        return len(self.errors) > 0

    @property
    def has_warnings(self):
        return len(self.warnings) > 0

    @property
    def has_info(self):
        return len(self.info_list) > 0

    def print_report(self):
        for e in self.errors:
            print(e)
        for w in self.warnings:
            print(w)
        for i in self.info_list:
            print(i)
        print(f"\n{'='*50}")
        print(f"Total: {len(self.errors)} errors, {len(self.warnings)} warnings, {len(self.info_list)} info")


def validate(filepath):
    result = ValidationResult()
    content = Path(filepath).read_text(encoding='utf-8')
    lines = content.split('\n')

    # ========================================
    # CHECK 1: Contradictory word-break rules
    # ========================================
    has_keep_all = bool(re.search(r'word-break\s*:\s*keep-all', content))
    has_normal = bool(re.search(r'word-break\s*:\s*normal', content))
    if has_keep_all and has_normal:
        # Check if they're on different selector types (which is correct)
        body_rules = len(re.findall(r'(?:p|body|div|span|li|td)[^}]*word-break\s*:\s*normal', content))
        heading_rules = len(re.findall(r'(?:h[1-6]|section-title)[^}]*word-break\s*:\s*keep-all', content))
        if body_rules == 0 and heading_rules == 0:
            # Has both but not in correct pattern — likely conflict
            result.warn("Both 'word-break: keep-all' and 'word-break: normal' found — verify they target different element types")

    # ========================================
    # CHECK 2: overflow-wrap contradictions
    # ========================================
    ow_break_word = len(re.findall(r'overflow-wrap\s*:\s*break-word', content))
    ow_normal = len(re.findall(r'overflow-wrap\s*:\s*normal', content))
    if ow_break_word > 0 and ow_normal > 0:
        result.warn(f"Found both 'overflow-wrap: break-word' ({ow_break_word}x) AND 'overflow-wrap: normal' ({ow_normal}x) — these may conflict")

    # ========================================
    # CHECK 3: Global * selector with keep-all
    # ========================================
    for i, line in enumerate(lines, 1):
        if re.search(r'\*\s*\{[^}]*word-break\s*:\s*keep-all', line):
            result.error("Global '*' selector with 'word-break: keep-all' will break paragraph text flow", i)

    # ========================================
    # CHECK 4: text-align justify on CJK
    # ========================================
    for i, line in enumerate(lines, 1):
        if re.search(r'text-align\s*:\s*justify', line) and not re.search(r'comment|/\\*', line.lower()):
            result.warn("text-align: justify creates ugly character spacing in CJK text", i)

    # ========================================
    # CHECK 5: Inline max-width on <p> tags
    # ========================================
    p_maxwidth_count = len(re.findall(r'<p[^>]*style="[^"]*max-width\s*:\s*\d+px', content))
    if p_maxwidth_count > 0:
        result.warn(f"Found {p_maxwidth_count} <p> tags with inline max-width — this causes width mismatch with surrounding content")

    # ========================================
    # CHECK 6: SVG height:auto with negative viewBox
    # ========================================
    has_negative_viewbox = bool(re.search(r'viewBox="[^"]*-[\d.]+-', content))  # Negative Y coord
    svg_auto_height = len(re.findall(r'<svg[^>]*height\s*=\s*"auto"', content))
    if has_negative_viewbox and svg_auto_height > 0:
        result.error("SVG elements have height='auto' but symbols use negative-coordinate viewBox — logo may render invisible")

    # ========================================
    # CHECK 7: SVG without overflow:visible
    # ========================================
    svg_tags = re.findall(r'<svg([^>]*)>', content)
    for svg_attrs in svg_tags:
        if 'overflow' not in svg_attrs.lower() and 'display' not in svg_attrs.lower():
            pass  # Many SVGs are fine without explicit overflow
    # Check nav bar SVG specifically
    nav_svg_pattern = re.findall(r'nav-logo-wordmark[^>]*<svg([^>]*)>', content, re.DOTALL)
    if nav_svg_pattern:
        for attrs in nav_svg_pattern:
            if 'overflow' not in attrs.lower():
                result.warn("Nav bar SVG missing 'overflow: visible' — logo might clip with negative-coordinate viewBox")

    # ========================================
    # CHECK 8: Unicode 12+ emoji (may show as boxes on Windows)
    # ========================================
    emoji_ranges = [
        (0x1F9D0, 0x1FAF7),   # Unicode 12-15 emoji range (approximate)
    ]
    emoji_in_text = []
    for i, line in enumerate(lines, 1):
        # Skip style/script/tag lines
        if '<' in line and ('style' in line.lower() or 'script' in line.lower()):
            continue
        for char in line:
            cp = ord(char)
            if any(start <= cp <= end for start, end in emoji_ranges):
                if char not in emoji_in_text:
                    emoji_in_text.append(char)

    if emoji_in_text:
        unique = set(emoji_in_text)
        result.warn(f"Found {len(unique)} potential Unicode 12+ emoji characters that may render as □ on Windows: {''.join(unique[:5])}{'...' if len(unique)>5 else ''}")

    # ========================================
    # CHECK 9: Missing alt / aria-label on SVG logos
    # ========================================
    svg_without_label = len(re.findall(r'<svg(?![^>]*aria-label)', content[:50000]))  # Check first 50k chars
    role_img_count = len(re.findall(r'role=["\']img["\']', content))
    aria_count = len(re.findall(r'aria-label=', content))
    if role_img_count > aria_count + 2:
        result.info_msg(f"Found {role_img_count} role='img' but only {aria_count} aria-label — consider adding accessibility labels")

    # ========================================
    # CHECK 10: Version consistency
    # ========================================
    version_matches = re.findall(r'v\d+\.\d+', content)
    if version_matches:
        versions = set(version_matches)
        if len(versions) > 1:
            result.warn(f"Multiple version numbers found: {versions} — should be consistent")

    # ========================================
    # CHECK 11: Safety net CSS vs JS agreement
    # ========================================
    css_has_break_word = 'break-word' in content.split('</style>')[0] if '</style>' in content else False
    js_has_break_word = False
    if '<script>' in content:
        script_sections = content.split('<script>')
        for section in script_sections[1:]:
            js_part = section.split('</script>')[0] if '</script>' in section else ''
            if "overflowWrap = 'break-word'" in js_part or 'overflowWrap = "break-word"' in js_part:
                js_has_break_word = True
    if css_has_break_word and js_has_break_word:
        result.error("Both CSS and JS safety nets contain 'break-word' — this contradicts 'keep-all' rules")

    # ========================================
    # CHECK 12: Chapter numbering gaps
    # ========================================
    chapter_ids = sorted(set(re.findall(r'id="(ch(\d+)-[^"]*)"', content)), key=lambda x: int(x[1]))
    if chapter_ids:
        nums = sorted([int(x[1]) for x in chapter_ids])
        expected = list(range(1, max(nums)+1))
        missing = set(expected) - set(nums)
        if missing:
            result.warn(f"Chapter numbering gaps detected, missing chapters: {sorted(missing)}")

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate-manual.py <index.html>")
        sys.exit(2)

    filepath = sys.argv[1]
    if not Path(filepath).exists():
        print(f"File not found: {filepath}")
        sys.exit(2)

    print(f"Validating: {filepath}")
    print("=" * 50)

    result = validate(filepath)
    result.print_report()

    if result.has_errors:
        sys.exit(2)
    elif result.has_warnings:
        sys.exit(1)
    else:
        print("[PASS] All checks passed!")
        sys.exit(0)


if __name__ == '__main__':
    main()
