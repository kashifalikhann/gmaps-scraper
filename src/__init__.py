"""Google Maps Scraper — HTTP-only actor for Apify marketplace.

Extracts business listings (name, phone, website, address, rating, category,
coordinates, hours) from Google Maps using HTTP-only requests with TLS
impersonation (curl_cffi). Optionally extracts emails from business websites,
verifies deliverability via DNS MX, tracks new/changed listings with
incremental mode, and exports to HubSpot/Salesforce/Pipedrive CSV format.
"""
