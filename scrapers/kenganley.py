"""
Ken Ganley Automotive Group specific scraper.
"""

from typing import List
from scrapers.base import BaseScraper
from models.dealership import DealershipData

class KenGanleyScraper(BaseScraper):
    """Scraper for Ken Ganley Automotive Group websites."""
    
    def __init__(self):
        super().__init__("Ken Ganley")
    
    def can_handle(self, html: str, url: str) -> bool:
        """Check if this is a Ken Ganley website."""
        return "kenganley" in url.lower() or "Ken Ganley" in html
    
    def extract(self, html: str, url: str) -> List[DealershipData]:
        """Extract dealership data from Ken Ganley locations page."""
        soup = self._get_soup(html)
        dealerships = []
        
        # The structure seems to be lists of items, often with nested generic divs.
        # Based on the snapshot, dealership info is often in h4 headings and paragraphs
        # following them within a container.
        
        # Strategy: Look for headings that look like dealership names, then check siblings/children
        
        # Common pattern in the log:
        # heading "Sarchione Chrysler Dodge Jeep Ram" [level=4]
        #   paragraph: 315 South Mill Street, Dalton, OH 44618
        #   ... sales phone ...
        
        items = soup.find_all('div', class_=lambda x: x and 'inventory-item' in x) # This is a guess, refining below
        
        # Trying a more generic approach based on the text structure observed
        # Find all h4 tags, as they seem to contain dealer names
        headings = soup.find_all('h4')
        
        for h4 in headings:
            name = self._extract_text_safely(h4)
            if not name:
                continue
                
            # Initialize data
            street = ""
            city = ""
            state = ""
            zip_code = ""
            phone = ""
            website = ""
            
            # Address usually follows in a paragraph
            address_p = h4.find_next_sibling('p')
            if address_p:
                address_text = self._extract_text_safely(address_p)
                # Parse address: "315 South Mill Street, Dalton, OH 44618"
                if ',' in address_text:
                    parts = address_text.split(',')
                    if len(parts) >= 2:
                        street = parts[0].strip()
                        rest = parts[1].strip().split()
                        if len(rest) >= 3:
                             # Start from end to get zip, state
                             zip_code = rest[-1]
                             state = rest[-2]
                             city = " ".join(rest[:-2])
                        elif len(parts) >= 3:
                             # "Street, City, State Zip"
                             city = parts[1].strip()
                             state_zip = parts[2].strip().split()
                             if len(state_zip) >= 2:
                                 state = state_zip[0]
                                 zip_code = state_zip[1]

            # Phone usually in a following list or paragraph
            # Looking for "Sales Phone:" pattern
            container = h4.parent
            if container:
                # Look for phone links or text
                phone_text = container.find(string=lambda x: x and "Sales Phone:" in x)
                if phone_text:
                    phone_parent = phone_text.parent
                    if phone_parent:
                         # The number might be in the next sibling or part of the same text node
                         # In the log: strong: "Sales Phone:", text: (330) 828-2263
                         # It implies they are siblings in a paragraph
                         phone = self._extract_text_safely(phone_parent.parent).replace("Sales Phone:", "").strip()
                
                # Website
                # Look for "Visit Our Website" link
                website_link = container.find('a', string=lambda x: x and "Visit Our Website" in x)
                if website_link:
                    website = website_link.get('href', '')

            if name and street:
                dealership = DealershipData(
                    name=name,
                    street=street,
                    city=city,
                    state=state,
                    zip=zip_code,
                    phone=phone,
                    website=website
                )
                dealerships.append(dealership)
                
        return dealerships

