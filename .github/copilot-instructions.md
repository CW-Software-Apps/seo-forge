# GitHub Copilot Instructions for SEO-Forge

When writing, refactoring, or generating web components, pages, or backend routes:

- **Blazor & .NET**:
  - Always generate SEO metadata using `<PageTitle>` and `<HeadContent>`.
  - When creating public entities (pages, blogs, products), suggest triggering `IIndexNowService.NotifyUrlChangedAsync`.
  - Prefer the `<SeoHeader>` and `<JsonLd>` reusable components from CWSoftware.Web.Components.Shared.
- **HTML & Semantic Structure**:
  - Enforce single `<h1>` per page.
  - Never skip heading levels.
  - Include descriptive `alt` tags on `<img>` elements.
  - Enforce `og:image` dimensions (1200x630px).
- **Structured Data**:
  - Output standard JSON-LD formatted with `@context: "https://schema.org"`.

