namespace CWSoftware.Web.Services;

/// <summary>
/// Service to notify search engines (Bing, Copilot, ChatGPT Search, Yandex, Seznam, Naver)
/// immediately when URLs are added, updated, or removed using the open IndexNow protocol.
/// </summary>
public interface IIndexNowService
{
    /// <summary>
    /// Notifies search engines that a single URL was updated or published.
    /// </summary>
    Task NotifyUrlChangedAsync(string url, CancellationToken cancellationToken = default);

    /// <summary>
    /// Notifies search engines of multiple modified URLs in a single batch request.
    /// </summary>
    Task NotifyUrlsChangedAsync(IEnumerable<string> urls, CancellationToken cancellationToken = default);
}
