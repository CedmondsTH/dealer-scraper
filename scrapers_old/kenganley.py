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
        
        # Use panel-body selector which wraps each dealership card
        panels = soup.select('div.panel-body')
        self.logger.info(f"Ken Ganley Scraper: Found {len(panels)} panels")
        
        for panel in panels:
            # Name is in h4
            name_el = panel.find('h4')
            if not name_el:
                continue
            name = self._extract_text_safely(name_el)
            
            # Address is in the first paragraph
            address_el = panel.find('p')
            street = ""
            city = ""
            state = ""
            zip_code = ""
            
            if address_el:
                full_address = self._extract_text_safely(address_el)
                # Parse address: "315 South Mill Street, Dalton, OH 44618"
                if ',' in full_address:
                    parts = full_address.split(',')
                    if len(parts) >= 2:
                        street = parts[0].strip()
                        # Handle the rest
                        rest = parts[-1].strip().split() # "OH 44618" or "State Zip"
                        if len(rest) >= 2:
                            zip_code = rest[-1]
                            state = rest[-2]
                        
                        # City is usually the part before state/zip
                        if len(parts) == 3:
                             city = parts[1].strip()
                        elif len(parts) == 2:
                             # Street, City State Zip
                             city_state_zip = parts[1].strip()
                             # This is harder to split without more logic, but let's try
                             # removing state and zip from the end
                             if state and zip_code:
                                 city = city_state_zip.replace(state, "").replace(zip_code, "").strip()
                    else:
                        street = full_address
                else:
                    street = full_address

            # Phone
            phone = ""
            # Look for "Sales Phone:" text pattern
            phone_marker = panel.find(string=lambda x: x and "Sales Phone:" in x)
            if phone_marker:
                # Usually in a <p><strong>Sales Phone:</strong><br>Number</p>
                # text of p would be "Sales Phone:Number"
                parent = phone_marker.find_parent('p')
                if parent:
                    phone = self._extract_text_safely(parent).replace("Sales Phone:", "").strip()
            
            # Website
            website = ""
            # Look for link with text "Visit Our Website"
            website_link = panel.find('a', string=lambda x: x and "Visit Our Website" in x)
            if website_link:
                website = website_link.get('href', '')
            
            # Fallback website if not found
            if not website and url:
                website = url

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
                
        self.logger.info(f"Ken Ganley Scraper: Extracted {len(dealerships)} dealerships")
        return dealerships

