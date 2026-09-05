# Universal Agent Guidelines (AGENTS.md) - SEO & GEO Engine

> This file instructs all AI coding agents (OpenCode, Cursor, Windsurf, Copilot, Antigravity, Aider) on mandatory SEO and GEO standards across this project.

## Core Rules & Architecture

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
