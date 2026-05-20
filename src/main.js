import { Actor } from 'apify';
import {
  PlaywrightCrawler,
  createPlaywrightRouter,
  Dataset,
  log,
  ProxyConfiguration,
} from 'crawlee';

const TLD_BLOCKLIST = new Set(['if', 'we', 'in', 'at', 'to', 'by', 'or', 'on', 'as', 'us',
  'be', 'it', 'is', 'an', 'no', 'so', 'go', 'my', 'up', 'me', 'browse', 'zen']);
const COMMON_TLDS = new Set(['com', 'org', 'net', 'gov', 'edu', 'mil', 'ac', 'co', 'io', 'ai',
  'uk', 'de', 'fr', 'es', 'it', 'ca', 'au', 'jp', 'cn', 'br', 'in', 'ru', 'eu']);

function sanitizeEmail(email) {
  const cleaned = email.replace(/[<>&"'\\()\[\]]/g, '').trim();
  const parts = cleaned.split('@');
  if (parts.length !== 2) return null;
  const local = parts[0].replace(/[^a-zA-Z0-9._%+\-]/g, '');
  const domain = parts[1].replace(/[^a-zA-Z0-9.\-]/g, '');
  if (!local || !domain || !domain.includes('.')) return null;
  if (local.length < 3) return null;
  const segments = domain.split('.');
  const tld = segments.pop();
  if (TLD_BLOCKLIST.has(tld)) return null;
  for (const seg of segments) {
    if (seg.length < 3) return null;
    if (COMMON_TLDS.has(seg)) return null;
  }
  return `${local}@${domain}`.toLowerCase();
}

const EMAIL_RE = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
const OBFUSCATED_RE = /([a-zA-Z0-9._%+-]+)\s*\[?\s*(?:at|@)\s*\]?\s*([a-zA-Z0-9.-]+)\s*\[?\s*(?:dot|\.)\s*\]?\s*([a-zA-Z]{2,})/gi;
const BLOCKED_DOMAINS = ['example.com', 'domain.com', 'yourdomain.com', 'yoursite.com',
  'sample.com', 'test.com', 'mysite.com', 'mywebsite.com', 'placeholder.com',
  '.png', '.jpg', '.svg', '.webp', '.gif', '.jpeg', '.ico'];

function decodeCfEmail(hex) {
  try {
    const key = parseInt(hex.slice(0, 2), 16);
    let out = '';
    for (let i = 2; i < hex.length; i += 2) {
      out += String.fromCharCode(parseInt(hex.slice(i, i + 2), 16) ^ key);
    }
    return out;
  } catch {
    return null;
  }
}

async function extractEmails(page) {
  const set = new Set();

  const mails = await page.$$eval('a[href^="mailto:"]', els =>
    els.map(el => (el.getAttribute('href') || '').replace('mailto:', '').split('?')[0].trim())
  );
  mails.filter(Boolean).forEach(e => set.add(e.toLowerCase()));

  const text = await page.evaluate(() => document.body?.innerText || '');
  (text.match(EMAIL_RE) || []).forEach(e => set.add(e.toLowerCase()));

  const html = await page.content();
  const decoded = html
    .replace(/&#64;/g, '@').replace(/&#46;/g, '.')
    .replace(/&#x40;/g, '@').replace(/&#x2E;/g, '.')
    .replace(/&amp;#64;/g, '@').replace(/&amp;#46;/g, '.');
  (decoded.match(EMAIL_RE) || []).forEach(e => set.add(e.toLowerCase()));

  const cfItems = await page.$$eval('.cf_email', els =>
    els.map(el => el.getAttribute('data-cfemail')).filter(Boolean)
  );
  for (const hex of cfItems) {
    const d = decodeCfEmail(hex);
    if (d) set.add(d.toLowerCase());
  }

  let m;
  while ((m = OBFUSCATED_RE.exec(text)) !== null) {
    set.add(`${m[1].toLowerCase()}@${m[2].toLowerCase()}.${m[3].toLowerCase()}`);
  }

  return [...set].filter(e => {
    try { return !BLOCKED_DOMAINS.some(b => e.split('@')[1]?.endsWith(b)); }
    catch { return true; }
  });
}

async function extractJsonLd(page) {
  return page.evaluate(() => {
    const scripts = document.querySelectorAll('script[type="application/ld+json"]');
    const results = [];
    for (const s of scripts) {
      try {
        const parsed = JSON.parse(s.textContent || '');
        results.push(parsed);
        if (parsed['@graph']) results.push(...parsed['@graph']);
      } catch {}
    }
    return results;
  });
}

function extractEmailFromJsonLd(jsonld) {
  const emails = new Set();
  for (const item of jsonld) {
    if (!item) continue;
    const flat = [item];
    if (Array.isArray(item['@graph'])) flat.push(...item['@graph']);
    for (const entry of flat) {
      const contactStr = entry.telephone || entry.email || '';
      if (contactStr && EMAIL_RE.test(contactStr)) {
        const match = contactStr.match(EMAIL_RE);
        if (match) emails.add(match[0].toLowerCase());
      }
      const contactPoints = entry.contactPoint || [];
      const cpArr = Array.isArray(contactPoints) ? contactPoints : [contactPoints];
      for (const cp of cpArr) {
        if (cp?.email) {
          const match = cp.email.match(EMAIL_RE);
          if (match) emails.add(match[0].toLowerCase());
        }
      }
    }
  }
  return [...emails];
}

async function applyStealth(page) {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    const _query = navigator.permissions.query.bind(navigator.permissions);
    navigator.permissions.query = p => p.name === 'notifications'
      ? Promise.resolve({ state: 'denied' })
      : _query(p);
    const _ctx = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (...a) {
      const c = _ctx.apply(this, a);
      if (c && a[0] === '2d') {
        const _gid = c.getImageData;
        c.getImageData = function (...ia) {
          const d = _gid.apply(this, ia);
          for (let i = 0; i < d.data.length; i += 100) d.data[i] ^= 1;
          return d;
        };
      }
      return c;
    };
    const originalToString = Function.prototype.toString;
    Function.prototype.toString = function () {
      if (this === navigator.webdriver) return 'function () { [native code] }';
      return originalToString.call(this);
    };
  });
}

async function detectCaptcha(page) {
  return page.evaluate(() => {
    const text = document.body?.innerText || '';
    const keywords = ['unusual traffic', 'captcha', 'are you a robot',
      'not a robot', 'verify', 'recaptcha', 'hcaptcha', 'automated queries'];
    return keywords.some(k => text.toLowerCase().includes(k));
  });
}

async function handleDisambiguation(page) {
  const suggestions = await page.$$('a[href*="/maps/search/"], div[role="feed"] a');
  for (const el of suggestions) {
    const text = await el.textContent().catch(() => '');
    if (text && text.length < 120) {
      const href = await el.getAttribute('href').catch(() => '');
      if (href && href.includes('/maps/search/')) {
        await page.goto(href.startsWith('http') ? href : `https://www.google.com${href}`, { waitUntil: 'load', timeout: 20000 });
        await page.waitForTimeout(3000);
        return true;
      }
    }
  }
  return false;
}

function cleanText(text) {
  return text.replace(/[\uE000-\uF8FF]/g, '').replace(/\u200B/g, '').trim();
}

function buildSearchUrl(query, domain) {
  const base = domain ? `https://${domain}` : 'https://www.google.com';
  return `${base}/maps/search/${encodeURIComponent(query)}/`;
}

const processedUrls = new Set();
const pendingEnrichment = new Map();
let totalScraped = 0;
let totalWithEmail = 0;

const router = createPlaywrightRouter();

router.addHandler('search', async ({ page, request, session, enqueueLinks, pushData, log: l }) => {
  const { query, options, domain } = request.userData;
  l.info(`Search: "${query}"`);

  const searchUrl = buildSearchUrl(query, domain);
  await page.goto(searchUrl, { waitUntil: 'load', timeout: 30000 });
  await page.waitForTimeout(3000);

  if (await detectCaptcha(page)) {
    session?.retire();
    throw new Error('CAPTCHA detected on search page');
  }

  let feedFound = true;
  try {
    await page.waitForSelector('div[role="feed"]', { timeout: 15000 });
  } catch {
    feedFound = false;
  }

  if (!feedFound) {
    l.warning(`No feed for "${query}" — trying disambiguation`);
    const handled = await handleDisambiguation(page);
    if (!handled) {
      l.warning(`Could not resolve "${query}" — pushing error to dataset`);
      await pushData({
        _error: true,
        query,
        message: `No results or disambiguation failed for this query`,
        scrapedAt: new Date().toISOString(),
      });
      return;
    }
    try {
      await page.waitForSelector('div[role="feed"]', { timeout: 15000 });
    } catch {
      await pushData({
        _error: true,
        query,
        message: `No results found after disambiguation`,
        scrapedAt: new Date().toISOString(),
      });
      return;
    }
  }

  let prevCount = 0;
  let stale = 0;
  while (stale < 10) {
    const count = await page.$$eval('a[href*="/maps/place/"]', els => els.length);
    if (count >= 500) break;
    if (count > prevCount) { prevCount = count; stale = 0; }
    else stale++;
    await page.evaluate(() => {
      const f = document.querySelector('div[role="feed"]');
      if (f) f.scrollTop = f.scrollHeight;
    });
    await page.waitForTimeout(2000);
  }

  const allUrls = await page.$$eval('a[href*="/maps/place/"]', els =>
    els.map(el => el.getAttribute('href')).filter(Boolean)
      .map(h => h.startsWith('http') ? h : `https://www.google.com${h}`)
      .filter((v, i, a) => a.indexOf(v) === i)
  );

  const remaining = Math.max(0, options.maxResults - totalScraped);
  const urls = allUrls.slice(0, remaining);

  l.info(`Found ${urls.length} listings for "${query}" (${allUrls.length} available, budget ${remaining})`);
  Actor.setStatusMessage(`Search "${query}": ${urls.length} listings found`);

  for (const url of urls) {
    const normalized = url.split('@')[0].split('?')[0];
    if (processedUrls.has(normalized)) continue;
    processedUrls.add(normalized);

    await enqueueLinks({
      urls: [url],
      label: 'listing',
      userData: { query, options },
    });
  }
});

router.addHandler('listing', async ({ page, request, session, pushData, log: l }) => {
  const { query, options } = request.userData;

  if (totalScraped >= options.maxResults) {
    l.info(`Hit global cap (${options.maxResults}), skipping ${request.url}`);
    return;
  }

  l.info(`Listing: ${request.url}`);

  try {
    await page.waitForSelector('h1', { timeout: 15000 });
    await page.waitForTimeout(2500);
  } catch {
    l.warning('Listing page load timeout');
    return;
  }

  if (await detectCaptcha(page)) {
    session?.retire();
    throw new Error('CAPTCHA on listing page');
  }

  const name = await page.$eval('h1', el => el.textContent?.trim() || '').catch(() => '');
  if (!name) return;

  const data = {
    query,
    name,
    placeUrl: request.url,
    scrapedAt: new Date().toISOString(),
  };

  const addr = await page.$eval('button[data-item-id*="address"]', el =>
    el.querySelector('div')?.textContent?.trim() || ''
  ).catch(() => null);
  if (addr) data.address = cleanText(addr);

  if (options.extractPhone) {
    const phone = await page.$eval('button[data-item-id*="phone"]', el =>
      el.querySelector('div')?.textContent?.trim() || ''
    ).catch(() => null);
    if (phone) data.phone = cleanText(phone);
  }

  if (options.extractWebsite) {
    const website = await page.$('a[data-item-id*="authority"]')
      .then(el => el?.getAttribute('href') || null).catch(() => null);
    if (website) {
      data.website = website;
      data.websiteDomain = new URL(website).hostname.replace('www.', '');
    }
  }

  if (options.extractRating) {
    const rt = await page.evaluate(() => {
      const el = document.querySelector('[role="img"]');
      return el?.getAttribute('aria-label') || '';
    }).catch(() => '');
    const rm = rt.match(/[\d.]+/);
    if (rm) {
      data.rating = parseFloat(rm[0]);
      const rc = await page.$eval('button[aria-label*="reviews"]', el =>
        parseInt((el.textContent || '0').replace(/[^0-9]/g, '')) || 0
      ).catch(() => 0);
      if (rc) data.reviewCount = rc;
    }
  }

  if (options.extractCategory) {
    const cat = await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('[role="main"] button, [role="main"] a[jsaction]'));
      const SKIP = ['see photos', 'add a photo', 'add photos', 'add photo', 'overview',
        'reviews', 'about', 'menu', 'directions', 'website', 'message', 'save', 'share',
        'call', 'ask a question', 'edit', 'report', 'update', 'claim this business'];
      const b = btns.find(x => {
        const raw = (x.textContent || '').trim();
        const t = raw.replace(/[\uE000-\uF8FF]/g, '').trim();
        return t.length > 0 && t.length < 40
          && !raw.includes('\n')
          && !x.hasAttribute('data-item-id')
          && !SKIP.includes(t.toLowerCase());
      });
      const raw = b?.textContent?.trim() || null;
      return raw ? raw.replace(/[\uE000-\uF8FF]/g, '').trim() : null;
    }).catch(() => null);
    if (cat) data.category = cat;
  }

  if (options.extractCoordinates) {
    const coords = await page.evaluate(() => {
      const cur = document.querySelector('link[rel="canonical"]')?.getAttribute('href') || location.href;
      const a = cur.match(/!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)/);
      if (a) return { lat: parseFloat(a[1]), lng: parseFloat(a[2]) };
      const b = cur.match(/@(-?\d+\.\d+),(-?\d+\.\d+)/);
      if (b) return { lat: parseFloat(b[1]), lng: parseFloat(b[2]) };
      return null;
    }).catch(() => null);
    if (coords) {
      data.coordinates = `${coords.lat}, ${coords.lng}`;
    }
  }

  if (options.extractHours) {
    const hb = await page.$('button[data-item-id*="oh"]');
    if (hb) {
      await hb.click().catch(() => {});
      await page.waitForTimeout(800);
      const hrs = await page.$$eval('table tr', rows =>
        rows.map(r => {
          const c = r.querySelectorAll('td');
          return c.length >= 2 ? `${c[0].textContent?.trim()}: ${c[1].textContent?.trim()}` : null;
        }).filter(Boolean)
      ).catch(() => null);
      if (hrs?.length) data.hours = hrs;
    }
  }

  totalScraped++;

  await pushData(data);

  if (options.extractEmails && data.website) {
    pendingEnrichment.set(request.url, data);
    const q = await Actor.openRequestQueue();
    await q.addRequest({
      url: data.website,
      label: 'website',
      uniqueKey: `email:${data.website}`,
      userData: { listingUrl: request.url },
    });
  }

  Actor.setStatusMessage(
    `Scraped: ${totalScraped} listings${totalWithEmail > 0 ? `, ${totalWithEmail} with emails` : ''}`
  );
});

