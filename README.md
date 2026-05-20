# Google Maps Scraper — Verified Emails, Incremental Mode, CRM Export

**The only Google Maps scraper with email verification, delta/incremental tracking, and one-click CRM export built in.** No API keys, no integrations, no separate enrichment tools.

## Why this scraper?

| Feature | What it means for you |
|---------|----------------------|
| **Email verification built-in** | DNS MX lookup confirms every email can receive mail. Flag or auto-filter disposable/invalid addresses. No bounced emails. |
| **Incremental / delta mode** | Run weekly. Only get new listings. Tracks previously seen places via KV store. No re-scraping the same data. |
| **One-click CRM export** | Pre-formatted rows for HubSpot, Salesforce, or Pipedrive. Download as CSV and import directly. |
| **Email extraction included** | 5 methods (mailto, HTML entities, CloudFlare decoding, JSON-LD, obfuscated patterns). No add-on fees. |
| **No duplicate rows** | Same business across overlapping queries? Deduped automatically. |
| **Clean URLs** | All `utm_*` and tracking parameters stripped from website URLs. |
| **Validated contacts** | TLD whitelist + email format validation + disposable domain rejection. |

## New in v2.0

- **Email verification** — DNS MX lookup checks if each email's domain can receive mail. Mode: flag (mark deliverability) or filter (remove bad emails).
- **Incremental / delta mode** — "New Only" returns only places you haven't seen before. "Flag" marks new vs known on every row. State stored in Apify KV between runs.
- **CRM export** — Select HubSpot, Salesforce, or Pipedrive format. Each row includes `_crmHeaders` and `_crmRow` for one-click CSV import.

## What you can extract

| Field | Description |
|-------|-------------|
| `name` | Business name |
| `address` | Full street address |
| `phone` | Phone number |
| `website` | Business website (UTMs stripped) |
| `emails` | Email addresses from business website |
| `websiteDomain` | Domain extracted from website URL |
| `emailSource` | How the email was found (mailto, jsonld, html, cloudflare) |
| `emailVerification` | Deliverability check result |
| `rating` | Star rating (1.0–5.0) |
| `reviewCount` | Number of reviews |
| `category` | Business category (Plumber, Restaurant, etc.) |
| `coordinates` | Latitude, longitude |
| `hours` | Opening hours by day |
| `placeUrl` | Google Maps place page link |
| `scrapedAt` | ISO timestamp of scrape |
| `_isNew` | Whether listing is new (incremental mode) |
| `_crmRow` | Pre-formatted CRM import row |

## Use cases

- **Local lead generation** — build lists of verified-contacted local businesses
- **Weekly competitor monitoring** — incremental mode catches new businesses in your market
- **CRM pipeline seeding** — export directly to HubSpot/Salesforce/Pipedrive format
- **Market research** — analyze business density and categories by location
- **Real estate / site selection** — understand competitive landscape before opening

## How pricing works

This actor uses **pay-per-event** pricing on the Apify platform:

- **Free tier**: $5/month free compute credits included with every Apify account
- **Emails disabled**: ~1–2 compute units per 100 listings
- **Emails enabled**: ~3–5 compute units per 100 listings
- **Email verification**: adds ~0.1 CU per 100 listings (DNS lookups are fast)
- **Incremental mode**: negligible cost (KV store reads/writes)
- **Typical free-tier capacity**: 500–2,000 listings per month at no cost

No hidden fees. Email verification and incremental mode are included at no extra charge.

## Quick start

1. **Enter queries** — `plumbers in Austin, TX`, `coffee shops San Francisco`
2. **Toggle features** — enable email verification, incremental mode, or CRM format
3. **Set limits** — max results up to 500, concurrency 1–20
4. **Run** — results appear as JSON, CSV, HTML, or Excel

## Input fields

| Field | Default | Description |
|-------|---------|-------------|
| `searchQueries` | — | Search terms on Google Maps (array, required) |
| `maxResults` | 50 | Total listings across ALL queries (1–500) |
| `extractEmails` | true | Visit websites to extract emails |
| `verifyEmails` | off | `off` / `flag` (mark status) / `filter` (remove bad) |
| `incrementalMode` | off | `off` / `flag` (mark new) / `new-only` (only new) |
| `crmFormat` | none | `none` / `hubspot` / `salesforce` / `pipedrive` |
| `extractPhone` | true | Extract phone numbers |
| `extractWebsite` | true | Extract website URLs |
| `extractRating` | true | Extract star rating + review count |
| `extractCoordinates` | true | Extract lat/lng coordinates |
| `extractCategory` | true | Extract business category |
| `extractHours` | false | Extract opening hours |
| `maxConcurrency` | 3 | Parallel pages (1–20) |
| `proxyCountry` | auto | ISO country code for geo-targeting |
| `domain` | google.com | Custom Google domain |

## Sample output

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
  "emailVerification": "filtered",
  "_isNew": true,
  "_crmRow": "\"Austin Plumbing Co\",\"+1 512-555-0123\",\"https://www.austinplumbing.com\",\"contact@austinplumbing.com\",\"123 Main St, Austin, TX 78701\",\"Plumber\",4.5,127",
  "placeUrl": "https://www.google.com/maps/place/...",
  "scrapedAt": "2026-05-20T12:00:00.000Z"
}
```

## Tips

- **Incremental mode is per-actor** — state is stored in your Apify KV store. Different API tokens have separate state.
- **Email filter mode removes bad emails** — use `verifyEmails: filter` when pushing to your CRM to avoid bounces.
- **CRM export** — download results as CSV. Every row has `_crmHeaders` (copy once as header) and `_crmRow`. Paste into your CRM's import tool.
- **Email extraction costs compute** — each website is fetched via HTTP. Disable for faster runs if you only need listings.
- **Overlapping queries are safe** — dedup handles them automatically.

## FAQ

### Is scraping Google Maps legal?

Web scraping publicly available data is a well-established practice. Review Google's ToS and consult your legal team.

### How is email verification different from email extraction?

- **Extraction** finds emails on business websites (always included).
- **Verification** checks if those email domains can receive mail via DNS MX lookup (optional, toggle on/off).

### Does incremental mode work across different Apify users?

No. State is stored per API token in your private Apify KV store.

### Can I scrape more than 500 results per query?

Input limit is 500. For larger datasets, run multiple queries with different keywords or location splits.

### How is this different from compass/crawler-google-places?

| Feature | compass | This scraper |
|---------|---------|-------------|
| Email verification | $2/1K add-on | Included (DNS MX) |
| Delta / incremental | Not available | Included (KV store) |
| CRM-ready export | Not available | HubSpot/SF/Pipedrive |
| Email extraction | $2/1K add-on | Included |
| Deduplication | Not available | Included |
| UTM stripping | Not available | Included |
| TLD validation | Not available | Included |

## Support

Report issues or request features on the [Issues tab](https://github.com/your-repo/gmaps-scraper/issues). Access results programmatically via Apify's API tab.

> **Disclaimer:** This Actor extracts only publicly available information from Google Maps and linked business websites. Results may contain personal data protected by GDPR and other regulations. Ensure you have a legitimate basis for scraping before use.
