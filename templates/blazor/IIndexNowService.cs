using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace CWSoftware.Web.Services;

/// <summary>
/// Service to notify search engines (Bing, Copilot, ChatGPT Search, Yandex, Seznam, Naver)
/// immediately when URLs are added, updated, or removed using the open IndexNow protocol.
/// </summary>
public interface IIndexNowService
{
    /// <summary>
    /// Notifies search engines that a URL was added, updated or removed.
    /// Throws IndexNowSubmissionException if the IndexNow API rejects the submission.
    /// </summary>
    Task NotifyUrlChangedAsync(string url, CancellationToken cancellationToken = default);

    /// <summary>
    /// Notifies search engines that multiple URLs changed (batch, up to 10.000).
    /// Throws IndexNowSubmissionException if the IndexNow API rejects the submission.
    /// </summary>
    Task NotifyUrlsChangedAsync(IEnumerable<string> urls, CancellationToken cancellationToken = default);
}

/// <summary>
/// Raised when the IndexNow API rejects a submission. Carries the HTTP status
/// code and the API error body so callers (UI, logs, retries) can surface it.
/// </summary>
public class IndexNowSubmissionException : Exception
{
    public int StatusCode { get; }
    public string ResponseBody { get; }

    public IndexNowSubmissionException(int statusCode, string responseBody)
        : base($"IndexNow submission failed (HTTP {statusCode}): {responseBody}")
    {
        StatusCode = statusCode;
        ResponseBody = responseBody;
    }
}
