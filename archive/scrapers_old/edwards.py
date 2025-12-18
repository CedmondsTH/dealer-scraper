"""
Edwards Auto Group specific scraping strategy.

This module handles extraction from Edwards Auto Group dealership websites
using their specific card-based layout patterns.
"""

import re
from typing import List
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from models.dealership import DealershipData
from utils.parsers import parse_address


class EdwardsScraper(BaseScraper):
    """Scraper for Edwards Auto Group dealership websites."""
    
    def __init__(self):
        super().__init__("Edwards Auto Group")
    
    def can_handle(self, html: str, url: str) -> bool:
        """Check if this is an Edwards Auto Group website."""
        return (
            "edwardsautogroup" in url.lower() or
            "Edwards" in html and "Council Bluffs" in html or
            "Edwards Chevrolet" in html or
            "Edwards CDJR" in html
        )
    
    def extract(self, html: str, url: str) -> List[DealershipData]:
        """Extract dealership data from Edwards Auto Group website."""
        soup = self._get_soup(html)
        dealerships = []
        
        # Edwards Auto Group uses a grid layout with Bootstrap columns
        # Each dealership is in a column with specific content structure
        
        # Look for Bootstrap columns that contain dealership information
        cards = soup.select("div.col-lg-4, div.col-md-6, div.col-sm-12, div[class*='col-']")
        
        # Also try generic card/container patterns
        if not cards:
            cards = soup.select("div.card, div.dealer-card, div.location")
        
        # Fallback: Look for any div containing Edwards dealership names
        if not cards:
            cards = soup.find_all(lambda tag: tag.name == 'div' and 
                                 tag.get_text() and 
                                 any(brand in tag.get_text() for brand in 
                                     ['Edwards Chevrolet', 'Edwards CDJR', 'Edwards Hyundai', 
                                      'Edwards Kia', 'Genesis of Council']))
        
        self.logger.info(f"Found {len(cards)} potential Edwards dealership cards")
        
        seen_names = set()  # Track duplicates properly
        
        for i, card in enumerate(cards):
            dealership = self._extract_from_edwards_card(card, url)
            if dealership and dealership.name:
                # Accept Edwards dealerships and Genesis (which is part of Edwards group)
                if dealership.name.startswith('Edwards') or 'Genesis' in dealership.name:
                    # Only add if not already seen (avoid duplicates)
                    if dealership.name not in seen_names:
                        self.logger.info(f"Successfully extracted: {dealership.name}")
                        dealerships.append(dealership)
                        seen_names.add(dealership.name)
                    else:
                        self.logger.info(f"Card {i+1}: Duplicate dealership skipped: {dealership.name}")
                else:
                    self.logger.info(f"Card {i+1}: Found dealership but not Edwards: {dealership.name}")
            else:
                # Debug what's in the card
                card_text = card.get_text()[:200] + "..." if len(card.get_text()) > 200 else card.get_text()
                self.logger.info(f"Card {i+1}: No valid dealership found. Content: {card_text}")
        
        if dealerships:
            self.logger.pattern_success(self.name, len(dealerships))
        
        return dealerships
    
    def _extract_from_edwards_card(self, card, url: str) -> DealershipData:
        """Extract dealership data from Edwards Auto Group card element."""
        text_content = card.get_text()
        
        # Skip if this doesn't look like a dealership card
        # Be more lenient - just require some dealership-related content
        if not any(keyword in text_content for keyword in 
                  ['Edwards', 'Sales:', 'Service:', 'Parts:', 'Genesis', 'Council Bluffs', 'Omaha', 'Storm Lake']):
            return None
        
        # Extract dealership name - look for Edwards + brand pattern
        name = self._extract_edwards_name(text_content)
        if not name:
            return None
        
        # Extract address information
        address_info = self._extract_edwards_address(text_content)
        
        # Extract phone number
        phone = self._extract_edwards_phone(text_content)
        
        # Extract website - look for buttons or links
        website = self._extract_edwards_website(card, url)
        
        # Debug data before creating DealershipData
        self.logger.info(f"Creating DealershipData: name='{name}', street='{address_info.get('street', '')}', city='{address_info.get('city', '')}', phone='{phone}'")
        
        dealership_data = DealershipData(
            name=name,
            street=address_info.get('street', ''),
            city=address_info.get('city', ''),
            state=address_info.get('state', ''),
            zip_code=address_info.get('zip', ''),
            phone=phone,
            website=website
        )
        
        self.logger.info(f"DealershipData created successfully for: {name}")
        return dealership_data
    
    def _extract_edwards_name(self, text: str) -> str:
        """Extract Edwards dealership name from text."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Pre-defined dealership names based on Edwards Auto Group structure
        known_dealerships = [
            "Edwards Chevrolet Buick GMC Cadillac",
            "Edwards CDJR Village Pointe", 
            "Edwards CDJR Council Bluffs",
            "Edwards Hyundai of Council Bluffs",
            "Edwards Kia of Council Bluffs", 
            "Edwards Chevrolet GMC of Storm Lake",
            "Edwards Chrysler Dodge Jeep RAM of Storm Lake",
            "Edwards Mitsubishi",
            "Edwards Nissan",
            "Genesis of Council Bluffs",
            # Additional possible dealerships
            "Edwards Toyota", "Edwards Ford", "Edwards Honda", 
            "Edwards Mazda", "Edwards Subaru", "Edwards Auto", "Edwards Motors"
        ]
        
        # Look for exact or partial matches
        for dealership in known_dealerships:
            if dealership in text or dealership.lower() in text.lower():
                return dealership
        
        # Fallback: Look for lines that start with "Edwards" or contain "Genesis"
        for line in lines:
            if line.startswith('Edwards') and any(brand in line for brand in 
                ['Chevrolet', 'Buick', 'GMC', 'Cadillac', 'CDJR', 'Hyundai', 'Kia', 'Toyota', 'Ford', 'Honda', 'Nissan']):
                return line
            elif 'Genesis' in line and 'Council Bluffs' in line:
                return "Genesis of Council Bluffs"
            # Even more lenient fallback - any line with Edwards + location
            elif line.startswith('Edwards') and any(loc in line for loc in ['Council Bluffs', 'Omaha', 'Storm Lake']):
                return line
        
        return ""
    
    def _extract_edwards_address(self, text: str) -> dict:
        """Extract address information from Edwards card text."""
        from utils.parsers import parse_address
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        address_info = {'street': '', 'city': '', 'state': '', 'zip': ''}
        
        # Look for full address patterns in the text
        for line in lines:
            # Check for full address pattern (street + city + state + zip)
            if re.search(r'\d+.*[A-Z]{2}\s+\d{5}', line):
                # This looks like a full address, parse it
                street, city, state, zip_code = parse_address(line)
                if street and city:
                    address_info['street'] = street
                    address_info['city'] = city
                    address_info['state'] = state
                    address_info['zip'] = zip_code
                    break
            # Look for street address only
            elif re.match(r'\d+\s+\w+', line) and not address_info['street']:
                address_info['street'] = line
            # Look for city, state zip pattern
            elif re.match(r'^[A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5}', line):
                parts = line.split(',')
                if len(parts) == 2:
                    address_info['city'] = parts[0].strip()
                    state_zip = parts[1].strip().split()
                    if len(state_zip) >= 2:
                        address_info['state'] = state_zip[0]
                        address_info['zip'] = state_zip[1]
        
        return address_info
    
    def _extract_edwards_phone(self, text: str) -> str:
        """Extract phone number from Edwards card text."""
        # Look for phone patterns after "Sales:"
        sales_match = re.search(r'Sales:\s*(\d{3}-\d{3}-\d{4})', text)
        if sales_match:
            return sales_match.group(1)
        
        # General phone pattern
        phone_match = re.search(r'(\d{3}-\d{3}-\d{4})', text)
        if phone_match:
            return phone_match.group(1)
        
        return ""
    
    def _extract_edwards_website(self, card, base_url: str) -> str:
        """Extract website from Edwards card element."""
        # Look for "Visit Our Site" or similar buttons
        for link in card.find_all('a', href=True):
            link_text = link.get_text(strip=True).lower()
            if any(phrase in link_text for phrase in ['visit our site', 'website', 'visit']):
                href = link['href']
                if href.startswith('http'):
                    return href
                elif href.startswith('/'):
                    # Convert relative URL
                    base = base_url.split('/')[0] + '//' + base_url.split('/')[2]
                    return base + href
        
        return base_url