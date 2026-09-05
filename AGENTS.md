# Universal Agent Guidelines (AGENTS.md) - SEO-FORGE Engine

> This file instructs all AI coding agents (**OpenCode**, **Claude Code**, **Cursor**, **Windsurf**, **GitHub Copilot**, **Antigravity**) on mandatory SEO, GEO, and automated remediation standards.

---

## ⚡ AUTONOMOUS REPAIR PROTOCOL (The Primary Workflow)

When the user asks to **"fix seo"**, **"auto seo"**, **"/seo-fix"**, or **"corrija todo o SEO até 100%"**:

1. **Step 1 - Audit**: Execute `python scripts/seo_checker.py .`
2. **Step 2 - Analyze**: Parse the list of `Affected files` and reported issues:
   - Missing `<title>` / `<PageTitle>`
   - Missing `<meta name="description">`
   - Missing Open Graph tags (`og:title`, `og:description`, `og:image`)
   - Multiple or missing `<h1>` tags
   - `<img>` tags missing `alt` attributes
3. **Step 3 - Remediate Iteratively**:
   - For **Blazor (`.razor`)**: Inject `<SeoHeader Title="..." Description="..." />` from `CWSoftware.Web.Components.Shared` right after the top directives (`@page`, `@inject`, etc.).
   - For **HTML/React/Next.js**: Add `<title>`, `<meta name="description">`, and `<link rel="canonical">`.
   - Add descriptive `alt` tags to all images.
4. **Step 4 - Validate**: Run `python scripts/seo_checker.py .` again.
5. **Step 5 - Done**: Repeat until `passed == true` (100% clean / 0 issues).

---

## Core Rules & Invariants

### 1. Multi-Framework Metadata
- **Blazor (.NET)**:
  - Every page (`.razor` with `@page`) MUST define `<PageTitle>` and `<meta name="description">` via `<HeadContent>` or `<SeoHeader Title="..." Description="..." />`.
  - In `App.razor`, verify `<HeadOutlet @rendermode="PageRenderMode" />`.
- **HTML / Next.js / React**:
  - Always export metadata (Next.js App Router `metadata` object or Pages Router `<Head>`).
  - Provide `<link rel="canonical" href="..." />`.

### 2. IndexNow Protocol
- When building content management, blog, or product catalog features, always dispatch URL updates to `IIndexNowService.NotifyUrlChangedAsync(url)`.
- Ensure `/{key}.txt` endpoint is accessible.

### 3. Open Graph & Social Cards
- Must include:
  - `og:site_name`, `og:title`, `og:description`, `og:image`, `og:url`, `og:type`
  - `twitter:card` (`summary_large_image`), `twitter:title`, `twitter:description`, `twitter:image`
- All images must use absolute URLs (`https://...`) and `1200x630px` resolution.

### 4. Structured Data (JSON-LD)
- Inject `<script type="application/ld+json">` for entities (`Organization`, `SoftwareApplication`, `FAQPage`, `BreadcrumbList`).
- In Blazor, use `<JsonLd SchemaData="@schema" />`.

### 5. Content Hierarchy
- Exactly **one `<h1>`** per page.
- Do not jump heading levels (e.g. `<h2>` directly to `<h4>`).
- Every `<img>` requires a meaningful `alt` attribute describing the content. Purely decorative images must use `alt=""` and `aria-hidden="true"`.
