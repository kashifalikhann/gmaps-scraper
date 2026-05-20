from utils import (
    extract_emails_from_html,
    extract_jsonld_from_html,
    extract_email_from_jsonld,
    sanitize_email,
)


async def extract_emails_from_website(
    website_url: str,
    client,
) -> dict:
    emails = []
    source = 'none'
    jsonld_data = []

    html = await client.fetch_website(website_url)
    if not html:
        return {'emails': [], 'source': 'unreachable', 'jsonld': []}

    mailto_emails = _mailto_emails(html)
    if mailto_emails:
        emails = mailto_emails
        source = 'mailto'
    else:
        jsonld_data = extract_jsonld_from_html(html)
        jsonld_emails = extract_email_from_jsonld(jsonld_data)
        if jsonld_emails:
            emails = jsonld_emails
            source = 'jsonld'
        elif 'data-cfemail' in html:
            all_emails = extract_emails_from_html(html)
            if all_emails:
                emails = all_emails
                source = 'cloudflare'
        else:
            all_emails = extract_emails_from_html(html)
            if all_emails:
                emails = all_emails
                source = 'html'

    if not emails:
        return {'emails': [], 'source': 'not-found', 'jsonld': jsonld_data}

    cleaned = []
    seen = set()
    for e in emails:
        sanitized = sanitize_email(e)
        if sanitized and sanitized not in seen:
            cleaned.append(sanitized)
            seen.add(sanitized)

    return {'emails': cleaned, 'source': source, 'jsonld': jsonld_data}


def _mailto_emails(html: str) -> list[str]:
    import re
    found = []
    for ref in re.findall(r'href="mailto:([^"?#]+)', html, re.IGNORECASE):
        e = ref.split('?')[0].strip()
        if e:
            found.append(e.lower())
    return found
