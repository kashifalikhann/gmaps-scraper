import re

TRACKING_PARAMS = [
    'fbclid', 'gclid', 'gclsrc', 'dclid', 'gbraid', 'wbraid',
    'msclkid', 'twclid', 'igshid', 'yclid',
    'ref', 'source', 'mc_cid', 'mc_eid',
]

DISPOSABLE_DOMAINS = {
    'mailinator.com', 'guerrillamail.com', '10minutemail.com', 'tempmail.com',
    'throwaway.email', 'yopmail.com', 'sharklasers.com', 'trashmail.com',
    'temp-mail.org', 'fakeinbox.com', 'maildrop.cc', 'getnada.com',
    'burnermail.io', 'mohmal.com', 'minuteinbox.com', 'emailondeck.com',
    'spamgourmet.com', 'sneakemail.com', 'mailcatch.com', 'spambox.us',
    'dispostable.com', 'mailnator.com', 'tempinbox.com', 'mailexpire.com',
    'spambox.org', 'mail-temp.com', 'temp-mail.net', 'luxe-mail.com',
    'mailmetrash.com', 'trash2009.com', 'maileater.com', 'mintemail.com',
}

COUNTRY_CODES = {
    'ac', 'ad', 'ae', 'af', 'ag', 'ai', 'al', 'am', 'ao', 'aq', 'ar', 'as',
    'at', 'au', 'aw', 'ax', 'az', 'ba', 'bb', 'bd', 'be', 'bf', 'bg', 'bh',
    'bi', 'bj', 'bm', 'bn', 'bo', 'br', 'bs', 'bt', 'bw', 'by', 'bz',
    'ca', 'cc', 'cd', 'cf', 'cg', 'ch', 'ci', 'ck', 'cl', 'cm', 'cn', 'co',
    'cr', 'cu', 'cv', 'cw', 'cx', 'cy', 'cz', 'de', 'dj', 'dk', 'dm', 'do',
    'dz', 'ec', 'ee', 'eg', 'er', 'es', 'et', 'eu', 'fi', 'fj', 'fk', 'fm',
    'fo', 'fr', 'ga', 'gd', 'ge', 'gf', 'gg', 'gh', 'gi', 'gl', 'gm', 'gn',
    'gp', 'gq', 'gr', 'gs', 'gt', 'gu', 'gw', 'gy', 'hk', 'hm', 'hn', 'hr',
    'ht', 'hu', 'id', 'ie', 'il', 'im', 'in', 'io', 'iq', 'ir', 'is', 'it',
    'je', 'jm', 'jo', 'jp', 'ke', 'kg', 'kh', 'ki', 'km', 'kn', 'kp', 'kr',
    'kw', 'ky', 'kz', 'la', 'lb', 'lc', 'li', 'lk', 'lr', 'ls', 'lt', 'lu',
    'lv', 'ly', 'ma', 'mc', 'md', 'me', 'mg', 'mh', 'mk', 'ml', 'mm', 'mn',
    'mo', 'mp', 'mq', 'mr', 'ms', 'mt', 'mu', 'mv', 'mw', 'mx', 'my', 'mz',
    'na', 'nc', 'ne', 'nf', 'ng', 'ni', 'nl', 'no', 'np', 'nr', 'nu', 'nz',
    'om', 'pa', 'pe', 'pf', 'pg', 'ph', 'pk', 'pl', 'pm', 'pn', 'pr', 'ps',
    'pt', 'pw', 'py', 'qa', 're', 'ro', 'rs', 'ru', 'rw', 'sa', 'sb', 'sc',
    'sd', 'se', 'sg', 'sh', 'si', 'sk', 'sl', 'sm', 'sn', 'so', 'sr', 'ss',
    'st', 'su', 'sv', 'sx', 'sy', 'sz', 'tc', 'td', 'tf', 'tg', 'th', 'tj',
    'tk', 'tl', 'tm', 'tn', 'to', 'tr', 'tt', 'tv', 'tw', 'tz', 'ua', 'ug',
    'uk', 'us', 'uy', 'uz', 'va', 'vc', 've', 'vg', 'vi', 'vn', 'vu',
    'wf', 'ws', 'ye', 'yt', 'za', 'zm', 'zw',
}

