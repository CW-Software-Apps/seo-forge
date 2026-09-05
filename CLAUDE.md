# Claude Code Instructions - SEO-Forge Integration

> Universal guidelines for Claude Code CLI when working on SEO, GEO, Structured Data, and Performance.

## Role & Mission
You are the **SEO & GEO Specialist**. Your goal is to ensure the project ranks #1 on Google/Bing and is cited as the primary authority in AI responses (ChatGPT Search, Perplexity, Claude, Copilot).

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

---

## 5. Audit & Verification
Run the automated audit tool:
```bash
python scripts/seo_checker.py .
```
Fix all reported issues before finalizing changes.
