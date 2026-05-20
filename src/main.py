import asyncio
import json
import logging
import time
from urllib.parse import urlparse

from apify import Actor

from src.client import GoogleMapsClient
from src.parser import extract_app_state, extract_place_from_array, parse_hours
from src.email_extractor import extract_emails_from_website
from src.email_verifier import verify_email_deliverability
from src.crm_formatter import format_crm_row
from src.utils import get_place_stable_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}
        search_queries = actor_input.get('searchStringsArray', [])
        location_query = actor_input.get('locationQuery', '')
        max_results = actor_input.get('maxCrawledPlacesPerSearch', 100)
        extract_emails = actor_input.get('extractEmails', True)
        verify_mode = actor_input.get('verifyEmails', 'off')
        incremental_mode = actor_input.get('incrementalMode', 'off')
        crm_format = actor_input.get('crmFormat', 'none')

        if not search_queries:
            logger.error('No search queries provided')
            return

        use_proxy = Actor.is_at_home()
        client = GoogleMapsClient(use_proxy=use_proxy)

        try:
            location = None
            if location_query:
                Actor.log.info(f'Geocoding location: {location_query}')
                location = await client.geocode_location(location_query)
                if location:
                    Actor.log.info(f'Resolved to: {location}')
                else:
                    Actor.log.warning(f'Could not geocode: {location_query}')

            lat, lng = (location['lat'], location['lng']) if location else (40.7128, -74.0060)

            seen_place_ids = set()
            if incremental_mode in ('flag', 'new-only'):
                seen_place_ids = await _load_seen_place_ids()

            total_scraped = 0

            for query in search_queries:
                if total_scraped >= max_results:
                    break

                Actor.log.info(f'Searching: {query}')
                html = await client.fetch_search_page(query, lat, lng)
                state = extract_app_state(html)

                if not state:
                    Actor.log.warning(f'Could not extract state for: {query}')
                    continue

                places_data = _extract_search_results(state)
                Actor.log.info(f'Found {len(places_data)} results for: {query}')

                for place in places_data:
                    if total_scraped >= max_results:
                        break
                    if not place or not place.get('title'):
                        continue

                    place_id = place.get('placeId') or ''
                    stable_id = get_place_stable_id(place.get('url') or '')
                    place['_placeId'] = stable_id

                    is_new = stable_id not in seen_place_ids
                    place['_isNew'] = is_new
                    place['scrapedAt'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

                    if incremental_mode == 'new-only' and not is_new:
                        continue
                    if incremental_mode == 'flag':
                        place['_isNew'] = is_new

                    if extract_emails and place.get('website'):
                        email_result = await extract_emails_from_website(
                            place['website'], client
                        )
                        place['emails'] = email_result.get('emails', [])
                        place['emailSource'] = email_result.get('source', '')

                        if place['emails'] and verify_mode != 'off':
                            verified = []
                            for e in place['emails']:
                                status = await verify_email_deliverability(e)
                                verified.append({
                                    'email': e,
                                    'deliverable': status.get('deliverable', False),
                                    'method': status.get('method', ''),
                                })
                            if verify_mode == 'filter':
                                place['emails'] = [
                                    v['email'] for v in verified if v['deliverable']
                                ]
                                place['emailVerification'] = 'filtered'
                            else:
                                place['emailVerification'] = json.dumps(verified)
                    else:
                        place['emails'] = []
                        place['emailSource'] = 'none'

                    if crm_format and crm_format != 'none':
                        headers, row = format_crm_row(place, crm_format)
                        place['_crmHeaders'] = headers
                        place['_crmRow'] = row

                    seen_place_ids.add(stable_id)
                    total_scraped += 1
                    await Actor.push_data(place)

                if total_scraped >= max_results:
                    break

            Actor.log.info(f'Total places scraped: {total_scraped}')

            if incremental_mode in ('flag', 'new-only'):
                await _save_seen_place_ids(seen_place_ids)

        finally:
            await client.close()


def _extract_search_results(state: list) -> list[dict]:
    results = []

    def walk(item):
        if isinstance(item, list):
            place = extract_place_from_array(item)
            if place:
                results.append(place)
            else:
                for child in item:
                    walk(child)

    walk(state)

    seen = set()
    deduped = []
    for r in results:
        key = r.get('title', '') + (r.get('phone') or '') + (r.get('address') or '')
        if key and key not in seen:
            seen.add(key)
            deduped.append(r)

    return deduped


async def _load_seen_place_ids() -> set:
    try:
        kv = await Actor.open_key_value_store()
        val = await kv.get_value('gmaps-seen-place-ids')
        if val:
            return set(json.loads(val))
    except Exception:
        pass
    return set()


async def _save_seen_place_ids(ids: set) -> None:
    try:
        kv = await Actor.open_key_value_store()
        await kv.set_value('gmaps-seen-place-ids', json.dumps(list(ids)))
    except Exception as e:
        logger.warning(f'Could not save seen place IDs: {e}')