router.addHandler('website', async ({ page, pushData, request, log: l }) => {
  const { listingUrl } = request.userData;

  l.info(`Emails from: ${request.url}`);

  try {
    await page.goto(request.url, { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(2000);
  } catch {
    l.warning(`Could not load ${request.url}`);
    return;
  }

  if (await detectCaptcha(page)) {
    l.warning(`CAPTCHA on ${request.url}`);
    return;
  }

  const htmlEmails = await extractEmails(page);
  const jsonld = await extractJsonLd(page);
  const jsonldEmails = extractEmailFromJsonLd(jsonld);
  const allEmails = [...new Set([...htmlEmails, ...jsonldEmails])];

  const cleanEmails = allEmails
    .map(sanitizeEmail)
    .filter(Boolean);

  if (cleanEmails.length > 0) {
    const listing = pendingEnrichment.get(listingUrl);
    if (listing) {
      listing.emails = cleanEmails;
      listing.emailSource = jsonldEmails.length > 0 ? 'jsonld+html' : 'html';
      await pushData(listing);
      totalWithEmail++;
    }
  }
});

async function flushPendingEnrichment() {
  if (pendingEnrichment.size > 0) {
    log.info(`${pendingEnrichment.size} website requests still pending — listing data already saved`);
    pendingEnrichment.clear();
  }
}

async function main() {
  const input = await Actor.getInput() || {};
  const {
    searchQueries = ['plumbers in Austin, TX'],
    maxResults = 50,
    extractEmails = true,
    extractPhone = true,
    extractWebsite = true,
    extractRating = true,
    extractCoordinates = true,
    extractCategory = true,
    extractHours = false,
    maxConcurrency = 3,
    proxyCountry = '',
    domain = '',
  } = input;

  if (!searchQueries.length) {
    throw new Error('At least one search query is required in searchQueries');
  }
  if (maxConcurrency < 1 || maxConcurrency > 20) {
    throw new Error('maxConcurrency must be between 1 and 20');
  }
  if (domain && !/^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(domain)) {
    throw new Error(`Invalid domain format: "${domain}". Use format like "google.co.uk"`);
  }

  const options = {
    extractEmails, extractPhone, extractWebsite, extractRating,
    extractCoordinates, extractCategory, extractHours,
    maxResults,
  };

  const totalCap = maxResults;

  log.info('=== Google Maps Scraper ===');
  log.info(`Queries: ${searchQueries.length}, Total limit: ${maxResults}`);
  log.info(`Concurrency: ${maxConcurrency}, Domain: ${domain || 'google.com'}, Email: ${extractEmails}`);
  log.info(`Fields: ${['phone', 'website', 'rating', 'coordinates', 'category', 'hours']
    .filter(k => options[`extract${k.charAt(0).toUpperCase() + k.slice(1)}`])
    .join(', ')}`);

  Actor.setStatusMessage('Starting crawl...');

  const config = {
    requestHandler: router,
    maxConcurrency,
    useSessionPool: true,
    persistCookiesPerSession: true,
    sessionPoolOptions: {
      maxPoolSize: maxConcurrency * 2,
    },
    maxRequestRetries: 3,
    maxRequestsPerCrawl: searchQueries.length + totalCap + (extractEmails ? totalCap : 0),
    requestHandlerTimeoutSecs: 60,
    launchContext: {
      launchOptions: {
        headless: true,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-gpu',
          '--disable-background-timer-throttling',
          '--disable-renderer-backgrounding',
        ],
      },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    },
    preNavigationHooks: [
      async (ctx) => {
        await applyStealth(ctx.page);
        await ctx.page.setViewportSize({ width: 1920, height: 1080 });
      },
    ],
    failedRequestHandler: async ({ request, log: l }) => {
      l.warning(`Failed after retries: ${request.url} (${request.label})`);
    },
  };

  if (proxyCountry) {
    config.proxyConfiguration = new ProxyConfiguration({ countryCode: proxyCountry });
    log.info(`Proxy country: ${proxyCountry}`);
  }

  log.info(`Max requests: ${config.maxRequestsPerCrawl} (${searchQueries.length} search + ${totalCap} listings${extractEmails ? ` + ${totalCap} websites` : ''})`);

  const crawler = new PlaywrightCrawler(config);

  const start = searchQueries.map(q => ({
    url: buildSearchUrl(q, domain),
    label: 'search',
    userData: { query: q, options, domain },
  }));

  await crawler.run(start);

  await flushPendingEnrichment();

  const results = (await Dataset.getData()).items;
  const listings = results.filter(r => !r._error);
  const errors = results.filter(r => r._error);
  const withEmail = listings.filter(r => r.emails?.length > 0).length;

  log.info('=== Complete ===');
  log.info(`Listings: ${listings.length}, Errors: ${errors.length}, With emails: ${withEmail}`);
  log.info(`Total emails found: ${results.reduce((s, r) => s + (r.emails?.length || 0), 0)}`);

  Actor.setStatusMessage(`Done: ${listings.length} listings, ${errors.length} failed queries, ${withEmail} with emails`);
}

Actor.main(main, { statusMessage: 'Google Maps Scraper initializing' })
  .catch(err => {
    log.error(`Fatal: ${err.message}`);
    process.exit(1);
  });
