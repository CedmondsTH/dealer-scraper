"""
JSON-LD scraping strategy for structured data extraction.

This strategy extracts dealer information from JSON-LD structured data
commonly found in automotive dealer websites.
"""

from typing import List, Dict, Any
import json
import sys
from bs4 import BeautifulSoup

from ..base_scraper import ScraperStrategy


class JsonLdStrategy(ScraperStrategy):
    """Extracts dealer data from JSON-LD structured data."""
    
    @property
    def strategy_name(self) -> str:
        return "JSON-LD Structured Data"
    
    def can_handle(self, html: str, page_url: str) -> bool:
        """Check if page contains JSON-LD structured data."""
        soup = BeautifulSoup(html, "lxml")
        json_ld_scripts = soup.find_all("script", {"type": "application/ld+json"})
        return len(json_ld_scripts) > 0
    
    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealers from JSON-LD structured data."""
        soup = BeautifulSoup(html, "lxml")
        dealers = []
        
        # Find all JSON-LD script tags
        for script in soup.find_all("script", {"type": "application/ld+json"}):
            try:
                data = json.loads(script.string or "")
            except json.JSONDecodeError:
                print(f"DEBUG: Failed to parse JSON-LD script", file=sys.stderr)
                continue
            
            # Handle different JSON-LD structures
            items = self._extract_items_from_data(data)
            
            for item in items:
                dealer = self._extract_dealer_from_item(item, page_url)
                if dealer:
                    dealers.append(dealer)
        
        print(f"DEBUG: JSON-LD strategy extracted {len(dealers)} dealers", file=sys.stderr)
        return dealers
    
    def _extract_items_from_data(self, data: Any) -> List[Dict[str, Any]]:
        """Extract items from JSON-LD data structure."""
        items = []
        
        # Recursively collect any nested objects that match relevant @type
        relevant_types = {"AutoDealer", "AutomotiveBusiness", "LocalBusiness"}

        def collect(obj, out: List[Dict[str, Any]]):
            if isinstance(obj, dict):
                obj_type = obj.get("@type")
                if isinstance(obj_type, list):
                    if any(t in relevant_types for t in obj_type):
                        out.append(obj)
                elif isinstance(obj_type, str) and obj_type in relevant_types:
                    out.append(obj)

                # Traverse nested properties that often contain lists of entities
                for v in obj.values():
                    collect(v, out)
            elif isinstance(obj, list):
                for it in obj:
                    collect(it, out)

        roots: List[Any] = []
        if isinstance(data, dict):
            roots = [data]
        elif isinstance(data, list):
            roots = data

        results: List[Dict[str, Any]] = []
        for root in roots:
            collect(root, results)

        return results
    
    def _is_corporate_entry(self, item: Dict[str, Any], name: str) -> bool:
        """Check if this JSON-LD item represents a corporate entity rather than a dealer location."""
        
        # Filter by name patterns
        corporate_names = [
            "auto group", "automotive group", "group", "motors", "corporation", "corp",
            "sales", "service", "parts", "department", "headquarters", "hq"
        ]
        
        name_lower = name.lower()
        if any(corp_term in name_lower for corp_term in corporate_names):
            return True
        
        # Filter by JSON-LD @type
        json_type = item.get("@type", "")
        if isinstance(json_type, list):
            json_type = json_type[0] if json_type else ""
        
        # Corporate types that should be filtered out
        corporate_types = [
            "AutomotiveBusiness", "AutoDealer", "AutoRepair", "AutoBodyShop", 
            "Organization", "Corporation", "LocalBusiness"
        ]
        
        if any(corp_type in json_type for corp_type in corporate_types):
            # Additional check: if it has "department" field, it's likely corporate
            if "department" in item:
                return True
        
        return False
    
    def _extract_dealer_from_item(self, item: Dict[str, Any], page_url: str) -> Dict[str, Any]:
        """Extract dealer information from a JSON-LD item."""
        try:
            name = item.get("name", "")
            if not name:
                return None
            
            # Filter out corporate/non-dealer entries
            if self._is_corporate_entry(item, name):
                print(f"DEBUG: Skipping corporate entry: {name}", file=sys.stderr)
                return None
            
            # Extract address information
            address_info = item.get("address", {})
            if isinstance(address_info, list) and len(address_info) > 0:
                address_info = address_info[0]
            
            street = ""
            city = ""
            state = ""
            zip_code = ""
            
            if isinstance(address_info, dict):
                street = address_info.get("streetAddress", "")
                city = address_info.get("addressLocality", "")
                state = address_info.get("addressRegion", "")
                zip_code = address_info.get("postalCode", "")
            elif isinstance(address_info, str):
                # Sometimes address is just a string
                from utils.address_parser import parse_address
                street, city, state, zip_code = parse_address(address_info)
            
            # Extract contact information
            phone = item.get("telephone", "")
            if isinstance(phone, list) and len(phone) > 0:
                phone = phone[0]
            
            # Extract website
            website = item.get("url", page_url)
            if isinstance(website, list) and len(website) > 0:
                website = website[0]
            
            return {
                "name": name,
                "street": street,
                "city": city,
                "state": state,
                "zip": zip_code,
                "phone": phone,
                "website": website
            }
            
        except Exception as e:
            print(f"DEBUG: Error extracting dealer from JSON-LD item: {e}", file=sys.stderr)
            return None