COMMON_GTLDS = {
    'com', 'org', 'net', 'gov', 'edu', 'mil', 'info', 'biz', 'name', 'pro',
    'aero', 'coop', 'museum', 'mobi', 'travel', 'jobs', 'cat', 'tel', 'asia', 'int',
    'app', 'dev', 'cloud', 'shop', 'store', 'online', 'site', 'tech', 'blog',
    'media', 'news', 'email', 'design', 'world', 'life', 'club', 'agency',
    'digital', 'global', 'group', 'guru', 'network', 'studio', 'solutions',
    'services', 'systems', 'today', 'tools', 'video', 'marketing',
    'finance', 'insurance', 'photos', 'photography', 'technology',
    'education', 'health', 'healthcare', 'support', 'directory', 'business',
    'engineering', 'management', 'training', 'events', 'foundation',
    'productions', 'properties', 'international', 'enterprises', 'consulting',
    'solar', 'builders', 'camp', 'careers', 'catering', 'cleaning',
    'clothing', 'community', 'company', 'computer', 'construction',
    'contractors', 'cool', 'coupons', 'credit', 'dating', 'delivery',
    'direct', 'discount', 'dog', 'domains', 'energy', 'expert',
    'express', 'family', 'farm', 'fashion', 'financial',
    'fish', 'fitness', 'flights', 'florist', 'football', 'fund',
    'furniture', 'gallery', 'games', 'garden', 'gift', 'gold',
    'golf', 'graphics', 'green', 'guide', 'homes',
    'host', 'hosting', 'house', 'immo', 'industries',
    'institute', 'investments', 'kitchen', 'land', 'lease', 'legal',
    'lgbt', 'lighting', 'limited', 'link', 'live', 'loan', 'love',
    'ltd', 'maison', 'market', 'markets', 'media', 'men', 'menu',
    'money', 'movie', 'music', 'navy', 'network', 'ninja',
    'one', 'organic', 'parts', 'partners', 'party', 'pet',
    'phone', 'photo', 'pictures', 'pink', 'pizza', 'place',
    'plumbing', 'plus', 'press', 'promo', 'properties', 'pub',
    'racing', 'realty', 'recipes', 'red', 'rent', 'rentals',
    'repair', 'report', 'restaurant', 'review', 'reviews',
    'rock', 'run', 'sale', 'salon', 'school', 'science',
    'services', 'shoes', 'show', 'singles', 'site',
    'soccer', 'social', 'software', 'solar', 'solutions',
    'space', 'studio', 'supplies', 'supply', 'support', 'surf',
    'systems', 'tax', 'taxi', 'team', 'tech', 'technology',
    'tips', 'today', 'tools', 'top', 'tour', 'town',
    'toys', 'trade', 'training', 'travel', 'university',
    'vegas', 'ventures', 'vet', 'viajes', 'video', 'villas',
    'vision', 'voyage', 'watch', 'website', 'wedding', 'wiki',
    'wine', 'work', 'works', 'world', 'wtf', 'xyz', 'zone',
    'hotel', 'exchange', 'codes', 'coffee', 'cafe',
    'london', 'nyc', 'tokyo', 'paris', 'berlin',
    'band', 'bar', 'bio', 'black', 'blue', 'boutique',
    'cab', 'camera', 'capital', 'cards', 'care',
    'cash', 'center', 'ceo', 'charity', 'chat', 'cheap',
    'church', 'city', 'claims', 'clinic', 'coach',
    'codes', 'coffee', 'college', 'cooking', 'cool',
    'country', 'creditcard', 'cruises', 'dance', 'date',
    'deals', 'degree', 'dental', 'dentist', 'diamonds',
    'diet', 'digital', 'direct', 'directory', 'doctor',
    'dog', 'domains', 'download', 'earth', 'education',
}


def is_valid_tld(tld: str) -> bool:
    t = tld.lower()
    return t in COUNTRY_CODES or t in COMMON_GTLDS


