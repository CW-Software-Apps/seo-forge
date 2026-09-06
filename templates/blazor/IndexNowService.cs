using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace CWSoftware.Web.Services;

/// <summary>
/// Default implementation of IndexNow protocol client for ASP.NET Core and Blazor.
/// </summary>
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
        if (string.IsNullOrWhiteSpace(key))
        {
            _logger.LogWarning("IndexNow:Key is not configured in appsettings.json. Skipping notification.");
            return;
        }

        var host = _config["IndexNow:Host"] ?? "cwsoftware.com.br";
        var keyLocation = $"https://{host}/{key}.txt";

        var urlList = urls
            .Where(u => !string.IsNullOrWhiteSpace(u))
            .Select(u => u.StartsWith("http", StringComparison.OrdinalIgnoreCase) ? u : $"https://{host}/{u.TrimStart('/')}")
            .Distinct()
            .ToList();

        if (urlList.Count == 0)
        {
            return;
        }

        var payload = new
        {
            host = host,
            key = key,
            keyLocation = keyLocation,
            urlList = urlList
        };

        try
        {
            var response = await _httpClient.PostAsJsonAsync("https://api.indexnow.org/indexnow", payload, cancellationToken);
            if (response.IsSuccessStatusCode)
            {
                _logger.LogInformation("IndexNow successfully submitted {Count} URLs for host {Host}.", urlList.Count, host);
            }
            else
            {
                var content = await response.Content.ReadAsStringAsync(cancellationToken);
                _logger.LogWarning("IndexNow API returned status {StatusCode}: {Content}", (int)response.StatusCode, content);
                throw new IndexNowSubmissionException((int)response.StatusCode, content);
            }
        }
        catch (IndexNowSubmissionException)
        {
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to submit URLs to IndexNow API.");
            throw;
        }
    }
}
