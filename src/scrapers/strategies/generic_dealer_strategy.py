"""
Generic dealer site scraping strategy.

This strategy handles common HTML patterns used by
various dealer websites that don't have specific strategies.
"""

from typing import List, Dict, Any
import re
import sys
from bs4 import BeautifulSoup

from ..base_scraper import ScraperStrategy
from ...utils.address_parser import parse_address
from ...utils.data_cleaner import data_cleaner


class GenericDealerStrategy(ScraperStrategy):
    """Extracts dealer data from generic dealer HTML structures."""
    
    @property
    def strategy_name(self) -> str:
        return "Generic Dealer HTML"
    
    def can_handle(self, html: str, page_url: str) -> bool:
        """Check if page contains generic dealer structures."""
        soup = BeautifulSoup(html, "html.parser")
        
        # Look for common dealer patterns
        patterns = [
            "div.car-details",  # HGreg
            "div.panel.panel-default",  # Ken Ganley
            "div.location.dealer",  # Group 1 subpages
            "div.dealerInfo",  # Sierra Auto Group
            "div.fusion-layout-column",  # Gregory Auto Group
            "div.card.border-0",  # Car wash sites
            "li.location-result",  # Open Road
            "h3.h4",  # All American Auto Group
            "h2[class*='miles']",  # AutoBell
            "a:contains('Directions')",
            "a:contains('Contact')",
        ]
        
        # Check for Banister-style dealer location cards (panel-based layout)
        dealer_panels = soup.find_all('div', class_=lambda x: x and 'panel' in x and 'panel-default' in x)
        print(f"DEBUG: Found {len(dealer_panels)} dealer panels with panel/panel-default classes", file=sys.stderr)
        if len(dealer_panels) >= 3:
            print(f"DEBUG: Banister panel detection SUCCESS - found {len(dealer_panels)} panels", file=sys.stderr)
            return True
            
        # Check for Bakhtiari-style dealer location cards (location class layout)
        dealer_locations = soup.find_all('div', class_=lambda x: x and 'location' in x and 'bg-main' in x)
        print(f"DEBUG: Found {len(dealer_locations)} dealer locations with location/bg-main classes", file=sys.stderr)
        if len(dealer_locations) >= 3:
            print(f"DEBUG: Bakhtiari location detection SUCCESS - found {len(dealer_locations)} locations", file=sys.stderr)
            return True

        # Check for Colonial-style dealer listings (div.get-direction__dealer-name)
        colonial_dealers = soup.find_all('div', class_='get-direction__dealer-name')
        colonial_count = 0
        for div in colonial_dealers:
            if 'colonial' in div.get_text().lower():
                colonial_count += 1
        
        print(f"DEBUG: Found {colonial_count} Colonial-style dealer names", file=sys.stderr)
        if colonial_count >= 3:
            print(f"DEBUG: Colonial detection SUCCESS - found {colonial_count} dealers", file=sys.stderr)
            return True
        
        for pattern in patterns:
            try:
                if soup.select(pattern):
                    return True
            except Exception:
                # Some selectors like :contains aren't supported by bs4; skip errors
                pass

        # Heuristics: 'Our Locations' marker with many headings or phone numbers
        page_text = soup.get_text(" ", strip=True).lower()
        if "our locations" in page_text and len(soup.find_all(["h2", "h3", "h4"])) >= 3:
            return True
        if "dealeron" in page_text:
            return True
        if page_url and any(host in page_url.lower() for host in ["banistercars.com", "bakhtiariauto.com", "aschenbachautogroup.com", "bakerautogroup.com"]):
            return True
        
        return False
    
    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealers from generic dealer HTML structures."""
        soup = BeautifulSoup(html, "html.parser")
        dealers = []
        
        # Try different extraction methods
        banister_dealers = self._extract_banister_style_dealers(soup, page_url)
        print(f"DEBUG: Banister extraction found {len(banister_dealers)} dealers", file=sys.stderr)
        dealers.extend(banister_dealers)
        
        bakhtiari_dealers = self._extract_bakhtiari_style_dealers(soup, page_url)
        print(f"DEBUG: Bakhtiari extraction found {len(bakhtiari_dealers)} dealers", file=sys.stderr)
        dealers.extend(bakhtiari_dealers)
        
        colonial_dealers = self._extract_colonial_style_dealers(soup, page_url)
        print(f"DEBUG: Colonial extraction found {len(colonial_dealers)} dealers", file=sys.stderr)
        dealers.extend(colonial_dealers)
        
        hgreg_dealers = self._extract_hgreg_dealers(soup, page_url)
        print(f"DEBUG: HGreg extraction found {len(hgreg_dealers)} dealers", file=sys.stderr)
        dealers.extend(hgreg_dealers)
        
        ken_ganley_dealers = self._extract_ken_ganley_dealers(soup, page_url)
        print(f"DEBUG: Ken Ganley extraction found {len(ken_ganley_dealers)} dealers", file=sys.stderr)
        dealers.extend(ken_ganley_dealers)
        
        group1_dealers = self._extract_group1_subpage_dealers(soup, page_url)
        print(f"DEBUG: Group1 extraction found {len(group1_dealers)} dealers", file=sys.stderr)
        dealers.extend(group1_dealers)
        
        sierra_dealers = self._extract_sierra_auto_dealers(soup, page_url)
        print(f"DEBUG: Sierra extraction found {len(sierra_dealers)} dealers", file=sys.stderr)
        dealers.extend(sierra_dealers)
        
        gregory_dealers = self._extract_gregory_auto_dealers(soup, page_url)
        print(f"DEBUG: Gregory extraction found {len(gregory_dealers)} dealers", file=sys.stderr)
        dealers.extend(gregory_dealers)
        
        carwash_dealers = self._extract_carwash_dealers(soup, page_url)
        print(f"DEBUG: Carwash extraction found {len(carwash_dealers)} dealers", file=sys.stderr)
        dealers.extend(carwash_dealers)
        
        open_road_dealers = self._extract_open_road_dealers(soup, page_url)
        print(f"DEBUG: Open Road extraction found {len(open_road_dealers)} dealers", file=sys.stderr)
        dealers.extend(open_road_dealers)
        
        all_american_dealers = self._extract_all_american_dealers(soup, page_url)
        print(f"DEBUG: All American extraction found {len(all_american_dealers)} dealers", file=sys.stderr)
        dealers.extend(all_american_dealers)
        
        autobell_dealers = self._extract_autobell_dealers(soup, page_url)
        print(f"DEBUG: AutoBell extraction found {len(autobell_dealers)} dealers", file=sys.stderr)
        dealers.extend(autobell_dealers)
        dealeron_dealers = self._extract_dealeron_locations(soup, page_url)
        print(f"DEBUG: Dealeron extraction found {len(dealeron_dealers)} dealers", file=sys.stderr)
        dealers.extend(dealeron_dealers)
        
        heading_dealers = self._extract_heading_address_blocks(soup, page_url)
        print(f"DEBUG: Heading/Address extraction found {len(heading_dealers)} dealers", file=sys.stderr)
        dealers.extend(heading_dealers)
        
        print(f"DEBUG: Generic dealer strategy extracted {len(dealers)} dealers", file=sys.stderr)
        return dealers

    def _extract_banister_style_dealers(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealers from Banister-style location pages with panel cards."""
        dealers = []
        
        # Look for panel-based dealer cards
        dealer_panels = soup.find_all('div', class_=lambda x: x and 'panel' in x and 'panel-default' in x)
        print(f"DEBUG: _extract_banister_style_dealers found {len(dealer_panels)} panels", file=sys.stderr)
        
        if not dealer_panels:
            return dealers
            
        for panel in dealer_panels:
            # Extract dealer name from h3/strong text
            name = ""
            name_el = panel.find('h3')
            if name_el:
                strong_el = name_el.find('strong')
                if strong_el:
                    name = strong_el.get_text(strip=True).replace('\n', ' ').replace('\r', ' ')
                    # Clean up extra spaces
                    name = ' '.join(name.split())
            
            if not name:
                continue
                
            # Extract address and phone from paragraph elements
            street, city, state, zip_code = "", "", "", ""
            phone = ""
            
            # Get all paragraph elements
            p_elements = panel.find_all('p', class_='larger')
            print(f"DEBUG: Panel found {len(p_elements)} p.larger elements", file=sys.stderr)
            
            for p in p_elements:
                # CRITICAL: Use get_text() with separator to preserve <br> as line breaks!
                p_text = p.get_text('\n', strip=True)  
                print(f"DEBUG: p_text with line breaks: '{p_text}'", file=sys.stderr)
                
                # Check if this paragraph contains a phone number
                phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', p_text)
                if phone_match:
                    phone = phone_match.group(0)
                    print(f"DEBUG: Found phone: {phone}", file=sys.stderr)
                    continue
                
                # Check if this paragraph contains an address
                # Address format: "930 N Battlefield Blvd\nChesapeake, VA 23320"
                address_keywords = ['blvd', 'street', 'road', 'ave', 'dr', 'freeway', 'fwy', 'pkwy', 'ste', 'suite', 'way', 'ln', 'lane', 'ct', 'court', 'pl', 'place', 'hwy', 'st', 'rd', 'ave', 'drive', 'main', 'hill', 'kansas']
                if not phone_match and any(keyword in p_text.lower() for keyword in address_keywords):
                    lines = [line.strip() for line in p_text.split('\n') if line.strip()]
                    print(f"DEBUG: Address paragraph has {len(lines)} lines: {lines}", file=sys.stderr)
                    if len(lines) >= 2:
                        # First line is street
                        street = lines[0]
                        
                        # Second line is city, state, zip
                        # Handle both "Houston, TX 77034" and "Houston TX 77034" formats
                        city_line = lines[1]
                        city_match = re.match(r'([^,]+),?\s*([A-Z]{2})\s*(\d{5})', city_line)
                        if city_match:
                            city, state, zip_code = city_match.groups()
                            print(f"DEBUG: Parsed address - street='{street}', city='{city}', state='{state}'", file=sys.stderr)
            
            # If we got basic info, add the dealer
            print(f"DEBUG: Panel processed - name='{name}', street='{street}', city='{city}'", file=sys.stderr)
            if name and street:
                print(f"DEBUG: Adding dealer: {name}", file=sys.stderr)
                dealers.append({
                    "name": name,
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "phone": phone,
                    "website": page_url
                })
            else:
                print(f"DEBUG: Skipping panel - missing name or street", file=sys.stderr)
        
        return dealers

    def _extract_dealeron_locations(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract locations from DealerOn-style 'Our Locations' pages.
        Heuristics based: cards with Directions/Contact links, heading for name, two-line address, phone.
        """
        dealers: List[Dict[str, Any]] = []
        containers = set()
        # Find candidate action links
        for link in soup.find_all("a"):
            text = (link.get_text(strip=True) or "").lower()
            if text in {"directions", "contact", "contact us", "visit site", "visit website"}:
                # Walk up to a reasonable container
                parent = link
                depth = 0
                while parent and depth < 4 and parent.name not in ("section", "article", "li", "div"):
                    parent = parent.parent
                    depth += 1
                if parent and parent.name in ("section", "article", "li", "div"):
                    containers.add(parent)

        phone_pattern = re.compile(r"\(??\d{3}\)??[\-\.\s]?\d{3}[\-\.\s]?\d{4}")
        city_state_zip_pattern = re.compile(r"([^,\n]+),\s*([A-Z]{2})\s*(\d{5})(?:-\d{4})?")

        for container in list(containers):
            # Name: first heading inside or just above
            name_el = container.find(["h1", "h2", "h3", "h4", "h5", "h6"]) or container.find_previous_sibling(["h2", "h3", "h4"]) or container.find_previous(["h2", "h3"]) 
            name = name_el.get_text(strip=True) if name_el else ""

            # Text content lines
            text_block = container.get_text("\n", strip=True)
            lines = [ln.strip() for ln in text_block.split("\n") if ln.strip()]
            # Find city/state/zip line
            street = city = state = zip_code = phone = ""
            for idx, ln in enumerate(lines):
                m = city_state_zip_pattern.search(ln)
                if m:
                    city, state, zip_code = m.groups()
                    # Street is likely the previous non-empty line
                    if idx > 0:
                        street = lines[idx - 1]
                    break
            # Phone
            for ln in lines:
                pm = phone_pattern.search(ln)
                if pm:
                    phone = pm.group(0)
                    break

            if name and (street or (city and state)):
                if not street and idx < len(lines) - 1:
                    # Sometimes street is above heading; best effort
                    street = lines[max(0, idx - 1)]
                s_street, s_city, s_state, s_zip = parse_address(f"{street}, {city}, {state} {zip_code}")
                dealers.append({
                    "name": name,
                    "street": s_street or street,
                    "city": s_city or city,
                    "state": (s_state or state).upper(),
                    "zip": s_zip or zip_code,
                    "phone": phone,
                    "website": page_url,
                })
        return dealers

    def _extract_heading_address_blocks(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealers from sequences of headings followed by address/phone lines (e.g., Bakhtiari, Aschenbach)."""
        dealers: List[Dict[str, Any]] = []
        # Locate the Our Locations section root
        section_root = None
        for tag in soup.find_all(["h1", "h2", "h3"]):
            if (tag.get_text(strip=True) or "").lower() == "our locations":
                section_root = tag
                break
        search_start = section_root.parent if section_root and section_root.parent else (section_root or soup)

        headings = search_start.find_all(["h2", "h3", "h4", "h5"], recursive=True)
        phone_pattern = re.compile(r"\(??\d{3}\)??[\-\.\s]?\d{3}[\-\.\s]?\d{4}")
        city_state_zip_pattern = re.compile(r"([^,\n]+),\s*([A-Z]{2})\s*(\d{5})(?:-\d{4})?")

        for h in headings:
            name = h.get_text(" ", strip=True)
            if not name or len(name) < 3:
                continue
            
            # Filter out navigation/section headings that aren't dealer names
            navigation_terms = [
                "explore our locations", "our locations", "find us", "visit us", "locations",
                "dealerships", "store locations", "branches", "offices", "contact us",
                "where to find us", "find a location", "location finder", "store finder"
            ]
            
            name_lower = name.lower()
            if any(nav_term in name_lower for nav_term in navigation_terms):
                print(f"DEBUG: Rejected navigation heading: {name}", file=sys.stderr)
                continue
            # Collect small following sibling texts up to next heading
            texts: list[str] = []
            nxt = h.next_sibling
            hops = 0
            while nxt and hops < 8:
                if getattr(nxt, "name", None) in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    break
                if hasattr(nxt, "get_text"):
                    t = nxt.get_text("\n", strip=True)
                    if t:
                        texts.append(t)
                nxt = nxt.next_sibling
                hops += 1
            blob = "\n".join(texts)
            if not blob:
                continue
            # Find address and phone
            street = city = state = zip_code = phone = ""
            lines = [ln.strip() for ln in blob.split("\n") if ln.strip()]
            for idx, ln in enumerate(lines):
                m = city_state_zip_pattern.search(ln)
                if m:
                    city, state, zip_code = m.groups()
                    if idx > 0:
                        street = lines[idx - 1]
                    break
            for ln in lines:
                pm = phone_pattern.search(ln)
                if pm:
                    phone = pm.group(0)
                    break
            if city and state:
                s_street, s_city, s_state, s_zip = parse_address(f"{street}, {city}, {state} {zip_code}")
                dealers.append({
                    "name": name,
                    "street": s_street or street,
                    "city": s_city or city,
                    "state": (s_state or state).upper(),
                    "zip": s_zip or zip_code,
                    "phone": phone,
                    "website": page_url,
                })
        return dealers
    
    def _extract_hgreg_dealers(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract HGreg-specific dealers."""
        dealers = []
        for card in soup.select("div.car-details"):
            name_el = card.select_one("h2 a")
            address_el = card.select_one("p.extra-details.address")
            
            name = name_el.get_text(strip=True) if name_el else ""
            address = address_el.get_text(" ", strip=True) if address_el else ""
            website = name_el['href'] if name_el and name_el.has_attr('href') else page_url
            
            street, city, state, zip_code = parse_address(address)
            
            if name:
                dealers.append({
                    "name": name,
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "phone": "",
                    "website": website
                })
        return dealers
    
    def _extract_ken_ganley_dealers(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract Ken Ganley-specific dealers."""
        dealers = []
        for card in soup.select("div.panel.panel-default"):
            name_el = card.select_one("h4.margin-bottom-x > strong")
            address_el = card.select_one("div.panel-body > p")
            
            # Find phone in active tab-pane
            phone = ""
            for p in card.select("div.tab-pane.active p"):
                if "Sales Phone" in p.get_text():
                    phone_text = p.get_text(" ", strip=True)
                    phone_match = re.search(r"Sales Phone:\s*(\d[\d-]+)", phone_text)
                    if phone_match:
                        phone = phone_match.group(1)
                    break
            
            # Find website
            website = page_url
            for a in card.select("div.cta-section a"):
                if "visit" in a.get_text(strip=True).lower():
                    website = a.get('href', page_url)
                    break
            
            name = name_el.get_text(strip=True) if name_el else ""
            address = address_el.get_text(" ", strip=True) if address_el else ""
            
            street, city, state, zip_code = parse_address(address)
            
            if name:
                dealers.append({
                    "name": name,
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "phone": phone,
                    "website": website
                })
        return dealers
    
    def _extract_group1_subpage_dealers(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract Group 1 subpage dealers."""
        dealers = []
        for card in soup.select("div.location.dealer"):
            name_el = card.select_one("h3.af-brand-text")
            p_tags = card.find_all("p")
            
            name = name_el.get_text(strip=True) if name_el else ""
            street = p_tags[0].get_text(strip=True) if len(p_tags) > 0 else ""
            
            city, state, zip_code = "", "", ""
            if len(p_tags) > 1:
                city_match = re.match(r"([\w\s\.-]+),\s*([A-Z]{2})\s*(\d{5})", p_tags[1].get_text(strip=True))
                if city_match:
                    city, state, zip_code = city_match.groups()
            
            phone = p_tags[2].get_text(strip=True) if len(p_tags) > 2 else ""
            
            website = page_url
            for a in card.select("a"):
                if a.get_text(strip=True).lower() == "website" and a.has_attr("href"):
                    website = a["href"]
                    break
            
            if name:
                dealers.append({
                    "name": name,
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "phone": phone,
                    "website": website
                })
        return dealers
    
    def _extract_sierra_auto_dealers(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract Sierra Auto Group dealers."""
        dealers = []
        for card in soup.select("div.dealerInfo"):
            name_el = card.select_one("h2.dealerBrand")
            address1_el = card.select_one("div.dealerAddress1")
            address2_el = card.select_one("div.dealerAddress2")
            phone_el = card.select_one("div.dealerPhone")
            website_el = card.select_one("div.dealerCTA a")
            
            name = name_el.get_text(strip=True) if name_el else ""
            address1 = address1_el.get_text(strip=True) if address1_el else ""
            address2 = address2_el.get_text(strip=True) if address2_el else ""
            phone = phone_el.get_text(strip=True) if phone_el else ""
            website = website_el["href"] if website_el and website_el.has_attr("href") else page_url
            
            full_address = f"{address1}, {address2}" if address1 and address2 else (address1 or address2)
            street, city, state, zip_code = parse_address(full_address)
            
            if name and full_address:
                dealers.append({
                    "name": name,
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "phone": phone,
                    "website": website
                })
        return dealers
    
    def _extract_gregory_auto_dealers(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract Gregory Auto Group dealers."""
        dealers = []
        for card in soup.select("div.fusion-layout-column"):
            name_el = card.select_one("h4.fusion-title-heading")
            text_el = card.select_one("div.fusion-text")
            
            if not name_el:
                continue
                
            name = name_el.get_text(strip=True)
            street, city, state, zip_code, phone = "", "", "", "", ""
            
            if text_el:
                text_content = text_el.get_text("\n", strip=True)
                lines = [line.strip() for line in text_content.split("\n") if line.strip()]
                
                if lines:
                    street = lines[0]
                    
                    for line in lines[1:]:
                        # Check for city, state, zip
                        city_match = re.match(r"^([^,]+),\s*([A-Z]{2})\s+(\d{5})$", line.strip())
                        if city_match:
                            city, state, zip_code = city_match.groups()
                            continue
                        
                        # Check for phone
                        if "call:" in line.lower():
                            phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', line)
                            if phone_match:
                                phone = phone_match.group()
            
            website = page_url
            for button in card.select("a.fusion-button"):
                if "website" in button.get_text(strip=True).lower():
                    website = button.get('href', page_url)
                    break
            
            if name:
                dealers.append({
                    "name": name,
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "phone": phone,
                    "website": website
                })
        return dealers
    
    def _extract_carwash_dealers(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract car wash site dealers."""
        dealers = []
        for card in soup.select("div.card.border-0"):
            item_card = card.select_one("div.item-card9")
            if not item_card:
                continue
                
            name_el = item_card.select_one("h4")
            address_el = item_card.select_one("p")
            website_el = item_card.select_one("a")
            phone_el = card.select_one("div.call-number")
            
            name = name_el.get_text(strip=True) if name_el else ""
            address = address_el.get_text(strip=True) if address_el else ""
            phone = phone_el.get_text(strip=True) if phone_el else ""
            website = website_el["href"] if website_el and website_el.has_attr("href") else page_url
            
            # Make relative URLs absolute
            if website.startswith("/"):
                from urllib.parse import urlparse
                parsed = urlparse(page_url)
                website = f"{parsed.scheme}://{parsed.netloc}{website}"
            
            street, city, state, zip_code = parse_address(address)
            
            if name and address:
                dealers.append({
                    "name": name,
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "phone": phone,
                    "website": website
                })
        return dealers
    
    def _extract_open_road_dealers(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract Open Road dealers."""
        dealers = []
        for card in soup.select("li.location-result"):
            name_el = card.select_one("h2.name")
            address_el = card.select_one("div.address")
            
            name = name_el.get_text(strip=True) if name_el else ""
            address = address_el.get_text(" ", strip=True) if address_el else ""
            
            street, city, state, zip_code = parse_address(address)
            
            if name and address:
                dealers.append({
                    "name": name,
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "phone": "",
                    "website": page_url
                })
        return dealers
    
    def _extract_all_american_dealers(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract All American Auto Group dealers."""
        dealers = []
        for h3 in soup.select("h3.h4"):
            h3_text = h3.get_text(strip=True)
            if not h3_text or "all american" not in h3_text.lower():
                continue
            
            name = h3_text
            street, city, state, zip_code = "", "", "", ""
            website = page_url
            
            # Look for address in following p element
            p_element = h3.find_next_sibling("p")
            if p_element:
                p_html = str(p_element)
                address_lines = re.split(r'<br\s*/?>', p_html)
                address_lines = [re.sub(r'<[^>]+>', '', line).strip() for line in address_lines if line.strip()]
                
                if len(address_lines) >= 2:
                    street = address_lines[0]
                    city_state_zip = address_lines[1]
                    
                    match = re.match(r"^(.+?),\s*([A-Z]{2}),?\s*(\d{5})$", city_state_zip.strip())
                    if match:
                        city, state, zip_code = match.groups()
            
            # Look for website link
            a_element = h3.find_next_sibling("a", class_="btn")
            if not a_element:
                parent = h3.parent
                if parent:
                    a_element = parent.find("a", class_="btn")
            
            if a_element and a_element.has_attr("href"):
                website = a_element["href"]
            
            if name and street:
                dealers.append({
                    "name": name,
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "phone": "",
                    "website": website
                })
        return dealers
    
    def _extract_autobell_dealers(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract AutoBell dealers."""
        dealers = []
        for h2 in soup.find_all("h2"):
            span = h2.find("span")
            if not span or "miles away" not in span.get_text():
                continue
            
            street = h2.get_text(separator=" ", strip=True).split(" miles away")[0]
            address_el = h2.find_next_sibling("address")
            
            city, state, zip_code = "", "", ""
            if address_el:
                address_lines = address_el.decode_contents().split("<br>")
                if len(address_lines) == 2:
                    city_state_zip = BeautifulSoup(address_lines[1], "html.parser").get_text(" ", strip=True)
                    match = re.match(r"(.+),\s*([A-Z]{2})\s*(\d{5})", city_state_zip)
                    if match:
                        city, state, zip_code = match.groups()
            
            if street:
                dealers.append({
                    "name": street,
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "phone": "",
                    "website": page_url
                })
        return dealers
    
    def _extract_bakhtiari_style_dealers(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealers from Bakhtiari-style location pages with location cards."""
        dealers = []
        
        # Look for Bakhtiari-style dealer cards
        dealer_cards = soup.find_all('div', class_=lambda x: x and 'location' in x and 'bg-main' in x)
        print(f"DEBUG: _extract_bakhtiari_style_dealers found {len(dealer_cards)} location cards", file=sys.stderr)
        
        if not dealer_cards:
            return dealers
            
        for card in dealer_cards:
            name = ""
            street = ""
            city = ""
            state = ""
            zip_code = ""
            phone = ""
            website = page_url
            
            # Extract dealer name from span.h1.text-uppercase
            name_el = card.find('span', class_='h1 text-uppercase')
            if name_el:
                name = name_el.get_text(strip=True)
                
            # If no name found, try h6 > span
            if not name:
                name_el = card.find('h6')
                if name_el:
                    name_parts = []
                    span_el = name_el.find('span', class_='h1 text-uppercase')
                    if span_el:
                        name_parts.append(span_el.get_text(strip=True))
                    # Check for brand name after line break
                    br_el = name_el.find('br')
                    if br_el and br_el.next_sibling:
                        next_text = br_el.next_sibling.strip()
                        if next_text:
                            name_parts.append(next_text)
                    name = " ".join(name_parts)
            
            # Extract address from p.larger elements
            p_elements = card.find_all('p', class_='larger')
            print(f"DEBUG: Bakhtiari card found {len(p_elements)} p.larger elements", file=sys.stderr)
            
            for p in p_elements:
                p_text = p.get_text('\n', strip=True)
                print(f"DEBUG: Bakhtiari p_text: '{p_text}'", file=sys.stderr)
                
                # Check if this paragraph contains a phone number
                phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', p_text)
                if phone_match:
                    phone = phone_match.group(0)
                    print(f"DEBUG: Bakhtiari found phone: {phone}", file=sys.stderr)
                    continue
                
                # Check if this paragraph contains an address
                # Address format: "6511 Santa Monica Blvd\nLos Angeles, CA 90038"
                address_keywords = ['blvd', 'street', 'road', 'ave', 'dr', 'freeway', 'fwy', 'pkwy', 'ste', 'suite', 'way', 'ln', 'lane', 'ct', 'court', 'pl', 'place', 'hwy', 'st', 'rd', 'ave', 'drive', 'main', 'hill', 'kansas']
                if not phone_match and any(keyword in p_text.lower() for keyword in address_keywords):
                    lines = [line.strip() for line in p_text.split('\n') if line.strip()]
                    print(f"DEBUG: Bakhtiari address paragraph has {len(lines)} lines: {lines}", file=sys.stderr)
                    
                    if len(lines) >= 2:
                        # First line is street
                        street = lines[0]
                        
                        # Second line is city, state, zip
                        # Handle both "Los Angeles, CA 90038" and "Los Angeles CA 90038" formats
                        city_line = lines[1]
                        city_match = re.match(r'([^,]+),?\s*([A-Z]{2})\s*(\d{5})', city_line)
                        if city_match:
                            city, state, zip_code = city_match.groups()
                            print(f"DEBUG: Bakhtiari parsed address - street='{street}', city='{city}', state='{state}'", file=sys.stderr)
            
            # If we got basic info, add the dealer
            print(f"DEBUG: Bakhtiari processed - name='{name}', street='{street}', city='{city}'", file=sys.stderr)
            if name and street:
                print(f"DEBUG: Adding Bakhtiari dealer: {name}", file=sys.stderr)
                dealers.append({
                    "name": name,
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "phone": phone,
                    "website": page_url
                })
            else:
                print(f"DEBUG: Skipping Bakhtiari card - missing name or street", file=sys.stderr)
        
        return dealers
    
    def _extract_colonial_style_dealers(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealers from Colonial Auto Group style pages."""
        dealers = []
        
        # Find all div elements with class 'get-direction__dealer-name' containing Colonial dealers
        dealer_divs = soup.find_all('div', class_='get-direction__dealer-name')
        colonial_divs = []
        
        for div in dealer_divs:
            if 'colonial' in div.get_text().lower():
                colonial_divs.append(div)
        
        print(f"DEBUG: _extract_colonial_style_dealers found {len(colonial_divs)} dealer divs", file=sys.stderr)
        
        for div in colonial_divs:
            name = div.get_text().strip()
            print(f"DEBUG: Processing Colonial dealer: {name}", file=sys.stderr)
            
            # Look for address and phone information in the next sibling divs
            street = ""
            city = ""
            state = ""
            zip_code = ""
            phone = ""
            
            # The structure is:
            # <div class='get-direction__dealer-name'>Colonial Cadillac</div>
            # <div>201 Cambridge Rd, Woburn, MA 01801</div>
            # <div>(888) 755-1359</div>
            
            current = div.next_sibling
            siblings_checked = 0
            
            while current and siblings_checked < 10:  # Look at next few siblings
                if hasattr(current, 'get_text'):
                    text = current.get_text().strip()
                    print(f"DEBUG: Colonial sibling text: '{text}'", file=sys.stderr)
                    
                    if text:  # Non-empty text
                        # Check for phone number
                        phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
                        if phone_match and not phone:
                            phone = phone_match.group(0)
                            print(f"DEBUG: Found Colonial phone: {phone}", file=sys.stderr)
                        
                        # Check for address pattern (street + city, state zip)
                        elif not street and ',' in text:
                            # Try to parse full address: "201 Cambridge Rd, Woburn, MA 01801"
                            parts = text.split(',')
                            if len(parts) >= 2:
                                potential_street = parts[0].strip()
                                remaining = ','.join(parts[1:]).strip()
                                
                                # Check if remaining part matches city, state zip
                                city_match = re.match(r'^([^,]+?)\s+([A-Z]{2})\s+(\d{5})$', remaining)
                                if city_match:
                                    street = potential_street
                                    city, state, zip_code = city_match.groups()
                                    print(f"DEBUG: Found Colonial address - street='{street}', city='{city}', state='{state}', zip='{zip_code}'", file=sys.stderr)
                    
                    siblings_checked += 1
                
                current = current.next_sibling
            
            # Only add if we have basic required info
            if name and street and city and state:
                dealers.append({
                    "name": name,
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "phone": phone,
                    "website": page_url
                })
                print(f"DEBUG: Added Colonial dealer: {name} at {street}", file=sys.stderr)
            else:
                print(f"DEBUG: Skipping Colonial dealer - missing info: name={bool(name)}, street={bool(street)}, city={bool(city)}, state={bool(state)}", file=sys.stderr)
        
        return dealers