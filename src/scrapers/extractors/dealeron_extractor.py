"""
DealerOn-style location extractor.

Extracts locations from DealerOn-style 'Our Locations' pages using heuristics:
- Cards with Directions/Contact links
- Headings for dealer names
- Two-line address format
- Phone numbers
"""
import re
import logging
from typing import List, Dict, Any, Set
from bs4 import BeautifulSoup
from src.utils.address_parser import parse_address

logger = logging.getLogger(__name__)


class DealerOnExtractor:
    """Extractor for DealerOn-style location pages."""
    
    # Action link texts that indicate dealer cards
    ACTION_LINK_TEXTS = {"directions", "contact", "contact us", "visit site", "visit website"}
    
    @property
    def extractor_name(self) -> str:
        return "DealerOn Locations"
    
    def can_extract(self, soup: BeautifulSoup, page_url: str) -> bool:
        """Check if this page has DealerOn-style action links."""
        for link in soup.find_all("a", limit=20):
            text = (link.get_text(strip=True) or "").lower()
            if text in self.ACTION_LINK_TEXTS:
                return True
        return False
    
    def extract(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract locations from DealerOn-style 'Our Locations' pages."""
        dealers: List[Dict[str, Any]] = []
        containers = self._find_dealer_containers(soup)
        
        phone_pattern = re.compile(r"\(??\d{3}\)??[\-\.\s]?\d{3}[\-\.\s]?\d{4}")
        city_state_zip_pattern = re.compile(r"([^,\n]+),\s*([A-Z]{2})\s*(\d{5})(?:-\d{4})?")
        
        for container in containers:
            dealer = self._extract_dealer_from_container(
                container, phone_pattern, city_state_zip_pattern, page_url
            )
            if dealer:
                dealers.append(dealer)
        
        return dealers
    
    def _find_dealer_containers(self, soup: BeautifulSoup) -> Set[BeautifulSoup]:
        """Find dealer card containers by looking for action links."""
        containers = set()
        
        # Find candidate action links
        for link in soup.find_all("a"):
            text = (link.get_text(strip=True) or "").lower()
            if text in self.ACTION_LINK_TEXTS:
                # Walk up to a reasonable container
                parent = link
                depth = 0
                while parent and depth < 4 and parent.name not in ("section", "article", "li", "div"):
                    parent = parent.parent
                    depth += 1
                
                if parent and parent.name in ("section", "article", "li", "div"):
                    containers.add(parent)
        
        return containers
    
    def _extract_dealer_from_container(
        self,
        container: BeautifulSoup,
        phone_pattern: re.Pattern,
        city_state_zip_pattern: re.Pattern,
        page_url: str
    ) -> Dict[str, Any] | None:
        """Extract dealer information from a container element."""
        # Find dealer name from heading
        name = self._extract_name(container)
        
        # Extract address and phone from text content
        text_block = container.get_text("\n", strip=True)
        lines = [ln.strip() for ln in text_block.split("\n") if ln.strip()]
        
        street, city, state, zip_code, phone = self._parse_contact_info(
            lines, phone_pattern, city_state_zip_pattern
        )
        
        # Validate minimum requirements
        if name and (street or (city and state)):
            # Use address parser for standardization
            s_street, s_city, s_state, s_zip = parse_address(
                f"{street}, {city}, {state} {zip_code}"
            )
            return {
                "name": name,
                "street": s_street or street,
                "city": s_city or city,
                "state": (s_state or state).upper(),
                "zip": s_zip or zip_code,
                "phone": phone,
                "website": page_url,
            }
        
        return None
    
    def _extract_name(self, container: BeautifulSoup) -> str:
        """Extract dealer name from container headings."""
        # Try to find heading inside container
        name_el = container.find(["h1", "h2", "h3", "h4", "h5", "h6"])
        
        # Fall back to previous sibling heading
        if not name_el:
            name_el = container.find_previous_sibling(["h2", "h3", "h4"])
        
        # Last resort: find any previous heading
        if not name_el:
            name_el = container.find_previous(["h2", "h3"])
        
        return name_el.get_text(strip=True) if name_el else ""
    
    def _parse_contact_info(
        self,
        lines: List[str],
        phone_pattern: re.Pattern,
        city_state_zip_pattern: re.Pattern
    ) -> tuple[str, str, str, str, str]:
        """Parse street, city, state, zip, and phone from text lines."""
        street = city = state = zip_code = phone = ""
        
        # Find city/state/zip line
        idx = 0
        for i, ln in enumerate(lines):
            m = city_state_zip_pattern.search(ln)
            if m:
                city, state, zip_code = m.groups()
                idx = i
                # Street is likely the previous non-empty line
                if i > 0:
                    street = lines[i - 1]
                break
        
        # Sometimes street is above heading; best effort fallback
        if not street and idx < len(lines) - 1:
            street = lines[max(0, idx - 1)]
        
        # Find phone
        for ln in lines:
            pm = phone_pattern.search(ln)
            if pm:
                phone = pm.group(0)
                break
        
        return street, city, state, zip_code, phone

