# IJR Website Redesign — Technical Plan

> Derived from the business team's `IJR_Website_Plan.docx`. This is an engineering
> plan mapping the requirements onto the existing Frappe app. Items needing a
> business/product decision are collected in **§9 Needs Your Attention**.

## 1. Current state of the codebase

The site is a **Frappe app** (`ijr`) with server-rendered Jinja pages under
`ijr/www/`, styled with a custom CSS and using **Shoelace** web components
(`sl-*`) + **Alpine.js** for client interactivity.

What already exists and can be reused:

- **Pages:** `rankings`, `state`, `indicator`, `compare`, `methodology`,
  `pictures` (this is the "IJR in Pictures" gallery), and the homepage
  (`_homepage.html`).
- **Downloads:** `IJR File` doctype + `IJR File Download` (tracking) +
  `/api/method/ijr.api.download?file_id=...` endpoint, which streams the file
  and logs the IP. A `Downloads` dialog in `templates/secondary-nav.html`.
- **Maps:** reusable India map includes (`templates/includes/india_map.html`,
  `map_with_hover.html`) — directly reusable for the Diversity interactive map.
- **Navigation:** there is **no global mega-menu** today. There's a page-level
  `secondary-nav` (Rankings/States/Indicators/Methodology) and a basic homepage
  nav. The header described in the doc is net-new.

The central gap: **`IJR File` is a flat record** — only `title`, `file`,
`published`, `order`. It has **no concept of report, type, year, language, or
state**. Almost every screen in the requirements is a *filtered view over
files*, so the data model is the heart of this project.

## 2. Architectural approach

Keep the existing stack (Frappe + Jinja + Shoelace + Alpine). Do **not**
hardcode per-year state lists / language sets into templates — model them as
**metadata on each file** so the filter UIs are generated from data. This makes
the "2025 has 15 states in 9 languages, 2022 has 7 states in 2 languages"
behaviour fall out of the data automatically and lets the business team add the
2027 report without a code change.

Two layers:

1. **Data model** (doctypes) — the source of truth for every downloadable asset
   and every piece of editorial content.
2. **Presentation** (www pages + a shared mega-menu template + Alpine filter
   components) — thin, data-driven views.

## 3. Data model (the core work)

### 3.1 Extend `IJR File` into a faceted asset

Add fields so every downloadable asset is self-describing:

| Field | Type | Purpose |
|---|---|---|
| `publication` | Link → **Publication** | IJR / Consumer Justice / Juvenile Justice / Budgets for Justice / Police Recruitment / Justice Dashboard / Diversity Study |
| `document_type` | Link → **Document Type** | Main Report, National Factsheet, State Factsheet, Executive Summary, Primer, Procedural Framework, Press Release, Backgrounder, Annexure, Press Kit |
| `year` | Link → **IJR Number** (or Int) | 2025 / 2022 / 2020 / 2019 / 2024 / 2023 |
| `language` | Link → **Language** | English, Hindi, Bengali, Gujarati, Kannada, Malayalam, Tamil, Marathi, Telugu (extensible) |
| `state` | Link → **State** | for state factsheets / state press releases; blank = national |
| `press_kit_section` | Select | National / State / Additional / Backgrounder (drives the Press Kit tray grouping) |
| `published`, `order` | (existing) | |

These are **Link fields to small master doctypes** (`Publication`, `Document
Type`, `Language`) rather than hardcoded Selects, so the business team manages
the option lists without code changes.

### 3.2 New master doctypes

- **Publication** — name, slug, description, ordering, "is special study" flag.
- **Document Type** — label, slug, applies-to (which publications), ordering.
- **Language** — label, code, native name, ordering.
- (Optional) **Backgrounder Theme** — the 9 thematic backgrounders (Police,
  Prisons, Judiciary, Legal Aid, Human Resources, Diversity, Trends, Technology,
  SHRC). Could also be modelled as a `Document Type` + `theme` tag.

### 3.3 New editorial / link doctypes (Media + Blogs + About)

