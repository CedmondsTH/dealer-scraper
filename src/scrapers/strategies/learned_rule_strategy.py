from typing import List, Dict, Any
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from ..base_scraper import ScraperStrategy
from ...services.rule_store import RuleStore


class LearnedRuleExtractorStrategy(ScraperStrategy):
    def __init__(self, store: RuleStore | None = None) -> None:
        self.store = store or RuleStore()

    @property
    def strategy_name(self) -> str:
        return "Learned Rule Extractor"

    def can_handle(self, html: str, page_url: str) -> bool:
        parsed = urlparse(page_url)
        host = (parsed.hostname or "").lower()
        path = parsed.path or "/"
        
        # Check domain-specific rules first
        rules = self.store.list_for_host(host)
        if any(re.search(r.path_pattern, path) for r in rules):
            return True
            
        # Check pattern-based rules
        pattern_rules = self.store.list_for_host("*pattern*")
        if pattern_rules:
            layout_signature = self._generate_layout_signature(html)
            if layout_signature:
                return any(r.path_pattern == layout_signature for r in pattern_rules)
                
        return False

    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        parsed = urlparse(page_url)
        host = (parsed.hostname or "").lower()
        path = parsed.path or "/"
        
        # Try domain-specific rules first
        rules = self.store.list_for_host(host)
        
        # If no domain rules, try pattern-based rules
        if not rules:
            pattern_rules = self.store.list_for_host("*pattern*")
            layout_signature = self._generate_layout_signature(html)
            if layout_signature:
                rules = [r for r in pattern_rules if r.path_pattern == layout_signature]
        
        soup = BeautifulSoup(html, "lxml")
        dealers: List[Dict[str, Any]] = []

        for r in rules:
            # For pattern rules, we already matched, skip path check
            if r.host != "*pattern*" and not re.search(r.path_pattern, path):
                continue
            cards = soup.select(r.card_selector)
            for card in cards:
                name_el = card.select_one(r.fields.get("name", "")) if r.fields.get("name") else None
                name = name_el.get_text(strip=True) if name_el else ""
                street_el = card.select_one(r.fields.get("street", "")) if r.fields.get("street") else None
                street = street_el.get_text(strip=True) if street_el else ""
                csz_el = card.select_one(r.fields.get("city_state_zip", "")) if r.fields.get("city_state_zip") else None
                csz = csz_el.get_text(strip=True) if csz_el else ""
                city = state = zip_code = ""
                if csz:
                    m = re.search(r"([^,]+),\s*([A-Za-z]{2})\s*(\d{5})", csz)
                    if m:
                        city, state, zip_code = m.groups()
                phone = ""
                ph_el = card.select_one(r.fields.get("phone", "")) if r.fields.get("phone") else None
                if ph_el:
                    t = ph_el.get_text(" ", strip=True)
                    pm = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", t)
                    if pm:
                        phone = pm.group(0)

                site = page_url
                website_selector = r.fields.get("website", "a[href]")
                a = card.select_one(website_selector) if website_selector else card.select_one("a[href]")
                if a and a.has_attr("href") and a["href"].startswith("http"):
                    site = a["href"]

                if name and (street or city):
                    dealers.append({
                        "Name": name,
                        "Street": street,
                        "City": city,
                        "State": state.upper(),
                        "Zip": zip_code,
                        "Phone": phone,
                        "Website": site,
                        "Country": "USA",
                        "DealerType": "New Car Dealer",
                        "CarBrands": "",
                    })

        return dealers

    def _generate_layout_signature(self, html: str) -> str:
        """Generate a layout signature based on HTML structure patterns."""
        try:
            soup = BeautifulSoup(html, "lxml")
            
            # Analyze structure patterns
            signatures = []
            
            # Count common container patterns
            sections = len(soup.find_all(['section', 'div', 'article'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['location', 'dealer', 'store', 'office', 'branch']
            )))
            if sections >= 3:
                signatures.append(f"containers:{sections}")
            
            # Check for list patterns
            lists = soup.find_all(['ul', 'ol'])
            list_items = sum(len(lst.find_all('li')) for lst in lists)
            if list_items >= 3:
                signatures.append(f"lists:{list_items}")
            
            # Check for address-like patterns
            address_patterns = soup.find_all(text=lambda text: text and re.search(
                r'\d+\s+[A-Za-z\s]+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Dr|Drive)',
                text
            ))
            if len(address_patterns) >= 3:
                signatures.append("addresses:multiple")
            
            # Check for phone patterns
            phone_patterns = soup.find_all(text=lambda text: text and re.search(
                r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
                text
            ))
            if len(phone_patterns) >= 3:
                signatures.append("phones:multiple")
            
            # Check for state patterns (common in dealer listings)
            state_patterns = soup.find_all(text=lambda text: text and re.search(
                r'\b[A-Z]{2}\s+\d{5}',  # State code + ZIP
                text
            ))
            if len(state_patterns) >= 3:
                signatures.append("states:multiple")
            
            # Generate final signature
            if len(signatures) >= 2:  # Need at least 2 pattern indicators
                return "layout:" + "|".join(sorted(signatures))
            
            return ""
            
        except Exception:
            return ""

