# Cool Call Pro — WCAG 2.1 AA Accessibility Checklist

Use this checklist when creating new pages (via Python generators or manually) or editing existing ones. All rules are based on the WCAG 2.1 AA standard and the site's established patterns.

Lighthouse target: **100/100 Accessibility** (achieved on index, city, and contact pages as of 3 April 2026).

---

## HTML Document Structure

- [ ] `<html lang="en">` on every page
- [ ] `<meta charset="UTF-8" />`
- [ ] `<meta name="viewport" content="width=device-width, initial-scale=1.0" />`
- [ ] Unique, descriptive `<title>` (include city/state name for location pages)
- [ ] `<a href="#main-content" class="skip-link">Skip to main content</a>` as first element inside `<body>`
- [ ] `<main id="main-content">` wrapping primary content

## Heading Hierarchy

- [ ] Exactly **one `<h1>`** per page
- [ ] Headings never skip levels: h1 -> h2 -> h3 (no h1 -> h3)
- [ ] Footer uses `<h3 class="footer-heading">` for Resources / Company / Service Areas
- [ ] Content sections under `<h2>` can use `<h3>` for sub-sections
- [ ] No heading tags used purely for styling — use CSS classes instead

## Navigation & Landmarks

- [ ] `<nav role="navigation" aria-label="Main navigation">` on header nav
- [ ] `<nav aria-label="Breadcrumb">` with `<ol class="breadcrumb-list">` for breadcrumbs
- [ ] Last breadcrumb item has `aria-current="page"`
- [ ] `<footer class="footer">` semantic element for footer
- [ ] Hamburger button: `<button class="hamburger" aria-label="Menu">`

## Links & Buttons

- [ ] All links use descriptive text (not "click here" or "read more")
- [ ] Phone links use `href="tel:+18445821795"` format
- [ ] Decorative link arrows (like `->`) are part of the link text, not standalone
- [ ] Interactive elements use `<button>` for actions and `<a>` for navigation
- [ ] Header CTA starts with `aria-hidden="true" tabindex="-1"` (JS toggles on scroll)
- [ ] Links in body text MUST have `text-decoration: underline` to distinguish from surrounding text (WCAG 1.4.1)

## Images & Icons

- [ ] All `<img>` tags have descriptive `alt` attributes
- [ ] Decorative images use `alt=""` (empty alt)
- [ ] Inline SVG icons that are decorative must have `aria-hidden="true"`
- [ ] The mobile call bar SVG always has `aria-hidden="true"`
- [ ] Decorative step numbers (`<div class="step-number">`) must have `aria-hidden="true"`
- [ ] Jump-link dot separators (`<span class="jump-link-dot">`) must have `aria-hidden="true"`

## Color Contrast — CRITICAL

Minimum contrast ratios — **4.5:1 for normal text**, **3:1 for large text** (18px+ bold or 24px+ regular).

### Inline link colors on WHITE/LIGHT backgrounds

| Color Purpose | Use This Variable | Hex Value | Ratio on White |
|--------------|-------------------|-----------|---------------|
| Orange links in content | `var(--orange-dark)` | `#b53610` | 6.00:1 |
| Red emergency links | hardcoded `#d32f2f` | `#d32f2f` | 4.75:1 |
| Blue links / breadcrumbs | hardcoded `#0d5dc9` | `#0d5dc9` | 6.13:1 |

**NEVER use `var(--orange)` (`#d84315`) for inline link text** — it's 4.43:1 on white, which FAILS.
**NEVER use `var(--red)` (`#e53e3e`) for inline link text on light bg** — it's 3.93:1, which FAILS.
**NEVER use `var(--blue-light)` (`#4fa3ff`) for text on light bg** — it's 2.62:1, which FAILS.

### Section tags (`.section-tag`)

| Background | Color | CSS Rule |
|-----------|-------|----------|
| Light (white/gray-50) | `#0d5dc9` | Default in `.section-tag` |
| Dark (navy/`.section-dark`/`.page-hero`) | `var(--blue-light)` | `.section-dark .section-tag` / `.page-hero .section-tag` |

### Topbar and nav CTA

| Element | Background | Value |
|---------|-----------|-------|
| `.topbar` | `#cc3d12` | Slightly darker than `--orange`, 4.95:1 with white |
| `.btn-cta.nav-cta` | `#cc3d12` | Same as topbar |

### Footer text on navy (`#0a1628`)