The Media and Blogs sections are lists of (mostly external) links, not file
downloads — they need their own content types:

- **Blog Post** — recommend **reusing Frappe's built-in Blog module** (Blog
  Category + Blog Post) rather than hand-rolling. Gives listicle feed, slugs,
  authors, SEO for free.
- **Op-Ed / Article** — title, external URL (substack/column), author, date,
  thumbnail. (See §9 — "need to take a call" on substack.)
- **Media Coverage** — title, outlet, external URL, year (for the yearwise
  sidebar archive).
- **Report Coverage** — same as above + `report` tag (IJR / CJR / JJ) for the
  filter.
- **Team Member**, **Partner** — for About Us (name, photo, role, bio, link).
- **Contact** — likely a static page or Frappe Web Form.

## 4. Global header & mega-menu

New shared template (e.g. `templates/includes/main-nav.html`) included by
`web.html`, fixed to the top, with hover-expanded mega menus. Built with
Alpine.js for hover/focus state and Shoelace for icons; CSS for the 4-column
grid.

Menu structure (from the doc):

- **Logo** → Home.
- **Reports** → 4-column mega menu: *IJR* (Main Report, National Factsheet,
  State Factsheet, Executive Summary) · *Other Reports* (Consumer Justice,
  Juvenile Justice, Budgets for Justice, Police Recruitment) · *Special Studies*
  (Justice Dashboard, Election States' Diversity) · *Press Kits* (Consumer, JJ,
  Budgets, IJR 2025, IJR 2022).
- **Blogs** → listicle feed.
- **Media** → dropdown: Op-Eds & Articles, Media Coverage, Reports Coverage.
- **IJR in Pictures** → existing gallery.
- **Compare States** → existing compare page.
- **IJR Rankings** → existing rankings (+ Consumer Reports rankings).
- **About Us** → dropdown: Team Profiles, Partners, Contact Us.

The menu can be hardcoded in the template (simplest) or driven by a
**Navigation Settings** singleton if the business team wants to edit it. Mobile
behaviour (the doc only describes desktop hover) needs a collapsed/accordion
variant — flagged in §9.

## 5. Page build plan

| Page | Route | Approach |
|---|---|---|
| Reports — **IJR** | `/reports/ijr` | Filter bar (Type / Year / Language) → query `IJR File`. Conditional **Press Kit tray** when Type=Press Kit: National (9 lang buttons), State (per-year state grid + lang), Additional (SHRC / Small States), and the 3×3 Backgrounder grid for 2022. All data-driven off the file metadata. Alpine for conditional show/hide. |
| Reports — **Consumer Justice** | `/reports/consumer-justice` | 3 rows: Download (Eng/Hindi) · Interactive Dashboard link · View Press Kit (Type+Language filters). |
| Reports — **Juvenile Justice** | `/reports/juvenile-justice` | Same filter pattern as IJR (Type + Language). |
| Reports — **Budgets for Justice** | `/reports/budgets-for-justice` | Same filter pattern (Type + Language). |
| Reports — **Police Recruitment** | `/reports/police-recruitment` | Simple dual-button (Eng / Hindi). |
| Special — **Justice Dashboard (2024)** | `/special-studies/justice-dashboard` | Single download. |
| Special — **Diversity in Election States (2023)** | `/special-studies/diversity` | Interactive India map (reuse `india_map.html`); clicking a state reveals its press releases / factsheet / annexure. Fallback: plain per-state download list (see §9). |
| **Press Kits** | `/press-kits` | Horizontal tabs per topic → National grid by language + State dropdown filtering state×language simultaneously. Same underlying `IJR File` query. |
| **Media** | `/media/op-eds`, `/media/coverage`, `/media/reports-coverage` | Listicle / yearwise sidebar / filterable sidebar. Dynamic footer: latest 3 blog posts + 3 Instagram posts + social links. |
| **Blogs** | `/blogs` (or Frappe `/blog`) | Listicle feed from Blog module. |
| **About Us** | `/about/team`, `/about/partners`, `/contact` | List/grid from Team Member / Partner doctypes; Contact via Web Form. |

