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
*/
