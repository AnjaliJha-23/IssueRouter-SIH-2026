---
name: Civic Horizon
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#434655'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#747686'
  outline-variant: '#c4c5d7'
  surface-tint: '#2151da'
  primary: '#0037b0'
  on-primary: '#ffffff'
  primary-container: '#1d4ed8'
  on-primary-container: '#cad3ff'
  inverse-primary: '#b7c4ff'
  secondary: '#006c4a'
  on-secondary: '#ffffff'
  secondary-container: '#82f5c1'
  on-secondary-container: '#00714e'
  tertiary: '#004870'
  on-tertiary: '#ffffff'
  tertiary-container: '#006194'
  on-tertiary-container: '#b2d9ff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dce1ff'
  primary-fixed-dim: '#b7c4ff'
  on-primary-fixed: '#001551'
  on-primary-fixed-variant: '#0039b5'
  secondary-fixed: '#85f8c4'
  secondary-fixed-dim: '#68dba9'
  on-secondary-fixed: '#002114'
  on-secondary-fixed-variant: '#005137'
  tertiary-fixed: '#cce5ff'
  tertiary-fixed-dim: '#93ccff'
  on-tertiary-fixed: '#001d31'
  on-tertiary-fixed-variant: '#004b73'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  display-lg:
    fontFamily: Public Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Public Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.015em
  headline-xl:
    fontFamily: Public Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Public Sans
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 34px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Public Sans
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Public Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Public Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Public Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Public Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Public Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-lg:
    fontFamily: Public Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Public Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Public Sans
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  space-2xs: 0.125rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-base: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 3rem
  space-3xl: 4rem
  gutter-mobile: 1rem
  gutter-tablet: 1.5rem
  gutter-desktop: 2rem
  container-max: 80rem
---

## Brand & Style

This design system embodies the rigor of critical public infrastructure fused with the forward momentum of high-performance civic technology. It balances institutional authority with modern software clarity, eliminating bureaucratic friction to mobilize cross-sector innovation among government agencies, academic research centers, corporate CSR bodies, and citizens.

The visual style is **Corporate Modern with High-Density Technical Precision**. It draws on disciplined utility, optical cleanliness, structured micro-hierarchies, and meticulous informational transparency. Visual noise, decorative flourishes, and opaque algorithmic behaviors are systematically replaced by high-contrast metrics, verifiable data ribbons, and explicit state signaling.

Target audiences experience an interface that feels:
- **Authoritative & Legitimate:** Uncompromising adherence to accessibility (WCAG 2.1 AAA contrast targets), crisp structure, and institutional stability.
- **Empowering & Dynamic:** Actionable workflows (Discover, Cluster, Verify, Route, Build, Measure) that treat complex societal problems as solvable engineering and operational pipelines.
- **Transparent & Accountable:** Routing engines, algorithmic confidence bands, and evidence indices are surfaced directly in the UI with tactile, clear data artifacts.

## Colors

The palette establishes an immediate sense of institutional trust, mathematical integrity, and environmental accountability.

- **Primary (`#1d4ed8` - Civic Tech Cobalt):** Anchors primary calls-to-action, active workflow states, verified system vectors, and routing links.
- **Secondary (`#059669` - Impact Forest/Emerald):** Designates verified societal impact, validated challenge evidence, top-tier institutional clearances, and positive outcome deltas.
- **Tertiary (`#0284c7` - Algorithmic Sky):** Applied to live stream telemetry, computational indicators, cross-sector cluster groups, and assistive navigation elements.
- **Neutral (`#0f172a` - Deep Slate Obsidian):** Provides high-contrast typographic rendering across body text and primary headlines, paired with layered surfaces (`#ffffff`, `#f8fafc`, and `#f1f5f9`).

### Semantic State Applications
- **Surfaces & Layout:** Background canvas uses `#f8fafc`. Card interiors and active dialog canvases sit on `#ffffff`. Secondary panel recesses, side rails, and inactive stepper segments employ `#f1f5f9`.
- **System Borders:** Boundaries are strictly articulated with crisp slate lines using `#e2e8f0` (default) and `#cbd5e1` (interactive inputs, selected states, and metric cards).
- **Critical & Warning Feedback:** Alert flags, routing warnings, and delayed milestone alerts utilize `#dc2626` (destructive/critical) and `#d97706` (elevated review required).

