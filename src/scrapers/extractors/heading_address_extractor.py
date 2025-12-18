"""
Heading-Address block extractor.

Extracts dealer data from pages where dealer information appears as
headings followed by address/phone lines (e.g., Bakhtiari, Aschenbach).
"""
import re
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from src.utils.address_parser import parse_address

logger = logging.getLogger(__name__)


class HeadingAddressExtractor:
    """Extractor for heading + address block patterns."""
    
    # Navigation terms that aren't dealer names
    NAVIGATION_TERMS = [
        "explore our locations", "our locations", "find us", "visit us", "locations",
        "dealerships", "store locations", "branches", "offices", "contact us",
        "where to find us", "find a location", "location finder", "store finder"
    ]
    
    @property
    def extractor_name(self) -> str:
        return "Heading-Address Blocks"
    
    def can_extract(self, soup: BeautifulSoup, page_url: str) -> bool:
        """Check if this page has heading-address block patterns."""
        headings = soup.find_all(["h2", "h3", "h4", "h5"])
        # Simple heuristic: if there are multiple headings, this pattern might apply
        return len(headings) > 3
    
    def extract(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealers from sequences of headings followed by address/phone lines."""
        dealers: List[Dict[str, Any]] = []
        
        # Locate the Our Locations section root
        search_start = self._find_locations_section(soup)
        
        headings = search_start.find_all(["h2", "h3", "h4", "h5"], recursive=True)
        phone_pattern = re.compile(r"\(??\d{3}\)??[\-\.\s]?\d{3}[\-\.\s]?\d{4}")
        city_state_zip_pattern = re.compile(r"([^,\n]+),\s*([A-Z]{2})\s*(\d{5})(?:-\d{4})?")
        
        for h in headings:
            dealer = self._extract_dealer_from_heading(
                h, phone_pattern, city_state_zip_pattern, page_url
            )
            if dealer:
                dealers.append(dealer)
        
        return dealers
    
    def _find_locations_section(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Find the 'Our Locations' section or return the whole soup."""
        section_root = None
        for tag in soup.find_all(["h1", "h2", "h3"]):
            if (tag.get_text(strip=True) or "").lower() == "our locations":
                section_root = tag
                break
        
        if section_root and section_root.parent:
            return section_root.parent
        return section_root or soup
    
    def _extract_dealer_from_heading(
        self, 
        heading: BeautifulSoup, 
        phone_pattern: re.Pattern,
        city_state_zip_pattern: re.Pattern,
        page_url: str
    ) -> Dict[str, Any] | None:
        """Extract dealer information from a heading and its following content."""
        name = heading.get_text(" ", strip=True)
        if not name or len(name) < 3:
            return None
        
        # Filter out navigation/section headings that aren't dealer names
        if self._is_navigation_heading(name):
            logger.debug(f"Rejected navigation heading: {name}")
            return None
        
        # Collect small following sibling texts up to next heading
        blob = self._collect_following_text(heading)
        if not blob:
            return None
        
        # Find address and phone
        street, city, state, zip_code, phone = self._parse_contact_info(
            blob, phone_pattern, city_state_zip_pattern
        )
        
        if city and state:
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
    
    def _is_navigation_heading(self, name: str) -> bool:
        """Check if a heading is a navigation term, not a dealer name."""
        name_lower = name.lower()
        return any(nav_term in name_lower for nav_term in self.NAVIGATION_TERMS)
    
    def _collect_following_text(self, heading: BeautifulSoup, max_hops: int = 8) -> str:
        """Collect text content following a heading until the next heading."""
        texts: list[str] = []
        nxt = heading.next_sibling
        hops = 0
        
        while nxt and hops < max_hops:
            # Stop at the next heading
            if getattr(nxt, "name", None) in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                break
            
            # Collect text content
            if hasattr(nxt, "get_text"):
                t = nxt.get_text("\n", strip=True)
                if t:
                    texts.append(t)
            
            nxt = nxt.next_sibling
            hops += 1
        
        return "\n".join(texts)
    
    def _parse_contact_info(
        self, 
        blob: str, 
        phone_pattern: re.Pattern,
        city_state_zip_pattern: re.Pattern
    ) -> tuple[str, str, str, str, str]:
        """Parse street, city, state, zip, and phone from a text blob."""
        street = city = state = zip_code = phone = ""
        lines = [ln.strip() for ln in blob.split("\n") if ln.strip()]
        
        # Find city, state, zip
        for idx, ln in enumerate(lines):
            m = city_state_zip_pattern.search(ln)
            if m:
                city, state, zip_code = m.groups()
                # The line before is probably the street
                if idx > 0:
                    street = lines[idx - 1]
                break
        
        # Find phone
        for ln in lines:
            pm = phone_pattern.search(ln)
            if pm:
                phone = pm.group(0)
                break
        
        return street, city, state, zip_code, phone

