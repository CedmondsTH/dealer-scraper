from typing import Any, Dict, List, Optional
from urllib.parse import unquote

from bs4 import BeautifulSoup

from ..base_scraper import ScraperStrategy


class OverfuelLocationsStrategy(ScraperStrategy):
    """Parses Overfuel-powered locations pages (e.g., ALM Cars location finder)."""

    @property
    def strategy_name(self) -> str:
        return "Overfuel Locations HTML"

    def can_handle(self, html: str, page_url: str) -> bool:
        soup = BeautifulSoup(html, "html.parser")

        has_overfuel_brand = "overfuel" in html.lower()
        has_locations_header = bool(
            soup.find(text=lambda t: t and "Find a Location" in t)
        )
        has_microformat_spans = bool(
            soup.select("a[href*='google.com/maps/search'] .street-address")
        )

        return has_overfuel_brand or (has_locations_header and has_microformat_spans)

    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        dealers: List[Dict[str, Any]] = []
        seen: set[tuple[str, str, str]] = set()

        # Pass A: collect from ALL Google Maps anchors (footer contains full list)
        for anchor in soup.select("a[href*='google.com/maps/search']"):
            name_el = anchor.select_one("b, .org")
            street_el = anchor.select_one(".street-address")
            city_el = anchor.select_one(".locality")
            state_el = anchor.select_one(".region")
            zip_el = anchor.select_one(".postal-code")

            name = (name_el.get_text(strip=True) if name_el else "").strip()
            street = (street_el.get_text(strip=True) if street_el else "").strip()
            city = (city_el.get_text(strip=True) if city_el else "").strip()
            state = (state_el.get_text(strip=True) if state_el else "").strip()
            zip_code = (zip_el.get_text(strip=True) if zip_el else "").strip()

            if not name:
                href = anchor.get("href", "")
                try:
                    q = href.split("/maps/search/")[-1]
                    q = unquote(q)
                    name = q.split(",")[0].strip()
                except Exception:
                    name = ""

            if not (name and street and city and state):
                continue

            # phone: walk up to find tel nearby
            phone: Optional[str] = ""
            parent = anchor
            for _ in range(3):
                parent = parent.parent if parent and parent.parent else parent
            tel_link = (
                parent.select_one("a[href^='tel:']")
                if hasattr(parent, "select_one")
                else None
            )
            if tel_link:
                phone = tel_link.get("href", "").replace("tel:", "").strip()

            key = (name.lower(), street.lower(), city.lower())
            if key in seen:
                continue
            seen.add(key)

            dealers.append(
                {
                    "name": name,
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "phone": phone,
                    "website": page_url,
                }
            )

        # Pass B: card-based enrichment/additions (if any cards weren’t covered)
        for card in soup.select("div.card"):
            header_name_el = card.select_one(".card-header h6")
            anchor = card.select_one("a[href*='google.com/maps/search']")
            if not anchor:
                continue

            name = (
                header_name_el.get_text(strip=True) if header_name_el else ""
            ).strip()
            if not name:
                name_el = anchor.select_one("b, .org")
                if name_el:
                    name = name_el.get_text(strip=True)
            if not name:
                href = anchor.get("href", "")
                try:
                    q = href.split("/maps/search/")[-1]
                    q = unquote(q)
                    name = q.split(",")[0].strip()
                except Exception:
                    name = ""

            street_el = anchor.select_one(".street-address")
            city_el = anchor.select_one(".locality")
            state_el = anchor.select_one(".region")
            zip_el = anchor.select_one(".postal-code")
            street = (street_el.get_text(strip=True) if street_el else "").strip()
            city = (city_el.get_text(strip=True) if city_el else "").strip()
            state = (state_el.get_text(strip=True) if state_el else "").strip()
            zip_code = (zip_el.get_text(strip=True) if zip_el else "").strip()

            if not (name and street and city and state):
                continue

            tel_link = card.select_one("a[href^='tel:']")
            phone = (
                tel_link.get("href", "").replace("tel:", "").strip() if tel_link else ""
            )

            key = (name.lower(), street.lower(), city.lower())
            if key in seen:
                continue
            seen.add(key)

            dealers.append(
                {
                    "name": name,
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "phone": phone,
                    "website": page_url,
                }
            )

        return dealers