## Typography

The typography uses **Public Sans** throughout headlines, body copy, and UI metadata. Developed originally for high-integrity public sector services, Public Sans provides exceptional legibility across dense data dashboards, civic form portals, and variable screen resolutions.

### Hierarchy & Application Rules
- **Display & Section Titles:** Display and `headline-xl` elements must strictly maintain tightened letter spacing (`-0.02em`) to command presence without occupying disproportionate vertical space.
- **Numbers & Metrics:** Quantitative indicators (match confidence percentages, citizen signature counts, and allocation funding values) use tabular number formatting (`font-feature-settings: 'tnum' 1`) to preserve linear alignment across comparative tables and cards.
- **Micro-Copy & Metadata:** Status indicators, step nodes, role badges, and criteria weights utilize uppercase or title-cased `label-sm` with widened tracking (`0.04em`) to maintain sharp legibility against tinted badge backgrounds.
- **Algorithmic Tracing:** Router IDs, transaction hashes, and routing rules apply `code-sm` (`JetBrains Mono`) for clear developer/analyst inspection.

## Layout & Spacing

The layout is built on a responsive 12-column fluid grid system bounded by a maximum container width of `80rem` (1280px) for standard workflow hubs and `96rem` (1536px) for data-intensive master routing matrices.

### Responsive Breakpoints
- **Mobile (0 – 639px):** 4 columns, `gutter-mobile` (16px) margins. Lateral card stacks collapse vertically. Workflow steppers convert from horizontal pipelines into pinned milestone chips with progress meters.
- **Tablet (640px – 1023px):** 8 columns, `gutter-tablet` (24px) margins. Workspace pipelines split into stacked 2-column modules. Router criteria panels dock into collapsible bottom/side sheets.
- **Desktop (1024px+):** 12 columns, `gutter-desktop` (32px) margins. Allows simultaneous rendering of the Master Societal Challenge data stream (7 columns) alongside the Router Match Breakdown and Action Panel (5 columns).

### Spatial Rhythm
Spacers strictly adhere to a 4px/8px incremental base rhythm. Vertical layout cadence uses `space-xl` (32px) to separate distinct analytical cards, while inner component padding strictly maintains `space-lg` (24px) for prominent interactive units and `space-md` (12px) for nested metric cells.

## Elevation & Depth

Visual hierarchy is maintained through a combination of crisp micro-borders and disciplined, tinted ambient shadows. Heavy skeuomorphism and opaque frosted effects are avoided to keep performance high and maintain accessibility.

### Depth Layers
- **Level 0 (Flat Canvas / Recessed):** `#f8fafc` background with `#f1f5f9` inset utility strips. Used for main viewports, inactive tabs, and timeline track backdrops. Border: None or `#e2e8f0`.
- **Level 1 (Surface Cards & Default Modules):** `#ffffff` solid background with a structural 1px perimeter border of `#e2e8f0`. Shadow: `0 1px 3px 0 rgba(15, 23, 42, 0.06), 0 1px 2px -1px rgba(15, 23, 42, 0.04)`.
- **Level 2 (Interactive Hover / Active Focus / Router Modals):** Triggered when hovering over role entry modules, router match cards, or verified challenge items. Solid `#ffffff` paired with border `#cbd5e1`. Shadow: `0 4px 6px -1px rgba(15, 23, 42, 0.08), 0 2px 4px -2px rgba(15, 23, 42, 0.05)`.
- **Level 3 (Floating Action Bars, Header Nav & Diagnostic Drawers):** High-priority overlays. Border: `#cbd5e1`. Shadow: `0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.03)`.

## Shapes

This design system uses a **Soft (Level 1)** geometric standard. Border radii are restrained to project institutional precision, organizational discipline, and clear boundaries:

