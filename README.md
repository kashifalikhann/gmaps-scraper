# Google Maps Scraper

Scrape Google Maps business listings — names, addresses, phone numbers, ratings, categories, opening hours, coordinates, and **email addresses extracted from business websites**. A complete Google Maps API alternative for lead generation and local business data.

## Why use Google Maps Scraper?

- **Extract hidden emails** — visits each business website and extracts contact emails using 5 methods (mailto links, HTML entities, CloudFlare decoding, JSON-LD, obfuscated patterns)
- **All data points** — rating, review count, coordinates, category, hours, phone, website, address
- **Multi-query** — run multiple searches in a single execution (e.g. "plumbers Austin", "electricians Austin")
- **Deduplicated** — same business across overlapping queries is only scraped once
- **Apify platform** — scheduling, proxy rotation, dataset export (JSON, CSV, Excel), webhooks

## What data can Google Maps Scraper extract?

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Business name |
| `address` | string | Street address |
| `phone` | string | Phone number |
| `website` | string | Business website URL |
| `emails` | array | Email addresses from the business website |
| `rating` | number | Star rating (1.0–5.0) |
| `reviewCount` | number | Number of Google Maps reviews |
| `category` | string | Business category |
| `coordinates` | string | Latitude and longitude (`"lat, lng"`) |
| `hours` | array | Opening hours by day |
| `placeUrl` | string | Google Maps place page URL |

## How to scrape Google Maps

1. **Enter your queries** — add search terms like "plumbers in Austin, TX" in the input tab
2. **Configure options** — toggle which fields to extract, enable email extraction, set concurrency
3. **Run the Actor** — click Start; the Actor searches Google Maps, scrolls results, and opens each listing
4. **Get your data** — download the dataset as JSON, CSV, HTML, or Excel

## How much will it cost to scrape Google Maps?

Pricing depends on the number of listings and whether email extraction is enabled:

- **Listings only**: ~1–2 compute units per 100 listings
- **With email extraction**: ~3–5 compute units per 100 listings (each business website is visited)
- **Free tier**: Apify's free tier includes $5/month in compute credits — enough for several hundred listings

## Input

See the **Input** tab for full configuration. Key fields:

- `searchQueries` — list of Google Maps search terms (each runs independently)
- `maxResults` — max listings per query (up to 500)
- `maxTotalResults` — hard global limit across all queries (0 = unlimited)
- `domain` — custom Google domain, e.g. `google.co.uk` for UK results
- `extractEmails` — enables business website visitation for email extraction
- `extractPhone` / `extractRating` / `extractCoordinates` / `extractCategory` / `extractHours` — toggle individual data points
- `maxConcurrency` — parallel page count (higher is faster but more likely to trigger rate limits)
- `proxyCountry` — ISO country code for geo-targeted results

## Local Testing

```bash
# Install dependencies
npm install

# Run locally (requires Apify account for proxy)
apify run

# Or run with specific input
echo '{"searchQueries":["plumbers in Austin, TX"],"maxResults":5}' | apify run -i -
```

Results land in `./storage/datasets/default/`. Requires Node 18+ and the `apify` CLI (`npm install -g apify-cli`).

## Output

Results are stored in the default dataset. Download in JSON, HTML, CSV, or Excel.

Example output item:

```json
{
  "query": "plumbers in Austin, TX",
  "name": "Austin Plumbing Co",
  "address": "123 Main St, Austin, TX 78701",
  "phone": "+1 512-555-0123",
  "website": "https://www.austinplumbing.com",
  "websiteDomain": "austinplumbing.com",
  "category": "Plumber",
  "rating": 4.5,
  "reviewCount": 127,
  "coordinates": "30.2672, -97.7431",
  "hours": ["Monday: 8:00 AM – 5:00 PM", "Tuesday: 8:00 AM – 5:00 PM"],
  "emails": ["contact@austinplumbing.com"],
  "emailSource": "jsonld+html",
  "placeUrl": "https://www.google.com/maps/place/...",
  "scrapedAt": "2026-05-20T12:00:00.000Z"
}
```

## Tips

- **Email extraction increases runtime** — each listing with a website requires an additional page visit. Set `extractEmails: false` for faster runs if you only need listing data
- **Use proxy for large runs** — set `proxyCountry` to your target market for localized results and use Apify proxy to avoid rate limits
- **Start with 1–2 queries** before scaling to many queries to verify your data quality
- **Overlapping queries** are automatically deduplicated — "plumbers Austin" and "plumbing Austin" will not produce duplicate entries

## FAQ

### Is scraping Google Maps legal?

Web scraping is a well-established practice. You should review Google's Terms of Service and consult your legal team if you have concerns about your specific use case.

### Why is email extraction slow?

Each business website must be loaded and scanned separately. Websites vary in speed and some may time out. The Actor handles these gracefully and scrapes what it can.

### Does this work for any location?

Yes. Specify any city, region, or country in your search queries. Results depend on Google Maps coverage for that area.

### Can I scrape more than 500 results per query?

The input limit is 500 per query. For larger datasets, run multiple queries with different keywords or location splits.

## Support

- Report issues or request features on the [Issues tab](https://github.com/your-repo/gmaps-scraper/issues)
- Access results programmatically via the [API tab](https://console.apify.com)
- Use webhooks to send data to your own systems after each run

> **Disclaimer:** This Actor extracts only publicly available information from Google Maps and linked business websites. Results may contain personal data, which is protected by GDPR and other regulations. Ensure you have a legitimate reason to scrape before using this tool. If unsure, consult your lawyers.
