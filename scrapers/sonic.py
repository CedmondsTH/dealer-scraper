"""Scraper for Sonic Automotive dealership websites."""

from typing import List
from scrapers.base import BaseScraper
from models.dealership import DealershipData


class SonicScraper(BaseScraper):
    """Scraper for Sonic Automotive dealership websites."""
    
    def __init__(self):
        super().__init__("Sonic Automotive")
    
    def can_handle(self, html: str, url: str) -> bool:
        """Check if this is a Sonic Automotive website."""
        return "sonicautomotive.com" in url.lower()
    
    def extract(self, html: str, url: str) -> List[DealershipData]:
        """Extract dealership data from Sonic Automotive website."""
        soup = self._get_soup(html)
        dealerships = []
        
        # Find all dealership listings in the proximity dealer list
        # Structure: ol#proximity-dealer-list > li.info-window
        dealer_list = soup.find('ol', id='proximity-dealer-list')
        
        if not dealer_list:
            self.logger.warning(f"{self.name}: Could not find proximity-dealer-list")
            return dealerships
        
        # Find all list items that are actual dealerships (have info-window class and vcard)
        dealer_items = dealer_list.find_all('li', class_='info-window')
        
        self.logger.info(f"{self.name}: Found {len(dealer_items)} dealer items")
        
        for item in dealer_items:
            try:
                vcard = item.find('div', class_='vcard')
                if not vcard:
                    continue
                
                # Extract name from span.org inside the link
                name_elem = vcard.find('span', class_='org')
                name = self._extract_text_safely(name_elem)
                
                # Extract website from the parent link
                website_elem = vcard.find('a', class_='url')
                website = self._extract_attribute_safely(website_elem, 'href', url)
                
                # Extract address components
                adr_elem = vcard.find('p', class_='adr')
                if adr_elem:
                    street_elem = adr_elem.find('span', class_='street-address')
                    city_elem = adr_elem.find('span', class_='locality')
                    state_elem = adr_elem.find('span', class_='region')
                    zip_elem = adr_elem.find('span', class_='postal-code')
                    
                    street = self._extract_text_safely(street_elem)
                    city = self._extract_text_safely(city_elem)
                    state = self._extract_text_safely(state_elem)
                    zip_code = self._extract_text_safely(zip_elem)
                else:
                    street = city = state = zip_code = ""
                
                # Extract phone from li.tel span.value
                phone_elem = vcard.find('span', class_='value')
                phone = self._extract_text_safely(phone_elem)
                
                # Only add if we have at least a name and street
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
                    
            except Exception as e:
                self.logger.warning(f"{self.name}: Error parsing dealer item: {e}")
                continue
        
        self.logger.info(f"{self.name}: Extracted {len(dealerships)} dealerships")
        return dealerships

