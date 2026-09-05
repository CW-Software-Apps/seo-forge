---
name: content-seo
description: On-page SEO, semantic HTML5 structure, strict heading hierarchy (H1-H6), high-CTR title and meta description copywriting, search intent mapping, and accessible image optimization. Use for on-page audits, copywriting optimization, and semantic architecture.
---

# Content SEO & Semantic Architecture

> Actionable guidelines for on-page search engine optimization, semantic HTML5 structure, heading hierarchy, and high-CTR copywriting.

---

## 1. Search Intent Mapping

| Intent Type | User Goal | Page Format | Example Target Query |
|---|---|---|---|
| **Informational** | Learn or troubleshoot | Blog post, Tutorial, Documentation, Guide | "Como integrar Blazor com API C#" |
| **Commercial Investigation** | Compare solutions before buying | Comparison tables, Feature breakdown, Case study | "Melhor ERP para pequenas empresas 2026" |
| **Transactional** | Buy, register, subscribe | Pricing page, Demo request, Signup page | "Contratar CW Software licença" |
| **Navigational** | Find a specific brand or portal | Login page, About, Contact, Homepage | "CW Software login portal" |

---

## 2. Heading Architecture & Hierarchy (H1–H6)

1. **Exactly One `<h1>`**: Every page must have one, and only one, `<h1>` tag containing the core topic and primary target phrase.
2. **Never Skip Levels**: Do not jump from `<h2>` directly to `<h4>`.
3. **Semantic Hierarchy**:
   - `<h1>`: Main topic of the page.
   - `<h2>`: Major sections / pillar topics.
   - `<h3>`: Sub-topics supporting the parent `<h2>`.
   - `<h4>`–`<h6>`: Detailed points, table columns, or sub-components.

---

## 3. High-CTR Copywriting Formulas

### 3.1 Title Tags (`<title>` / `<PageTitle>`)
- **Length**: Between **50 and 60 characters**.
- **Structure**: `[Primary Keyword / Hook] - [Secondary Context] | [Brand]`

### 3.2 Meta Descriptions
- **Length**: Between **150 and 160 characters**.
- **Structure**: `[Pain point solved] + [Unique benefit] + [Clear CTA]`.

---

## 4. Image SEO & Accessibility

1. **Alt Attributes**: Every `<img>` tag must have a descriptive `alt` text explaining what the image displays in context.
2. **Decorative Images**: If an image is purely decorative, set `alt=""` and `aria-hidden="true"`.
3. **Explicit Dimensions**: Always specify `width` and `height` to prevent layout shifts (CLS).
4. **Native Lazy Loading**: Add `loading="lazy"` to all images below the fold.
