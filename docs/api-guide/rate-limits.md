<!-- Mirrored from https://docs.spacetraders.io/api-guide/rate-limits -->

# Rate Limits

## Rate Limits

The SpaceTraders API is subject to rate limits. The following is a list that outlines the rate limits that are currently in place:

| Type | Status | Limit | Burst Limit | Burst Duration |
| --- | --- | --- | --- | --- |
| IP Address | 429 | 2 requests per second | 30 requests | 60 seconds |
| Account | 429 | 2 requests per second | 30 requests | 60 seconds |
| DDoS Protection | 502 | - | - | - |

## Response Headers

The SpaceTraders API will return the following headers in a 429 response to
indicate the current rate limit status.

| Header Name | Description |
| --- | --- |
| `x-ratelimit-type` | The type of rate limit that was exceeded. |
| `x-ratelimit-limit` | The maximum number of requests that can be made in a given time period. |
| `x-ratelimit-remaining` | The number of requests remaining in the current time period. |
| `x-ratelimit-reset` | The time at which the current time period will reset. |
| `x-ratelimit-limit-burst` | The maximum number of requests that can be made in a given burst duration. |
| `x-ratelimit-limit-per-second` | The maximum number of requests that can be made in a given time period. |

> **Warning: Other Status Codes**
>
> Unfortunately, our cloud infrastructure may also throw error codes, including a
> 429, and we cannot modify the headers or body of the response.
>
> Always check for headers to determine if the response is from our rate limiter. In all other instances, you may want to
> implement an exponential backoff strategy.

The DDoS protection is in place to protect the SpaceTraders API from being overwhelmed by a large number of requests. If you are receiving a `502 Bad Gateway` response, you should wait a few minutes before trying again.

We don't publish the exact details of our DDoS protection layer, but it is designed to allow a reasonable number of requests to be made in a short period of time.

## Example Response

The following is an example of a response when the rate limit has been exceeded:

```http
HTTP/1.1 429 Too Many Requests
Date: Tue, 21 Jan 2023 23:36:32 GMT
access-control-allow-origin: \*
access-control-expose-headers: Retry-After, X-RateLimit-Type, X-RateLimit-Limit-Burst, X-RateLimit-Limit-Per-Second, X-RateLimit-Remaining, X-RateLimit-Reset
content-type: application/json; charset=utf-8
retry-after: 1
x-powered-by: Express
x-ratelimit-limit-burst: 10
x-ratelimit-limit-per-second: 2
x-ratelimit-remaining: 0
x-ratelimit-reset: 2023-01-21T23:36:33.435Z
x-ratelimit-type: IP Address

{
  "error": {
    "message": "You have reached your API limit.",
    "code": 429,
    "data": {
      "type": "IP Address",
      "retryAfter": 1,
      "limitBurst": 10,
      "limitPerSecond": 2,
      "remaining": 0,
      "reset": "2023-01-21T23:36:33.435Z"
    }
  }
}
```