def sanitize_email(email: str) -> str | None:
    cleaned = re.sub(r'[<>&"\'\\()\[\]]', '', email).strip()
    parts = cleaned.split('@')
    if len(parts) != 2:
        return None
    local = re.sub(r'[^a-zA-Z0-9._%+\-]', '', parts[0])
    domain = re.sub(r'[^a-zA-Z0-9.\-]', '', parts[1])
    if not local or not domain or '.' not in domain:
        return None
    if len(local) < 3:
        return None
    if local.startswith('.') or local.endswith('.'):
        return None
    segments = domain.split('.')
    tld = segments.pop()
    if not is_valid_tld(tld):
        return None
    for seg in segments:
        if len(seg) < 2:
            return None
        if '-' in seg:
            return None
    placeholders = [
        'user@domain.com', 'name@domain.com', 'email@domain.com',
        'test@test.com', 'admin@domain.com',
    ]
    if f'{local}@{domain}'.lower() in placeholders:
        return None
    return f'{local}@{domain}'.lower()


def clean_website_url(url: str) -> str:
    try:
        from urllib.parse import urlparse, urlencode, urlunparse, parse_qs
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        for key in list(params.keys()):
            if key in TRACKING_PARAMS or key.startswith('utm_'):
                del params[key]
        query = urlencode(params, doseq=True) if params else ''
        return urlunparse(parsed._replace(query=query))
    except Exception:
        return url


def get_place_stable_id(place_url: str) -> str:
    import hashlib
    clean = place_url.split('?')[0].split('@')[0]
    return hashlib.md5(clean.encode()).hexdigest()


def extract_emails_from_html(html: str) -> list[str]:
    found = set()
    email_re = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    obfus_re = re.compile(
        r'([a-zA-Z0-9._%+-]+)\s*\[?\s*(?:at|@)\s*\]?\s*'
        r'([a-zA-Z0-9.-]+)\s*\[?\s*(?:dot|\.)\s*\]?\s*([a-zA-Z]{2,})',
        re.IGNORECASE,
    )

    for ref in re.findall(r'href="mailto:([^"?#]+)', html, re.IGNORECASE):
        e = ref.split('?')[0].strip()
        if e:
            found.add(e.lower())

    text = re.sub(r'<[^>]+>', ' ', html)
    text = text.replace('&nbsp;', ' ')
    for m in email_re.finditer(text):
        found.add(m.group(0).lower())

    decoded = html.replace('&#64;', '@').replace('&#46;', '.')
    decoded = decoded.replace('&#x40;', '@').replace('&#x2E;', '.')
    for m in email_re.finditer(decoded):
        found.add(m.group(0).lower())

    cf_pattern = re.compile(r'data-cfemail="([^"]+)"', re.IGNORECASE)
    for match in cf_pattern.finditer(html):
        hex_str = match.group(1)
        try:
            key = int(hex_str[:2], 16)
            out = ''
            for i in range(2, len(hex_str), 2):
                out += chr(int(hex_str[i:i + 2], 16) ^ key)
            if out:
                found.add(out.lower())
        except Exception:
            pass

    for m in obfus_re.finditer(text):
        found.add(
            f'{m.group(1).lower()}@{m.group(2).lower()}.{m.group(3).lower()}'
        )

    return sorted(found)


def extract_jsonld_from_html(html: str) -> list[dict]:
    results = []
    pattern = re.compile(
        r'<script[^>]*type="application/ld\+json"[^>]*>([\s\S]*?)</script>',
        re.IGNORECASE,
    )
    for match in pattern.finditer(html):
        try:
            import json
            parsed = json.loads(match.group(1))
            results.append(parsed)
            if '@graph' in parsed:
                results.extend(parsed['@graph'])
        except Exception:
            pass
    return results


def extract_email_from_jsonld(jsonld: list[dict]) -> list[str]:
    emails = set()
    email_re = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    for item in jsonld:
        if not item:
            continue
        items = [item]
        if isinstance(item.get('@graph'), list):
            items.extend(item['@graph'])
        for entry in items:
            email = entry.get('email', '') or ''
            phone = entry.get('telephone', '') or ''
            if email:
                for m in email_re.finditer(email):
                    emails.add(m.group(0).lower())
            elif phone:
                for m in email_re.finditer(phone):
                    emails.add(m.group(0).lower())
            contact_points = entry.get('contactPoint') or []
            if isinstance(contact_points, dict):
                contact_points = [contact_points]
            for cp in contact_points:
                if cp and cp.get('email'):
                    for m in email_re.finditer(cp['email']):
                        emails.add(m.group(0).lower())
    return sorted(emails)
