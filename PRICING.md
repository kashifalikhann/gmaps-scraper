# Pricing Strategy — Google Maps Scraper v2.0

## Model: Pay-Per-Event (PPE)

Apify's PPE model charges users per actor run based on compute units consumed.
We set a price per compute unit — Apify adds their markup.

## Final Recommendation: $4.00 per 1K results

**Strategy: Compete on workflow value, not price.**

At $4/1K with ALL features included (emails, DNS verification, incremental mode, CRM export), we sit at compass's *base* price but include everything compass charges extra for.

## Why $4/1K and not lower

| Rationale | Detail |
|-----------|--------|
| **compass comparison** | compass charges $4/1K base + $2/1K emails = $6/1K. At $4/1K we're 33% cheaper with more features. |
| **vortex_data at $1/1K** | vortex_data offers emails included at $1/1K, but they have 0 differentiation beyond that. We don't compete on price — we win on delta mode + email verification + CRM export. |
| **Perceived value** | Free or too-cheap signals low quality on Apify. $4/1K signals "professional tool." |
| **Margin safety** | Our email extraction is HTTP-based (not Playwright per site), so each run consumes fewer CUs. At $4/1K our effective margin is higher than compass's $6/1K. |

## Competitive Matrix

| Competitor | Price/1K | Emails? | Verified? | Delta? | CRM? | Monthly Users |
|-----------|----------|---------|-----------|-------|------|:------------:|
| **Us (v2.0)** | **$4.00** | ✅ Included | ✅ DNS MX | ✅ KV store | ✅ HubSpot/SF/Pipedrive | **0 → ?** |
| compass | $4-6/1K | ❌ $2 add-on | ❌ | ❌ | ❌ | 27K |
| vortex_data | $1.00 | ✅ Included | ❌ | ❌ | ❌ | 18 |
| get-leads | $3.00 | ✅ Included | ✅ | ❌ | ✅ HubSpot/SF | 7 |
| crustapi | $3.90 | ❌ | ❌ | ❌ | ❌ | — |
| scraperlink | $0.50 | ❌ | ❌ | ❌ | ❌ | 23 |
| jungle_thunder | $5.00 | ✅ | ❌ | ❌ | ❌ | — |

## Feature Comparison

| Feature | Us | compass | vortex_data | get-leads |
|---------|:--:|:-------:|:-----------:|:---------:|
| Email extraction | ✅ Free | ❌ $2/1K | ✅ Free | ✅ Free |
| Email verification (DNS MX) | ✅ Free | ❌ | ❌ | ✅ |
| Email filter mode | ✅ Free | ❌ | ❌ | ❌ |
| Incremental / delta | ✅ Free | ❌ | ❌ | ❌ |
| CRM export (HS/SF/PD) | ✅ Free | ❌ | ❌ | ✅ |
| Deduplication | ✅ | ❌ | ❌ | ❌ |
| UTM stripping | ✅ | ❌ | ❌ | ❌ |
| TLD validation | ✅ | ❌ | ❌ | ❌ |
| Disposable domain filter | ✅ | ❌ | ❌ | ❌ |

## How to set up on Apify

1. Actor detail → Monetization tab
2. Select "Pay Per Event"
3. Set base price per compute unit to achieve ~$4/1K at typical CU consumption
4. Fill in Display Information (icon, screenshots, categories)
5. Click "Publish to Store"

## After launch

- Monitor installs vs competitors via Apify Store category rankings
- Push the comparison table as the main messaging: "Everything compass charges extra for, included."
- Collect feedback on incremental mode and email verification quality
- Consider v2.5 features: review text extraction, images, social profiles (only if users ask)
