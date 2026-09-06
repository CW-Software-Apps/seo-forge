// ==============================================================================
// SEO-FORGE: Program.cs Integration Snippets for ASP.NET Core & Blazor (.NET 8/9/10)
// ==============================================================================

/*
1. SERVICE REGISTRATION (In your builder configuration):
-------------------------------------------------------
builder.Services.AddHttpClient<IIndexNowService, IndexNowService>();

2. ENDPOINT MAPPINGS (After app.UseRouting() / before app.Run()):
---------------------------------------------------------------
// Dynamic Robots.txt
app.MapGet("/robots.txt", (IConfiguration config) =>
{
    var host = config["IndexNow:Host"] ?? "cwsoftware.com.br";
    var content = $"""
    User-agent: *
    Allow: /
    Disallow: /admin/
    Disallow: /api/

    Sitemap: https://{host}/sitemap.xml
    """;
    return Results.Text(content, "text/plain");
});

// Dynamic Sitemap.xml (Minimal example)
app.MapGet("/sitemap.xml", (IConfiguration config) =>
{
    var host = config["IndexNow:Host"] ?? "cwsoftware.com.br";
    var today = DateTime.UtcNow.ToString("yyyy-MM-dd");
    var xml = $"""
    <?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://{host}/</loc>
            <lastmod>{today}</lastmod>
            <changefreq>daily</changefreq>
            <priority>1.0</priority>
        </url>
    </urlset>
    """;
    return Results.Content(xml, "application/xml", System.Text.Encoding.UTF8);
});

// IndexNow Verification File /{key}.txt
var indexNowKey = builder.Configuration["IndexNow:Key"];
if (!string.IsNullOrWhiteSpace(indexNowKey))
{
    app.MapGet($"/{indexNowKey}.txt", () => Results.Text(indexNowKey, "text/plain"));
}

3. INDEXNOW AUTO-NOTIFY (MANDATORY - the integration is dead without this!):
-----------------------------------------------------------------------
Registering the service in DI alone does NOTHING. You must dispatch pings
when public content is created/updated. Example for a blog service:

public class MarkdownBlogService : IBlogService
{
    private readonly IIndexNowService _indexNowService;

    public MarkdownBlogService(IIndexNowService indexNowService, ...)
    {
        _indexNowService = indexNowService;
        ...
    }

    public async Task SavePostAsync(BlogPost post, string culture = "en")
    {
        // ... save logic ...

        if (post.Visible) // only index public content
        {
            _ = _indexNowService.NotifyUrlsChangedAsync(
            [
                $"blog/{post.Slug}",
                $"pt/blog/{post.Slug}"
            ]); // fire-and-forget
        }
    }
}

4. INDEXNOW BOOTSTRAP (one-time bulk submission of EXISTING URLs):
-----------------------------------------------------------------------
Register and wire an admin-only button that submits all existing URLs once:

// Program.cs
builder.Services.AddHttpClient<IIndexNowService, IndexNowService>();
builder.Services.AddSingleton<IIndexNowBootstrapService, IndexNowBootstrapService>();

// Admin page (Blazor) - builds the URL list and submits in one batch:
var paths = new List<string> { "", "blog", "pt/blog" };
foreach (var slug in allVisibleSlugs)
{
    paths.Add($"blog/{slug}");
    paths.Add($"pt/blog/{slug}");
}
var count = await IndexNowBootstrap.SubmitPathsAsync(paths);

// Use GetLastBootstrapUtc() to show "last submitted" in the UI and warn
// before accidental re-submission (avoid IndexNow spam blocking).
*/

