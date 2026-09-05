---
name: technical-seo
description: Technical SEO, IndexNow protocol integration, Blazor SSR/Prerendering meta architecture, Core Web Vitals, dynamic sitemaps, robots.txt, and HTTP headers. Use for technical search engine optimization, instant crawl indexing, and web performance.
---

# Technical SEO & Crawlability Guide

> Modern technical SEO principles for high-performance web applications, specializing in **Blazor (.NET 8/9/10)**, the **IndexNow protocol**, and **Core Web Vitals**.

---

## 1. IndexNow Protocol (Instant Indexing)

IndexNow allows websites to notify search engines (Bing, Microsoft Copilot, ChatGPT Search, Yandex, Seznam, Naver) immediately when URLs are added, updated, or deleted.

### 1.1 Architecture
1. **API Key Generation**: Generate an 8–128 character hex string (e.g., `8b2c4a7e91f34d60b5e28a9c1f0d3e74`).
2. **Key Verification File**: Serve the key at the root of the domain: `https://yourdomain.com/{key}.txt` containing the key string as plain text.
3. **Endpoint Notification**: Send a `POST` request to `https://api.indexnow.org/indexnow` with the host and modified URLs.

### 1.2 ASP.NET Core / Blazor Implementation

#### Endpoint Key Verification (`Program.cs`)
```csharp
var indexNowKey = builder.Configuration["IndexNow:Key"] ?? "8b2c4a7e91f34d60b5e28a9c1f0d3e74";

// Serve /{key}.txt
app.MapGet($"/{indexNowKey}.txt", () => Results.Text(indexNowKey, "text/plain"));
```

#### Service Interface & Implementation
```csharp
public interface IIndexNowService
{
    Task NotifyUrlChangedAsync(string url, CancellationToken cancellationToken = default);
    Task NotifyUrlsChangedAsync(IEnumerable<string> urls, CancellationToken cancellationToken = default);
}

public class IndexNowService : IIndexNowService
{
    private readonly HttpClient _httpClient;
    private readonly IConfiguration _config;
    private readonly ILogger<IndexNowService> _logger;

    public IndexNowService(HttpClient httpClient, IConfiguration config, ILogger<IndexNowService> logger)
    {
        _httpClient = httpClient;
        _config = config;
        _logger = logger;
    }

    public Task NotifyUrlChangedAsync(string url, CancellationToken cancellationToken = default)
        => NotifyUrlsChangedAsync(new[] { url }, cancellationToken);

    public async Task NotifyUrlsChangedAsync(IEnumerable<string> urls, CancellationToken cancellationToken = default)
    {
        var key = _config["IndexNow:Key"];
        var host = _config["IndexNow:Host"] ?? "cwsoftware.com.br";
        var keyLocation = $"https://{host}/{key}.txt";

        var urlList = urls.Distinct().ToList();
        if (!urlList.Any()) return;

        var payload = new
        {
            host,
            key,
            keyLocation,
            urlList
        };

        try
        {
            var response = await _httpClient.PostAsJsonAsync("https://api.indexnow.org/indexnow", payload, cancellationToken);
            if (response.IsSuccessStatusCode)
            {
                _logger.LogInformation("IndexNow notification sent successfully for {Count} URLs.", urlList.Count);
            }
            else
            {
                _logger.LogWarning("IndexNow notification returned status {StatusCode}.", response.StatusCode);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to submit URLs to IndexNow.");
        }
    }
}
```

#### Automatic Persistence Hook
Call `IIndexNowService.NotifyUrlChangedAsync(pageUrl)` inside your command/service handlers whenever a public entity (page, blog post, product, landing page) is created, updated, or removed.

---

## 2. Blazor SSR & Prerendering Meta Architecture

Search engine bots (Googlebot, Bingbot) do not execute long interactive WebAssembly or WebSocket connections reliably. All primary SEO tags must be rendered during the **initial static HTML pass**.

