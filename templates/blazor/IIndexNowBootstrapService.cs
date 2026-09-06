using CWSoftware.Web.Services;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace CWSoftware.Web.Services;

/// <summary>
/// SEO-FORGE: One-time (repeatable on demand) bulk submission of every public
/// URL to IndexNow. Bootstraps the integration so Bing, Copilot and ChatGPT
/// Search become aware of all EXISTING content without waiting for organic
/// crawls. Wire it to an admin-only button (see templates/blazor/ProgramSnippets.cs).
/// </summary>
public interface IIndexNowBootstrapService
{
    DateTime? GetLastBootstrapUtc();
    Task<int> SubmitPathsAsync(IEnumerable<string> relativePaths);
}

public class IndexNowBootstrapService : IIndexNowBootstrapService
{
    private readonly IIndexNowService _indexNowService;
    private readonly IConfiguration _config;
    private readonly IWebHostEnvironment _env;
    private readonly ILogger<IndexNowBootstrapService> _logger;

    public IndexNowBootstrapService(
        IIndexNowService indexNowService,
        IConfiguration config,
        IWebHostEnvironment env,
        ILogger<IndexNowBootstrapService> logger)
    {
        _indexNowService = indexNowService;
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
    /// Submits a batch of relative paths (e.g. "blog/my-post", "pt/blog/my-post", "")
    /// to IndexNow in a single request (up to 10.000 URLs) and records a timestamp
    /// stamp so the UI can warn before an accidental re-submission.
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

        Directory.CreateDirectory(Path.GetDirectoryName(StampFilePath)!);
        await File.WriteAllTextAsync(StampFilePath, DateTime.UtcNow.ToString("O"));

        _logger.LogInformation("IndexNow bootstrap submitted {Count} URLs for host {Host}.", urls.Count, host);
        return urls.Count;
    }
}