A shared **filter-bar Alpine component** + a shared **download-card macro**
should be built once and reused across all report pages to keep them thin.

## 6. Download & API

`ijr.api.download` already streams + tracks. Extensions needed:

- A whitelisted **query endpoint** (or Jinja helper) that returns published
  `IJR File` records filtered by publication / type / year / language / state,
  so the filter UIs can render server-side (preferred for SEO) or fetch live.
- Optional: a **bulk/zip download** for press kits (nice-to-have).
- Keep download tracking as-is.

## 7. Migration & content

- **Schema migration:** new fields/doctypes ship via fixtures + `bench migrate`.
  Existing `IJR File` rows need back-tagging with publication/type/year/language.
- **Content entry is the largest non-engineering cost:** every PDF
  (reports, factsheets, press releases across ~9 languages × ~15 states × multiple
  years, plus backgrounders and annexures) must be uploaded and tagged. This is
  hundreds of files. Recommend a **bulk import** (Data Import) from a spreadsheet
  the business team fills in, rather than manual entry.

## 8. Suggested phasing

1. **Phase 0 — Data model:** new doctypes + `IJR File` fields + back-tag existing
   files. Nothing visible yet; unblocks everything.
2. **Phase 1 — Global header/mega-menu** + Reports landing + the IJR report page
   (incl. Press Kit tray). Highest-value, exercises the whole pattern.
3. **Phase 2 — Other Reports, Special Studies, Press Kits** (reuse Phase 1
   components).
4. **Phase 3 — Media + Blogs + About Us** (new editorial doctypes / Frappe Blog).
5. **Phase 4 — Polish:** mobile menu, social/Instagram feed, SEO, old-URL
   redirects.

## 9. Needs your attention (decisions / risks)

**Data inconsistencies in the doc — need an authoritative source list:**

1. **State lists disagree between sections.** The IJR Press-Kit "15 states + NE"
   list (Jharkhand, Kerala, West Bengal…) is *different* from the "IJR 2025 Press
   Kit" 15-state list (Haryana, Punjab, Odisha…). Which is correct?
2. **"Kannada" is listed as a state** in two state lists — it's a language, not a
   state. Likely a typo; please confirm the intended state.
3. **"Andhra Pradesh & Telangana"** appears combined in the IJR 2025 list but
   separate elsewhere. Combined or separate?
4. The 2022 state list (7 states) and 2025 list differ by design (that's fine) —
   but we need the *exact* final list per year, per language, to tag files.

**Product decisions:**

5. **Op-Eds source** — the doc literally says *"Need to take a call"* on whether
   these link to an external team column vs Substack. Which?
6. **Blogs** — OK to reuse Frappe's built-in Blog module (recommended) vs a
   bespoke listicle?
7. **Diversity (2023) page** — interactive clickable map (more build) vs simple
   per-state download list (the doc offers both: *"or we can let it remain as it
   is"*). Which?
8. **Mega-menu management** — hardcoded in template (simplest) vs editable via a
   settings doctype for the business team?
9. **Mobile navigation** — the doc only specifies desktop hover behaviour. We'll
   design a mobile accordion; flag if there's a specific mobile design.
10. **Instagram feed** at the bottom of Media — needs an embed approach (official
    embed vs a third-party widget vs manual links). API access / tokens may be
    required. Same for the social links (Twitter/IG/LinkedIn/YT).
11. **Consumer Reports rankings** — the header mentions rankings for "IJR &
    Consumer Reports". Does the Consumer ranking data/page exist, or is it new?

**Project:**

12. **Design assets** — is there a visual design/mockup, or is this text doc the
    only spec? Affects effort significantly.
13. **Content readiness** — who supplies and tags the hundreds of PDFs, and by
    when? This is the critical-path dependency, not the code.
14. **URL/SEO** — redirects from current URLs to the new structure to avoid
    losing search ranking.
