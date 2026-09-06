using System.Text.RegularExpressions;
using CWSoftware.Web.Services;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace CWSoftware.Web.Services;

/// <summary>
/// SEO-FORGE: One-time (repeatable on demand) bulk submission of every public
/// URL to IndexNow. Bootstraps the integration so Bing, Copilot and ChatGPT
/// Search become aware of all EXISTING content without waiting for organic
/// crawls.
///
/// Fully automatic: registered as a hosted service, it runs once on startup
/// (with delay + retries while the server warms up) if no previous bootstrap
/// stamp exists. It reads the project's own /sitemap.xml to build the URL list,
/// so it works generically for any ASP.NET Core / Blazor project. A timestamp
/// stamp prevents accidental re-submission (the IndexNow spec forbids spamming
/// unchanged URLs - the key can get blocked).
///
/// Manual re-submission is still available via the admin-only bootstrap API
/// (protected with the project's AdminPassword in the "x-admin-key" header).
/// </summary>
public interface IIndexNowBootstrapService
{
    DateTime? GetLastBootstrapUtc();
    Task<int> SubmitPathsAsync(IEnumerable<string> relativePaths);
}

public class IndexNowBootstrapService : IIndexNowBootstrapService, IHostedService
{
    private const int StartupDelaySeconds = 20;
    private const int MaxRetries = 5;
    private const int RetryDelaySeconds = 30;

    private readonly IIndexNowService _indexNowService;
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly IConfiguration _config;
    private readonly IWebHostEnvironment _env;
    private readonly ILogger<IndexNowBootstrapService> _logger;

    public IndexNowBootstrapService(
        IIndexNowService indexNowService,
        IHttpClientFactory httpClientFactory,
        IConfiguration config,
        IWebHostEnvironment env,
        ILogger<IndexNowBootstrapService> logger)
    {
        _indexNowService = indexNowService;
        _httpClientFactory = httpClientFactory;
        _config = config;
        _env = env;
        _logger = logger;
    }

    private string StampFilePath => Path.Combine(_env.ContentRootPath, "_data", "indexnow_bootstrap.stamp");

    public DateTime? GetLastBootstrapUtc()
    {
        var path = StampFilePath;
        if (!File.Exists(path)) return null;
        if (DateTime.TryParseExact(File.ReadAllText(path).Trim(), "O", null,
                System.Globalization.DateTimeStyles.RoundtripKind, out var dt))
        {
            return dt.ToUniversalTime();
        }
        return null;
    }

    /// <summary>
    /// Submits a batch of absolute or relative URLs/paths (e.g. "blog/my-post",
    /// "https://mysite.com/blog/my-post") to IndexNow in a single request
    /// (up to 10.000 URLs) and records a timestamp stamp.
    /// </summary>
    public async Task<int> SubmitPathsAsync(IEnumerable<string> relativePaths)
    {
        var host = _config["IndexNow:Host"];
        if (string.IsNullOrWhiteSpace(host))
        {
            _logger.LogWarning("IndexNow:Host is not configured. Bootstrap aborted.");
            return 0;
        }

        var urls = relativePaths
            .Where(p => !string.IsNullOrWhiteSpace(p))
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .ToList();

        if (urls.Count == 0) return 0;

        await _indexNowService.NotifyUrlsChangedAsync(urls);

        MarkBootstrap();

        _logger.LogInformation("IndexNow bootstrap submitted {Count} URLs for host {Host}.", urls.Count, host);
        return urls.Count;
    }

    private void MarkBootstrap()
    {
        Directory.CreateDirectory(Path.GetDirectoryName(StampFilePath)!);
        File.WriteAllText(StampFilePath, DateTime.UtcNow.ToString("O"));
    }

    // ---- IHostedService: automatic one-time bootstrap on startup ----

    public Task StartAsync(CancellationToken cancellationToken)
    {
        if (_env.IsDevelopment()) return Task.CompletedTask;

        _ = Task.Run(async () =>
        {
            await Task.Delay(TimeSpan.FromSeconds(StartupDelaySeconds));

            if (GetLastBootstrapUtc() != null) return;

            for (var attempt = 1; attempt <= MaxRetries; attempt++)
            {
                try
                {
                    var count = await BootstrapFromOwnSitemapAsync();
                    if (count > 0)
                    {
                        _logger.LogInformation("IndexNow auto-bootstrap completed: {Count} URLs submitted from sitemap.", count);
                        return;
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogWarning(ex, "IndexNow auto-bootstrap attempt {Attempt}/{MaxRetries} failed.", attempt, MaxRetries);
                }

                await Task.Delay(TimeSpan.FromSeconds(RetryDelaySeconds));
            }

            _logger.LogWarning("IndexNow auto-bootstrap gave up after {MaxRetries} attempts. Use POST /api/seo/indexnow/bootstrap with the x-admin-key header to submit manually.", MaxRetries);
        }, CancellationToken.None);

        return Task.CompletedTask;
    }

    public Task StopAsync(CancellationToken cancellationToken) => Task.CompletedTask;

    /// <summary>
    /// Reads the project's own dynamic or static /sitemap.xml and submits
    /// every &lt;loc&gt; URL found. Fully generic - no project-specific code.
    /// </summary>
    private async Task<int> BootstrapFromOwnSitemapAsync()
    {
        var host = _config["IndexNow:Host"];
        if (string.IsNullOrWhiteSpace(host)) return 0;

        var client = _httpClientFactory.CreateClient();
        var xml = await client.GetStringAsync($"https://{host}/sitemap.xml");

        var urls = Regex.Matches(xml, "<loc>(.*?)</loc>", RegexOptions.IgnoreCase)
            .Select(m => XmlUnescape(m.Groups[1].Value.Trim()))
            .Where(u => u.StartsWith("http", StringComparison.OrdinalIgnoreCase))
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .ToList();

        if (urls.Count == 0)
        {
            _logger.LogWarning("IndexNow auto-bootstrap: sitemap.xml returned no URLs.");
            return 0;
        }

        return await SubmitPathsAsync(urls);
    }

    private static string XmlUnescape(string value) => value
        .Replace("&amp;", "&").Replace("&lt;", "<").Replace("&gt;", ">")
        .Replace("&quot;", "\"").Replace("&apos;", "'");
}
