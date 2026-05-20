import json
import re
from urllib.parse import quote

from curl_cffi import requests

CIRCULAR_PROXY = 'http://proxy.apify.com:8000'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

GOOGLE_COOKIES = {
    'CONSENT': 'YES+cb.20240211-17-p0.en+FX+111',
    'SOCS': 'CAESHAgCEhJnd3NfMjAyNDAyMTEtMTdfcgNiA2hlcgJkYgMxMjIYAiIBKA',
}

NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'


class GoogleMapsClient:
    def __init__(self, max_concurrency: int = 5, use_proxy: bool = False):
        self.session = requests.AsyncSession(
            impersonate='chrome120',
            max_concurrency=max_concurrency,
        )
        self.proxy = CIRCULAR_PROXY if use_proxy else None

    def _base_headers(self, is_json: bool = False) -> dict:
        h = {
            'User-Agent': USER_AGENT,
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        if is_json:
            h['Accept'] = 'application/json, text/plain, */*'
        else:
            h['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
            h['Upgrade-Insecure-Requests'] = '1'
        return h

    async def close(self):
        await self.session.close()

    async def geocode_location(self, location_query: str) -> dict | None:
        if not location_query:
            return None
        params = {
            'q': location_query,
            'format': 'json',
            'limit': 1,
        }
        try:
            resp = await self.session.get(
                NOMINATIM_URL,
                params=params,
                headers={
                    'User-Agent': 'gmaps-scraper-actor/1.0 (https://apify.com)',
                    'Accept': 'application/json',
                },
                proxy=self.proxy,
            )
            resp.raise_for_status()
            data = resp.json()
            if data:
                return {'lat': float(data[0]['lat']), 'lng': float(data[0]['lon'])}
        except Exception as e:
            pass
        return None

    async def fetch_search_page(
        self, query: str, lat: float, lng: float, zoom: int = 15
    ) -> str:
        q = quote(query)
        url = f'https://www.google.com/maps/search/{q}/@{lat},{lng},{zoom}z'
        resp = await self.session.get(
            url,
            headers=self._base_headers(),
            cookies=GOOGLE_COOKIES,
            proxy=self.proxy,
        )
        resp.raise_for_status()
        return resp.text

    async def fetch_place_page(self, place_url: str) -> str:
        resp = await self.session.get(
            place_url,
            headers=self._base_headers(),
            cookies=GOOGLE_COOKIES,
            proxy=self.proxy,
        )
        resp.raise_for_status()
        return resp.text

    async def fetch_page_for_pagination(
        self, pagination_url: str
    ) -> str:
        resp = await self.session.get(
            pagination_url,
            headers=self._base_headers(),
            cookies=GOOGLE_COOKIES,
            proxy=self.proxy,
        )
        resp.raise_for_status()
        return resp.text

    async def fetch_website(self, url: str, timeout: int = 10) -> str | None:
        try:
            resp = await self.session.get(
                url,
                headers={
                    'User-Agent': USER_AGENT,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                },
                timeout=timeout,
                proxy=self.proxy,
            )
            resp.raise_for_status()
            return resp.text
        except Exception:
            return None