- **Inputs, Buttons, and System Badges:** `rounded` (0.25rem / 4px) to retain an intentional, engineered silhouette.
- **Cards, Panels, and Match Breakdowns:** `rounded-lg` (0.5rem / 8px) to establish clear visual encapsulation without looking overly playful.
- **Drawers, Floating Overlays, and Outer Modals:** `rounded-xl` (0.75rem / 12px) for distinct separation from background surfaces.
- **Workflow Stepper Nodes & Verification Pills:** Fully circular / pill (`rounded-full`) exclusively when representing closed completion status, user avatars, or numerical pipeline badges.

## Components

### 1. Header & SIH 2026 Civic Indicator
- **Shell:** Fixed top surface, `#ffffff` with a bottom border in `slate-200` (`#e2e8f0`).
- **SIH 2026 Badge:** A compact badge featuring a 1px border in `blue-200`, a background of `blue-50`, text in `blue-700` (`label-sm`), and a subtle emerald dot marking the platform's active status.
- **Global Actions:** Role-switcher dropdown, notification bell with impact-priority filtering, and institutional authorization status.

### 2. Role Entry Cards
- **Roles:** Government Agency, Academic/University, Industry/CSR Partner, Citizen Innovator.
- **Structure:** `rounded-lg` cards with a 1px `slate-200` border, `#ffffff` background, and hover transitions shifting the border to `blue-600` alongside an elevation bump to Level 2.
- **Visuals:** Top-aligned monochrome icon container tinted with subtle role-specific accents (e.g., Cobalt for Government, Sky for Universities, Forest for CSR, Slate for Citizens), followed by an operational mandate description and active intake queue counts.

### 3. Stepper / Workflow Nodes
- **Pipeline Stages:** `Discover` → `Understand` → `Cluster` → `Verify` → `Route` → `Build` → `Measure`.
- **Active State:** Solid `blue-600` circular node with white tabular numeral, paired with a bold label and `blue-600` connecting track.
- **Completed State:** Solid `emerald-600` circle with a check icon, connected via an `emerald-500` progress bar.
- **Pending State:** `slate-100` circle with `slate-400` border, text in `slate-500`, and dashed connecting rail.

### 4. Master Societal Challenge Data Card
- **Header:** Challenge ID (`code-sm`), priority tier pill (e.g., `P1 - Critical Water Security`), and a verified civic authority seal.
- **Evidence Bar:** Dual-layer visual bar showing aggregated citizen reports versus validated field surveys, colored in `blue-600` and `sky-400`.
- **Confidence Matrix:** 3-column micro-grid displaying **Impact Magnitude (1-100)**, **Feasibility Score (%)**, and **Data Confidence (0.0-1.0)** with bold tabular typography.

### 5. Smart Router Match Breakdown Panel
- **Container:** Recessed `#f8fafc` container with an `#e2e8f0` border and an explicit header: "Algorithmic Routing Logic".
- **Criteria Rows:** Shows itemized matching criteria (Geographic Proximity, Domain Capability, CSR Grant Matching, Track Record) with clear weight ribbons (e.g., `40% Weight`).
- **Target Recipient Preview:** Matched stakeholder preview pill with direct "Route to Entity" button in primary blue.

### 6. Workspace Collaboration Team & Milestone Pipeline
- **Team Roster:** Overlapping 28px avatar row with institutional affiliation tags (e.g., "IIT Bombay", "Ministry of Jal Shakti").
- **Milestone Track:** Horizontal list with structured cells detailing deliverable titles, target dates, verification sign-offs, and allocation disbursements in tabular numeric format.

### 7. Form Controls & Buttons
- **Primary Buttons:** `#1d4ed8` fill, `#ffffff` text, 4px border radius, 40px default height, hover state `#1e40af`.
- **Impact Buttons:** `#059669` fill, `#ffffff` text, hover state `#047857`.
- **Input Fields:** `#ffffff` background, 1px `slate-300` border, slate-900 text, 4px focus ring with `2px` offset using `blue-600`.