### 2.1 `App.razor` Setup
Ensure the root layout includes the Blazor `HeadOutlet`:
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <base href="/" />
    <!-- Blazor HeadOutlet renders PageTitle and HeadContent from pages -->
    <HeadOutlet @rendermode="PageRenderMode" />
</head>
<body>
    <Routes @rendermode="PageRenderMode" />
    <script src="_framework/blazor.web.js"></script>
</body>
</html>
```

### 2.2 Reusable `<SeoHeader>` Component
Create `Components/Shared/SeoHeader.razor`:
```razor
@code {
    [Parameter, EditorRequired] public string Title { get; set; } = string.Empty;
    [Parameter, EditorRequired] public string Description { get; set; } = string.Empty;
    [Parameter] public string? CanonicalUrl { get; set; }
    [Parameter] public string? OgImage { get; set; }
    [Parameter] public string OgType { get; set; } = "website";
    [Parameter] public bool NoIndex { get; set; } = false;

    private const string SiteName = "CW Software";
    private const string DefaultOgImage = "https://cwsoftware.com.br/images/og-default.jpg";
}

<PageTitle>@($"{Title} | {SiteName}")</PageTitle>

<HeadContent>
    <meta name="description" content="@Description" />
    @if (NoIndex)
    {
        <meta name="robots" content="noindex, nofollow" />
    }
    else
    {
        <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
    }

    @if (!string.IsNullOrWhiteSpace(CanonicalUrl))
    {
        <link rel="canonical" href="@CanonicalUrl" />
        <meta property="og:url" content="@CanonicalUrl" />
    }

    <!-- Open Graph -->
    <meta property="og:site_name" content="@SiteName" />
    <meta property="og:title" content="@Title" />
    <meta property="og:description" content="@Description" />
    <meta property="og:type" content="@OgType" />
    <meta property="og:image" content="@(OgImage ?? DefaultOgImage)" />

    <!-- Twitter Cards -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="@Title" />
    <meta name="twitter:description" content="@Description" />
    <meta name="twitter:image" content="@(OgImage ?? DefaultOgImage)" />
</HeadContent>
```

---

## 3. Dynamic Robots.txt and Sitemap.xml

### 3.1 Dynamic `robots.txt` Endpoint
```csharp
app.MapGet("/robots.txt", () => 
    Results.Text(
        """
        User-agent: *
        Allow: /
        Disallow: /admin/
        Disallow: /api/
        
        Sitemap: https://cwsoftware.com.br/sitemap.xml
        """, 
        "text/plain"
    ));
```

### 3.2 Dynamic `sitemap.xml` Endpoint
```csharp
app.MapGet("/sitemap.xml", async (ISitemapService sitemapService) =>
{
    var sitemapXml = await sitemapService.GenerateXmlAsync();
    return Results.Content(sitemapXml, "application/xml", System.Text.Encoding.UTF8);
});
```

---

## 4. Core Web Vitals in Blazor

| Metric | Target | Focus in Blazor |
|---|---|---|
| **LCP** (Largest Contentful Paint) | `< 2.5s` | Prerender hero text & images, preload hero banner (`<link rel="preload" as="image">`), eliminate render-blocking JS. |
| **INP** (Interaction to Next Paint) | `< 200ms` | Keep Blazor event handlers responsive. Offload CPU-heavy computation from SignalR circuit. Use debouncing on inputs. |
| **CLS** (Cumulative Layout Shift) | `< 0.1` | Set explicit `width` and `height` on images and SVGs. Use skeleton loaders with reserved dimensions for async queries. |

### Font Display Optimization
Always enforce `font-display: swap;` in CSS to prevent invisible text during font loading (FOIT):
```css
@font-face {
    font-family: 'Inter';
    font-display: swap;
    src: url('/fonts/inter.woff2') format('woff2');
}
```

---

## 5. Security & Canonical HTTP Headers

Ensure the following headers are configured in production middleware:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Referrer-Policy: strict-origin-when-cross-origin`
- Canonical redirects: 301 redirect all HTTP to HTTPS and non-canonical domains (e.g. `http://cwsoftware.com.br` -> `https://cwsoftware.com.br`).

