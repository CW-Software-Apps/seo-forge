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

// Program.cs - automatic: the bootstrap service is a hosted service and runs
// ONCE on startup if no previous stamp exists (reads the project's own
// /sitemap.xml to build the URL list). No admin button or curl needed.
builder.Services.AddHttpClient<IIndexNowService, IndexNowService>();
builder.Services.AddSingleton<IIndexNowBootstrapService, IndexNowBootstrapService>();
builder.Services.AddHostedService<IndexNowBootstrapService>(p => (IndexNowBootstrapService)p.GetRequiredService<IIndexNowBootstrapService>());

// Optional manual re-submission API (protected by AdminPassword header):
app.MapPost("/api/seo/indexnow/bootstrap", async (IIndexNowBootstrapService bootstrap, IConfiguration cfg, HttpRequest request, List<string> paths) =>
{
    var adminKey = cfg["AdminPassword"] ?? Environment.GetEnvironmentVariable("AdminPassword");
    if (string.IsNullOrEmpty(adminKey) || request.Headers["x-admin-key"].FirstOrDefault() != adminKey)
        return Results.Unauthorized();
    var count = await bootstrap.SubmitPathsAsync(paths);
    return Results.Ok(new { submitted = count });
});

// Validation endpoint - validates the WHOLE pipeline (config, key file,
// sitemap, stamp, optional live API ping via ?ping=true):
app.MapGet("/api/seo/indexnow/validate", async (IIndexNowBootstrapService bootstrap, IConfiguration cfg, HttpRequest request, bool ping = false) =>
{
    var adminKey = cfg["AdminPassword"] ?? Environment.GetEnvironmentVariable("AdminPassword");
    if (string.IsNullOrEmpty(adminKey) || request.Headers["x-admin-key"].FirstOrDefault() != adminKey)
        return Results.Unauthorized();
    return Results.Ok(await bootstrap.ValidateAsync(pingApi: ping));
});

// GetLastBootstrapUtc() can be shown in the admin UI to display the last
// submission date and warn before an accidental re-submission.
*/

