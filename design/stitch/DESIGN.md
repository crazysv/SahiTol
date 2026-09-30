# SahiTol Design System and Visual Tokens

Derived from owner Google Stitch project `245073995801566548` (*SahiTol Collector Frontend*).

---
name: SahiTol Design System
colors:
  surface: '#fcf9f3'
  surface-dim: '#dcdad4'
  surface-bright: '#fcf9f3'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3ed'
  surface-container: '#f0eee8'
  surface-container-high: '#ebe8e2'
  surface-container-highest: '#e5e2dc'
  on-surface: '#1c1c18'
  on-surface-variant: '#57423b'
  inverse-surface: '#31312d'
  inverse-on-surface: '#f3f0ea'
  outline: '#8a726a'
  outline-variant: '#dec0b7'
  surface-tint: '#a23e18'
  primary: '#9f3c16'
  on-primary: '#ffffff'
  primary-container: '#bf542c'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb59c'
  secondary: '#735c00'
  on-secondary: '#ffffff'
  secondary-container: '#fed65b'
  on-secondary-container: '#745c00'
  tertiary: '#615a59'
  on-tertiary: '#ffffff'
  tertiary-container: '#7a7371'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdbcf'
  primary-fixed-dim: '#ffb59c'
  on-primary-fixed: '#390c00'
  on-primary-fixed-variant: '#822801'
  secondary-fixed: '#ffe088'
  secondary-fixed-dim: '#e9c349'
  on-secondary-fixed: '#241a00'
  on-secondary-fixed-variant: '#574500'
  tertiary-fixed: '#eae0de'
  tertiary-fixed-dim: '#cec4c3'
  on-tertiary-fixed: '#1f1b1a'
  on-tertiary-fixed-variant: '#4b4544'
  background: '#fcf9f3'
  on-background: '#1c1c18'
  surface-variant: '#e5e2dc'
typography:
  headline-xl:
    fontFamily: Sora
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
  headline-xl-mobile:
    fontFamily: Sora
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
  headline-lg:
    fontFamily: Sora
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 34px
  headline-lg-mobile:
    fontFamily: Sora
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
  headline-md:
    fontFamily: Sora
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 26px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 26px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '700'
    lineHeight: 22px
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 18px
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 16px
  margin: 16px
  space-xs: 4px
  space-sm: 8px
  space-md: 16px
  space-lg: 24px
  space-xl: 32px
---

## Brand & Style

This design system is built on a contemporary Indian vernacular aesthetic, combining the tactile familiarity of local scrap markets with digital clarity. The brand personality is grounded, approachable, reliable, and deeply functional. It evokes trust, honesty, and operational ease for both daily collectors in the field and yard managers.

We employ a tactile, high-contrast visual style that draws inspiration from traditional weigh-slips, ledger books, and hand-painted market signboards. Surfaces are high-contrast and clear, utilizing deep charcoal foundations paired with warm cream, grounded by terracotta and accented with raw brass. Typography acts as a primary structural element, balancing massive, expressive headings with ultra-legible functional labels designed for rapid scanning under harsh sunlight.

## Colors

The color palette uses earthy, high-contrast tones rooted in traditional Indian materials and ledger environments. 

- **Primary (Terracotta `#C85A32`):** Used for primary actions, critical interactive elements, and focal points. It communicates warmth and action.
- **Secondary (Raw Brass `#D4AF37`):** Applied as an accent for highlights, active states, and badge backgrounds.
- **Tertiary (Deep Charcoal `#2B2625`):** Used for high-contrast text, borders, and structured containers, ensuring maximum legibility outdoors.
- **Neutral (Warm Cream `#F9F6F0`):** The foundational canvas color, replacing cold clinical whites with a softer, paper-like warmth inspired by physical weigh-slips.

## Typography

Typography is optimized for dual-script usage, ensuring flawless rendering in Devanagari (Hindi/Marathi) alongside Latin script. We pair the geometric, bold character of `Sora` for expressive headlines with the warm, open readability of `Plus Jakarta Sans` for body text and functional labels.

Headlines scale down gracefully on mobile screens to prevent awkward wrapping, while body sizes and labels remain generous to accommodate field use under bright sunlight. Line heights are kept slightly elevated to support complex Devanagari matras and conjunct characters without clipping.

## Layout & Spacing

The layout model relies on a fluid grid system optimized primarily for mobile form factors, utilizing a 16px outer margin and 16px column gutters. 

Spacing is anchored around an 8px baseline grid rhythm to ensure consistent vertical stacking. Component padding and touch targets are exaggerated (`space-md` through `space-lg`) to prevent mis-taps by collectors operating heavy scales or working in outdoor environments.

## Elevation & Depth

Elevation is conveyed through bold, high-contrast outlines and structural flat planes rather than soft, ambient shadows. Inspired by printed ledgers and market signboards, surfaces use crisp 2px deep charcoal borders (`#2B2625`) to separate cards, sheets, and modal layers. 

Interactive items utilize subtle tonal shifts (shifting from warm cream to raw brass or terracotta) on press states, relying on stark visual boundaries and high color contrast to ensure the UI remains instantly parseable in glaring sunlight.

## Shapes

The shape language is sturdy and utilitarian with soft corners (`roundedness` level 1: 0.25rem base, 0.5rem for large containers). This prevents the interface from feeling overly corporate or sharp while maintaining the robust, industrial sensibility of warehouse equipment, weigh-slips, and ledger cards. Avoid pill shapes for primary containers; favor stable rectangles with controlled corner radii.

## Components

- **Buttons:** Chunky, high-target primary buttons using terracotta (`#C85A32`) with deep charcoal text or borders. Minimum height of 48px to accommodate field use. Secondary actions feature solid warm cream backgrounds with thick dark borders.
- **Input Fields:** Styled like ledger entry lines. High-contrast deep charcoal borders, warm cream fill, and large, clear labels placed externally above the input for scanning speed.
- **Cards:** Used for material batches and weigh-slips. Rendered with solid warm cream backgrounds, 2px solid charcoal borders, and distinct header zones reminiscent of paper slips.
- **Chips / Tags:** Compact status markers for material types (e.g., *Paper*, *Iron*, *Plastic*). High-contrast background fills using raw brass or terracotta accents with bold labels.
- **Checkboxes & Radios:** Oversized touch areas with thick square/circular outlines that fill solidly with primary terracotta when selected.
- **Ledger Tables:** Specialized component for listing collected items, weights, and rates, featuring high-contrast row dividers and bold numeric alignments.