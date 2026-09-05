# Claude Code Instructions - SEO-Forge Integration

> Universal guidelines for Claude Code CLI when working on SEO, GEO, Structured Data, and Performance.

## ⚡ Autonomous Remediation Protocol (Zero Terminal Commands for User)
When the user triggers `/seo-fix` or asks in natural language:
- *"audite o SEO deste projeto"* / *"audit SEO"*
- *"como tá o SEO?"* / *"what is the SEO score?"*
- *"corrija o SEO até 100%"* / *"fix all SEO issues"*

👉 **DO NOT ask the user to open a terminal or run scripts manually.**
👉 **Execute the full autonomous cycle:**
1. Execute `python scripts/seo_checker.py .` using your terminal tool in the background.
2. Read the output and `seo_report.md`.
3. If user asked for audit/score: present the Health Score and summary directly.
4. If user asked to fix/remediate:
   - In Blazor (`.razor`), inject `<SeoHeader Title="..." Description="..." />` after top directives (`@page`, `@inject`).
   - Fix missing `alt` attributes on `<img>` tags.
   - Ensure single `<h1>` per page without skipped heading levels.
   - Wire IndexNow if indicated in `seo_report.md`.
5. Re-run `python scripts/seo_checker.py .` to verify that score reached 100/100 A+.
6. Report the final success summary to the user.

---

## 1. Technical SEO Invariants
1. **Instant Indexing (IndexNow)**:
   - When pages/articles are created or updated, verify or implement the `IIndexNowService` notification to Bing/Copilot/ChatGPT Search.
   - Ensure the public key file `/{key}.txt` returns the plain text key.
2. **Blazor SSR & Prerendering**:
   - In Blazor (.NET), never rely on client-side JS rendering for `<title>` or `<meta>` tags. Use `<HeadOutlet />` in `App.razor` and `<SeoHeader />` in page components so search engine bots receive rendered metadata on the initial static HTTP response.
3. **Robots.txt & Sitemap.xml**:
   - Ensure `/robots.txt` points to `/sitemap.xml` and blocks private/admin routes.
   - Sitemaps must use valid ISO 8601 timestamps and canonical URLs.
4. **Core Web Vitals**:
   - LCP < 2.5s: Preload hero assets, avoid render-blocking CSS/JS.
   - INP < 200ms: Keep UI thread responsive.
   - CLS < 0.1: Explicit dimensions (`width`, `height`) on all images and embeds.

---

## 2. Schema Markup (JSON-LD)
- Always use `<script type="application/ld+json">`.
- Standard schemas: `SoftwareApplication`, `Organization`, `WebSite`, `FAQPage`, `BreadcrumbList`.
- Validate against Google Rich Results standards.

---

## 3. Social Metadata (Open Graph)
- Standard image dimensions: `1200 x 630 px` (Aspect ratio 1.91:1).
- Keep critical logos and text within the central `1000 x 520 px` safe zone.
- Provide full tags: `og:title`, `og:description`, `og:image`, `og:url`, `og:type`, `twitter:card` (`summary_large_image`).

---

## 4. Content & Heading Structure (H1–H6)
- **Strictly One `<h1>`** per page representing the core query and topic.
- **Never skip heading levels** (e.g. `<h2>` -> `<h4>` is forbidden).
- Use semantic HTML5 elements: `<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<footer>`.
- Title tag: 50–60 characters.
- Meta description: 150–160 characters with clear call-to-action (CTA).