| Element | Minimum Opacity | CSS Variable / Value |
|---------|----------------|---------------------|
| Footer body text | `rgba(255,255,255, 0.75)` | `.footer-bottom p` |
| Footer links | `rgba(255,255,255, 0.78)` | `.footer-col li a` |
| Footer contact span | `rgba(255,255,255, 0.75)` | `.footer-contact span` |
| Footer disclaimer | `rgba(255,255,255, 0.65)` | `.footer-disclaimer` |
| Inline footer `<strong>` | `rgba(255,255,255, 0.9)` | Inline style |

**Never** go below `rgba(255,255,255, 0.65)` for any text on the navy footer.

### Emergency link animation

The `emergencyPulse` animation must NOT drop opacity below **0.8** — at 0.7 the contrast fails on the dark header.

## Animations & Motion

- [ ] `css/style.css` includes `@media (prefers-reduced-motion: reduce)` at the bottom
- [ ] All animations (vibrate, pulse, bounce, shake) are CSS-based so the media query catches them
- [ ] JS scroll animations are gated behind `window.matchMedia('(prefers-reduced-motion: reduce)')` check
- [ ] Never add `animation` properties inline — always use CSS classes
- [ ] Animation keyframes must not reduce opacity below levels that would break contrast ratios

## Focus & Keyboard

- [ ] Global `:focus-visible` style exists in CSS (3px orange outline)
- [ ] Every element with `:hover` also has a matching `:focus` style
- [ ] Never use `outline: none` without a replacement — use `:focus:not(:focus-visible)` pattern
- [ ] All interactive elements are reachable via Tab key
- [ ] Focus order follows visual reading order

## Touch Targets

- [ ] All tappable elements are at least **44x44px** on mobile
- [ ] City chips: `min-height: 44px` in mobile media query

## FAQ Accordion Pattern

Every FAQ section must follow this ARIA pattern:

```html
<div class="faq-item">
  <button class="faq-q" aria-expanded="false" aria-controls="faq-SLUG-N">
    <span>Question text</span>
    <span class="faq-icon"></span>
  </button>
  <div class="faq-a" id="faq-SLUG-N">
    <div class="faq-a-inner">
      <p>Answer text</p>
    </div>
  </div>
</div>
```

- [ ] `aria-controls` on button matches `id` on the answer div
- [ ] IDs use format `faq-{page-slug}-{number}` (e.g., `faq-austin-tx-1`)
- [ ] JS toggles `aria-expanded` between `"true"` and `"false"` on click

## Forms (contact.html)

- [ ] Every `<input>`, `<select>`, `<textarea>` has a matching `<label for="id">`
- [ ] Required fields have `required` attribute
- [ ] Form has an `aria-live="polite"` region for status messages: `<div id="form-status" role="status" aria-live="polite" class="sr-only"></div>`
- [ ] JS updates `#form-status` text on submit success/failure

## Tables

- [ ] All data tables have `<thead>` with `<th>` headers
- [ ] Use `<tbody>` for data rows
- [ ] No tables used for layout

## CSS Variables

All color variables must be defined in `:root` before use:

```
--gray-50, --gray-100, --gray-200, --gray-300, --gray-400, --gray-500, --gray-700, --gray-900
```

If you reference a `var(--color)`, verify it exists in the `:root` block of `style.css`.

## Index.html Special Rule

The `index.html` page has the **entire CSS inlined** in a `<style>` tag (no external stylesheet link). After ANY change to `style.css`:

1. Regenerate `css/style.min.css`
2. **Also update the inline `<style>` block in `index.html`** with the new minified CSS

If you forget step 2, index.html will show old styles.

---

## Quick Test Checklist

Before deploying any page changes:

1. **Lighthouse**: Run Lighthouse accessibility audit — target **100**
2. **Tab test**: Can you Tab through all interactive elements with a visible focus indicator?
3. **Heading check**: Use browser HeadingsMap extension — are headings in order with no skips?
4. **Zoom test**: Does the page work at 200% browser zoom?
5. **Reduced motion**: In DevTools Rendering, enable "Emulate prefers-reduced-motion: reduce" — do animations stop?
6. **Contrast spot-check**: Inspect any new colored text in DevTools — does computed contrast meet 4.5:1?

---

*Last updated: 3 April 2026 — after WCAG 2.1 AA audit, remediation, and Lighthouse 100/100 verification.*
