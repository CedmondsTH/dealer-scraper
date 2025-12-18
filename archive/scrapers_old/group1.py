"""
Group 1 Automotive specific scraping strategy.

This module handles extraction from Group 1 Automotive dealership websites
using their specific card-based layout patterns.
"""

import re
from typing import List
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from models.dealership import DealershipData
from utils.parsers import parse_address


class Group1Scraper(BaseScraper):
    """Scraper for Group 1 Automotive dealership websites."""
    
    def __init__(self):
        super().__init__("Group 1 Automotive")
    
    def can_handle(self, html: str, url: str) -> bool:
        """Check if this is a Group 1 Automotive website."""
        return (
            "group1auto" in url.lower() or
            "div.dealer-card" in html or
            "div.g1-location-card" in html
        )
    
    def extract(self, html: str, url: str) -> List[DealershipData]:
        """Extract dealership data from Group 1 Automotive website."""
        soup = self._get_soup(html)
        dealerships = []
        
        self.logger.info(f"Group 1 Scraper: Analyzing structure of {url}")
        
        # Group 1 locations page structure analysis based on snapshot
        # The snapshot shows a list of locations in generic containers
        # Hierarchy seems to be: generic -> generic -> link (Name), generic (Address), generic (Phone)
        
        # Strategy 1: Look for dealership links and their surrounding context
        # Links often have names like "Advantage BMW Midtown"
        
        # Find all links that might be dealerships
        # In the snapshot, they are often in a structure like:
        # generic -> link "Dealership Name"
        # generic -> text "Address | City, State Zip"
        
        # Let's try to find containers that have this pattern
        # We'll look for text that matches address patterns "City, State Zip"
        
        # Iterate through all text nodes to find address-like strings
        # Then look up the tree for the dealership card
        
        address_pattern = re.compile(r"\|\s*[\w\s\.-]+,\s*[A-Z]{2}\s*\d{5}")
        
        # In the snapshot, addresses are in "generic" elements as text:
        # "1305 Gray St. | Houston, TX 77002"
        
        potential_addresses = soup.find_all(string=address_pattern)
        self.logger.info(f"Group 1 Scraper: Found {len(potential_addresses)} potential addresses")
        
        for addr_text in potential_addresses:
            if not addr_text.strip():
                continue
                
            # The container of the address
            addr_container = addr_text.parent
            if not addr_container:
                continue
                
            # The dealership name is usually in a sibling element (often a previous sibling)
            # In snapshot:
            # generic (Name link)
            # generic (Address)
            
            card_container = addr_container.parent
            if not card_container:
                continue
                
            # Find name
            name = ""
            website = ""
            
            # Look for previous sibling that is a link or contains a link
            prev = addr_container.find_previous_sibling()
            if prev:
                link = prev.find('a') if prev.name != 'a' else prev
                if link:
                    name = self._extract_text_safely(link)
                    # The href is often "#", so we need to find the real website
                    # In snapshot, real website is in a "Visit Site" link in a following container
            
            if not name:
                # Try looking for a heading or link within the same container if structure is different
                name_el = card_container.find('a')
                if name_el:
                    name = self._extract_text_safely(name_el)
            
            # Parse address
            # Format: "1305 Gray St. | Houston, TX 77002"
            full_address = addr_text.strip()
            street = ""
            city = ""
            state = ""
            zip_code = ""
            
            if "|" in full_address:
                parts = full_address.split("|")
                street = parts[0].strip()
                if len(parts) > 1:
                    city_state_zip = parts[1].strip()
                    # Parse "Houston, TX 77002"
                    m = re.match(r"([\w\s\.-]+),\s*([A-Z]{2})\s*(\d{5})", city_state_zip)
                    if m:
                        city = m.group(1).strip()
                        state = m.group(2)
                        zip_code = m.group(3)
            
            # Find Phone
            # Snapshot: generic -> text "Sales:" -> link "713-289-1200"
            phone = ""
            # Look for next siblings of address container
            next_siblings = addr_container.find_next_siblings()
            for sib in next_siblings:
                if "Sales:" in sib.get_text():
                    phone_link = sib.find('a')
                    if phone_link:
                        phone = self._extract_text_safely(phone_link)
                    break
            
            # Find Website
            # Snapshot: generic (following the main info block) -> link "Visit Site"
            if not website or website == "#":
                # Traverse up to find the wrapper that contains both info and buttons
                wrapper = card_container.parent
                if wrapper:
                    visit_link = wrapper.find('a', string=lambda x: x and "Visit Site" in x)
                    if visit_link:
                        website = visit_link.get('href', '')
            
            if not website or website == "#":
                # Fallback: try "New Inventory" link
                if wrapper:
                    inv_link = wrapper.find('a', string=lambda x: x and "New Inventory" in x)
                    if inv_link:
                        website = inv_link.get('href', '')
                        # Truncate to root domain if needed
                        if website:
                            from urllib.parse import urlparse
                            parsed = urlparse(website)
                            website = f"{parsed.scheme}://{parsed.netloc}"

            if name and street:
                dealership = DealershipData(
                    name=name,
                    street=street,
                    city=city,
                    state=state,
                    zip_code=zip_code,
                    phone=phone,
                    website=website
                )
                dealerships.append(dealership)
        
        self.logger.info(f"Group 1 Scraper: Extracted {len(dealerships)} dealerships")
        return dealerships