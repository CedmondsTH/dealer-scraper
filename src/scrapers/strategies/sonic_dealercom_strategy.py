import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from ..base_scraper import ScraperStrategy


class DealerDotComLocationsStrategy(ScraperStrategy):
    """Parses Dealer.com locations pages (e.g., Sonic Automotive Locations)."""

    @property
    def strategy_name(self) -> str:
        return "Dealer.com Locations HTML"

    def can_handle(self, html: str, page_url: str) -> bool:
        soup = BeautifulSoup(html, "lxml")

        # Typical structure: <div class="dealer-list"> with <ol id="proximity-dealer-list">
        has_dealer_list = bool(
            soup.select_one("div.dealer-list ol#proximity-dealer-list")
        )

        # Presence of vcard entries with org/locality/region
        vcard_samples = soup.select("ol#proximity-dealer-list li .vcard .org")

        # Heuristic: Sonic/Dealer.com locations page, or strong vcard presence
        is_sonic = "sonicautomotive.com" in (page_url or "").lower()

        return has_dealer_list and (is_sonic or len(vcard_samples) >= 5)

    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "lxml")
        dealers: List[Dict[str, Any]] = []

        for li in soup.select("ol#proximity-dealer-list li.info-window"):
            vcard = li.select_one(".vcard")
            if not vcard:
                continue

            name_el = vcard.select_one(".org")
            name = name_el.get_text(strip=True) if name_el else ""
            if not name:
                continue

            # Address parts
            street = (
                (vcard.select_one(".street-address") or {}).get_text(strip=True)
                if vcard.select_one(".street-address")
                else ""
            )
            city = (
                (vcard.select_one(".locality") or {}).get_text(strip=True)
                if vcard.select_one(".locality")
                else ""
            )
            state = (
                (vcard.select_one(".region") or {}).get_text(strip=True)
                if vcard.select_one(".region")
                else ""
            )
            zip_code = (
                (vcard.select_one(".postal-code") or {}).get_text(strip=True)
                if vcard.select_one(".postal-code")
                else ""
            )

            # Phone
            phone_el = vcard.select_one(
                "ul.tels li.tel .value [data-phone-ref], ul.tels li.tel .value, a[href^='tel:']"
            )
            phone = ""
            if phone_el:
                text = phone_el.get_text(strip=True)
                href = getattr(phone_el, "get", lambda *_: None)("href", None)
                phone = (href[4:] if href and href.startswith("tel:") else text) or ""
            phone = re.sub(r"[^\d\-\(\)\s\+]", "", phone)

            # Website for the specific location (prefer anchor under name)
            site_el = vcard.select_one(".fn.n a.url") or vcard.select_one("a.url")
            website = site_el.get("href") if site_el else page_url

            dealers.append(
                {
                    "Name": name,
                    "Street": street,
                    "City": city,
                    "State": state,
                    "Zip": zip_code,
                    "Country": "USA",
                    "Phone": phone.strip(),
                    "Website": website.strip() if website else page_url,
                    "DealerType": "New Car Dealer",
                    "CarBrands": "",
                }
            )

        return dealers
