"""
Ray Skillman specific scraping strategy.
"""

import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup, Tag
from ..base_scraper import BaseScraper


class RaySkillmanStrategy(BaseScraper):
    """Scraper strategy specifically for Ray Skillman automotive group websites."""
    
    strategy_name = "Ray Skillman HTML"
    
    def can_handle(self, html: str, page_url: str) -> bool:
        """Check if this strategy can handle the given URL."""
        return "rayskillman.com" in page_url.lower()
    
    def extract_dealers(self, html: str, url: str) -> List[Dict[str, Any]]:
        """Extract dealer information from Ray Skillman HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        dealers = []
        
        print(f"DEBUG: Ray Skillman strategy processing {len(html)} characters")
        
        # Strategy 1: Look for location cards/containers
        location_containers = soup.find_all(['div', 'section'], class_=re.compile(r'location|dealer|store', re.I))
        print(f"DEBUG: Found {len(location_containers)} location containers")
        
        for container in location_containers:
            dealer = self._extract_dealer_from_container(container, url)
            if dealer:
                dealers.append(dealer)
        
        # Strategy 2: Look for address patterns in text
        if not dealers:
            address_pattern = re.compile(r'(\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Lane|Ln|Way|Court|Ct))', re.I)
            text_content = soup.get_text()
            addresses = address_pattern.findall(text_content)
            print(f"DEBUG: Found {len(addresses)} potential addresses in text")
            
            for address in addresses[:10]:  # Limit to reasonable number
                dealer = {
                    "name": "Ray Skillman Location",
                    "street": address,
                    "city": "",
                    "state": "",
                    "zip": "",
                    "phone": "",
                    "website": url
                }
                dealers.append(dealer)
        
        # Strategy 3: Look for structured data
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                import json
                data = json.loads(script.string or '{}')
                if isinstance(data, dict) and data.get('@type') in ['AutoDealer', 'LocalBusiness']:
                    address = data.get('address', {})
                    dealer = {
                        "name": data.get('name', 'Ray Skillman Location'),
                        "street": address.get('streetAddress', ''),
                        "city": address.get('addressLocality', ''),
                        "state": address.get('addressRegion', ''),
                        "zip": address.get('postalCode', ''),
                        "phone": data.get('telephone', ''),
                        "website": data.get('url', url)
                    }
                    dealers.append(dealer)
            except:
                continue
        
        print(f"DEBUG: Ray Skillman strategy extracted {len(dealers)} dealers")
        return dealers
    
    def _extract_dealer_from_container(self, container: Tag, base_url: str) -> Dict[str, Any]:
        """Extract dealer info from a container element."""
        try:
            # Try to find name
            name_elem = container.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            name = name_elem.get_text(strip=True) if name_elem else "Ray Skillman Location"
            
            # Try to find address components
            text = container.get_text()
            
            # Look for phone pattern
            phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
            phone_match = phone_pattern.search(text)
            phone = phone_match.group() if phone_match else ""
            
            # Look for address pattern
            address_pattern = re.compile(r'(\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr))', re.I)
            address_match = address_pattern.search(text)
            street = address_match.group() if address_match else ""
            
            # Look for city, state zip pattern
            city_state_zip_pattern = re.compile(r'([A-Za-z\s]+),\s*([A-Z]{2})\s*(\d{5})')
            csz_match = city_state_zip_pattern.search(text)
            
            if csz_match:
                city, state, zip_code = csz_match.groups()
            else:
                city = state = zip_code = ""
            
            if street or phone or any([city, state, zip_code]):
                return {
                    "name": name,
                    "street": street,
                    "city": city.strip(),
                    "state": state,
                    "zip": zip_code,
                    "phone": phone,
                    "website": base_url
                }
        except Exception as e:
            print(f"DEBUG: Error extracting from container: {e}")
        
        return None
