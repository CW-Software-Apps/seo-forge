# /seo-fix - Autonomous SEO & GEO Remediation Loop

Execute the full autonomous SEO audit and repair cycle on this codebase:

1. Run the audit script:
   ```bash
   python scripts/seo_checker.py .
   ```
2. Read the output. If issues are found:
   - Inspect every file listed in `Affected files`.
   - In Blazor (`.razor`), inject the `<SeoHeader Title="..." Description="..." />` component immediately following the top directives.
   - Ensure every page has exactly one `<h1>`.
   - Ensure all `<img>` tags have descriptive `alt` attributes.
   - Verify `<PageTitle>` and meta descriptions are present.
3. Re-run `python scripts/seo_checker.py .`
4. Repeat until the checker returns `[OK] 100% PERFECT! No SEO issues found!`.
5. Present a concise summary of all files updated.
