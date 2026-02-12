# X/Twitter Access Methods Reference

This document details various methods for accessing X/Twitter content while avoiding login requirements.

## 1. fxtwitter.com (Primary Method)

fxtwitter (formerly fixupx) is the most reliable method for bypassing Twitter's login wall.

### API Endpoints
- User timeline: `https://api.fxtwitter.com/{username}`
- Specific tweet: `https://api.fxtwitter.com/{username}/status/{tweet_id}`
- With media: Same endpoints work for media-rich content

### Response Format
The API returns JSON with:
- `code`: HTTP status code
- `tweet`: Tweet object with text, author, engagement metrics
- `user`: Author information
- `media_entities`: Media content if present

### Limitations
- Rate limited (exact limits not published)
- May break when Twitter changes APIs
- Third-party service (not official)

## 2. Nitter (Alternative Frontend)

Nitter is an open-source alternative Twitter frontend that allows anonymous browsing.

### Public Instances
- https://nitter.net
- https://nitter.privacydev.net
- https://nitter.namazso.eu
- https://nitter.unixfox.eu

### Direct URL Patterns
- User timeline: `https://{instance}/{username}`
- Specific tweet: `https://{instance}/{username}/status/{tweet_id}`
- RSS feed: `https://{instance}/{username}/rss`

### Advantages
- Open source (can self-host)
- No JavaScript
- Lightweight
- Multiple public instances

### Disadvantages
- Instance availability varies
- HTML parsing required
- Less structured data

## 3. Official Twitter API (Requires Authentication)

For production use, the official Twitter API is recommended:

### Requirements
- Twitter Developer Account
- API Keys and Tokens
- Compliance with Terms of Service

### Endpoints
- Tweet lookup: `GET /2/tweets/:id`
- User tweets: `GET /2/users/:id/tweets`

## 4. Browser Automation

Using Playwright or Selenium to scrape Twitter directly.

### Considerations
- Requires handling of JavaScript
- May face rate limiting or CAPTCHAs
- Needs headless browser
- Violates ToS if not careful

## 5. Alternative Services

### Zipline
- URL: `https://zipline.marcom.dev/fix`
- Alternative to fxtwitter
- Similar functionality

### Teitter
- URL: `https://teitter.vercel.app`
- Another Twitter content proxy
- Limited availability

## Best Practices

1. **Always implement fallbacks**: If primary method fails, try alternatives
2. **Respect rate limits**: Add delays between requests
3. **Handle errors gracefully**: Return informative messages when services fail
4. **Cache responses**: Store successful responses to reduce API calls
5. **Monitor service availability**: Third-party services may go down

## Recommended Approach

1. Start with fxtwitter for individual tweets
2. Fall back to nitter if fxtwitter fails
3. Use browser automation only as a last resort
4. For high-volume usage, consider official Twitter API with authentication