import sys
import json
import re
from io import BytesIO
from urllib.parse import urlparse
import pandas as pd
from bs4 import BeautifulSoup
import streamlit as st

print("app.py sys.executable:", sys.executable, file=sys.stderr)
print("app.py started", file=sys.stderr)  # Debug: confirm script starts

# --------------------------- ADDRESS PARSING HELPER ---------------------------
def parse_address(address_text: str) -> tuple[str, str, str, str]:
    """
    Parses a combined address string into street, city, state/province, and postal code.
    Handles both US (ZIP code) and Canadian (Postal Code) formats.
    """
    street, city, state, postal_code = "", "", "", ""

    # Regex to handle US (12345 or 12345-6789) and Canadian (A1B 2C3) postal codes
    us_zip_pattern = r"\d{5}(?:-\d{4})?"
    canadian_postal_pattern = r"[A-Za-z]\d[A-Za-z]\s?\d[A-Za-z]\d"
    
    # Pattern 1: Street, City, State ZIP, Country (e.g., "222 W Merchandise Mart Plaza, Chicago, IL 60654, USA")
    pattern1 = re.compile(
        r"^(.*?),\s*([^,]+?),\s*([A-Z]{2})\s+(" + us_zip_pattern + "|" + canadian_postal_pattern + r")(?:,\s*[^,]+)?\s*$"
    )
    match = pattern1.match(address_text)
    if match:
        street = match.group(1).strip()
        city = match.group(2).strip()
        state = match.group(3).strip().upper()
        postal_code = match.group(4).strip()
        # Ensure Canadian postal codes have a space
        if re.match(canadian_postal_pattern, postal_code) and ' ' not in postal_code:
            postal_code = postal_code[:3] + ' ' + postal_code[3:]
        return street, city, state, postal_code
    
    # Pattern 2: Original pattern without country
    pattern2 = re.compile(
        r"^(.*?),\s*([^,]+?),\s*([A-Za-z]{2})\s+(" + us_zip_pattern + "|" + canadian_postal_pattern + r")\s*$"
    )
    match = pattern2.match(address_text)
    if match:
        street = match.group(1).strip()
        city = match.group(2).strip()
        state = match.group(3).strip().upper()
        postal_code = match.group(4).strip()
        # Ensure Canadian postal codes have a space
        if re.match(canadian_postal_pattern, postal_code) and ' ' not in postal_code:
            postal_code = postal_code[:3] + ' ' + postal_code[3:]
        return street, city, state, postal_code
    
    # Fallback for less structured addresses
    parts = [part.strip() for part in address_text.split(',') if part.strip()]
    if len(parts) >= 3:
        street = parts[0]
        city = parts[1]
        # Handle the last part which might be "IL 60654" or "IL 60654 USA"
        last_parts = parts[-1].strip().split()
        if len(parts) >= 4 and len(last_parts) == 1:
            # Format: Street, City, State, ZIP, Country
            state = parts[2].strip().upper()
            postal_code = parts[3].strip()
        else:
            # Format: Street, City, "IL 60654" or "IL 60654 USA"
            if len(last_parts) >= 2:
                state = last_parts[0].strip().upper()
                postal_code = last_parts[1].strip()
            else:
                # Try regex extraction from the last part
                last_part = parts[-1]
                m_can = re.search(r"([A-Z]{2})\s+(" + canadian_postal_pattern + r")", last_part)
                m_us = re.search(r"([A-Z]{2})\s+(" + us_zip_pattern + r")", last_part)
                if m_can:
                    state = m_can.group(1)
                    postal_code = m_can.group(2)
                elif m_us:
                    state = m_us.group(1)
                    postal_code = m_us.group(2)
    
    return street, city, state, postal_code

# --------------------------- DATA EXTRACTION ---------------------------

def extract_dealer_data(html: str, page_url: str) -> list[dict]:
    """Extract dealership records using JSON-LD, JS arrays, HTML selectors, and Lithia-specific parsing."""
    soup = BeautifulSoup(html, "html.parser")
    dealers = []

    # Strategy 1: JSON-LD
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "")
        except Exception:
            continue
        if isinstance(data, dict) and "@graph" in data:
            items = data["@graph"]
        elif isinstance(data, list):
            items = data
        else:
            items = [data]
        for item in items:
            if item.get("@type") in ("AutoDealer", "AutomotiveBusiness", "LocalBusiness"):
                address = item.get("address", {})
                dealers.append({
                    "name": item.get("name", ""),
                    "street": address.get("streetAddress", ""),
                    "city": address.get("addressLocality", ""),
                    "state": address.get("addressRegion", ""),
                    "zip": address.get("postalCode", ""),
                    "phone": item.get("telephone", ""),
                    "website": item.get("url", page_url)
                })

    # Strategy 2: JS variable arrays
    patterns = [
        r"(?:var|let|const)\s+(?:locations|dealers|stores)\s*=\s*(\[.*?\]);",
        r"window\.dealerData\s*=\s*(\[.*?\]);",
        r"locationData:\s*(\[.*?\])",
    ]
    for script in soup.find_all("script"):
        text = script.string or ""
        for pat in patterns:
            m = re.search(pat, text, re.DOTALL)
            if not m:
                continue
            try:
                arr = json.loads(m.group(1))
            except Exception:
                continue
            for obj in (arr if isinstance(arr, list) else []):
                if isinstance(obj, dict):
                    dealers.append({
                        "name": obj.get("name") or obj.get("title", ""),
                        "street": obj.get("address") or obj.get("street", ""),
                        "city": obj.get("city", ""),
                        "state": obj.get("state") or obj.get("province", ""),
                        "zip": obj.get("zip") or obj.get("postalCode", ""),
                        "phone": obj.get("phone") or obj.get("telephone", ""),
                        "website": obj.get("url") or obj.get("website", page_url)
                    })

    # Strategy 3: Lithia-specific HTML parsing
    for li in soup.select("li.info-window"):
        name_el = li.select_one(".org")
        website_el = li.select_one("a.url")
        street_el = li.select_one(".street-address")
        city_el = li.select_one(".locality")
        state_el = li.select_one(".region")
        zip_el = li.select_one(".postal-code")
        phone_el = li.select_one(".tel[data-click-to-call='Sales']")
        phone_val = li.select_one(".tel[data-click-to-call='Sales'] .value")
        phone = ""
        if phone_el and phone_el.has_attr("data-click-to-call-phone"):
            phone = phone_el["data-click-to-call-phone"]
        elif phone_val:
            phone = phone_val.get_text(strip=True)
        dealers.append({
            "name": name_el.get_text(strip=True) if name_el else "",
            "street": street_el.get_text(strip=True) if street_el else "",
            "city": city_el.get_text(strip=True) if city_el else "",
            "state": state_el.get_text(strip=True) if state_el else "",
            "zip": zip_el.get_text(strip=True) if zip_el else "",
            "phone": phone,
            "website": website_el["href"] if website_el and website_el.has_attr("href") else page_url
        })

    # Strategy 4: Group 1 Automotive-specific HTML parsing
    for card in soup.select("div.dealer-card, div.location-card, div.g1-location-card"):
        name_el = card.select_one(".dealer-title, .dealer-name, h2, h3, h4")
        address_el = card.select_one(".dealer-address, .address, address, .dealer-info__address")
        phone_el = card.select_one(".dealer-phone, .phone, a[href^='tel:'], .dealer-info__phone")
        website_el = card.select_one("a[href^='http']:not([href*='group1auto.com'])")
        # Fallback: sometimes the website is a button
        if not website_el:
            website_el = card.select_one("a.btn, a.button, a[role='button']")
        name = name_el.get_text(strip=True) if name_el else ""
        address = address_el.get_text(separator=", ", strip=True) if address_el else ""
        phone = phone_el.get_text(strip=True) if phone_el else ""
        website = website_el['href'] if website_el and website_el.has_attr('href') else page_url
        # Try to split address into components
        street, city, state, zipc = "", "", "", ""
        m = re.match(r"(.+),\s*([\w\s\.-]+),\s*([A-Z]{2})\s*(\d{5})", address)
        if m:
            street = m.group(1).strip()
            city = m.group(2).strip()
            state = m.group(3)
            zipc = m.group(4)
        else:
            parts = address.split(",")
            if len(parts) >= 3:
                street = parts[0].strip()
                city = parts[1].strip()
                state_zip = parts[2].strip().split()
                if len(state_zip) == 2:
                    state, zipc = state_zip
        if name or street:
            dealers.append({
                "name": name,
                "street": street,
                "city": city,
                "state": state,
                "zip": zipc,
                "phone": phone,
                "website": website
            })

    canadian_provinces = {"AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE", "QC", "SK", "YT"}
    # Strategy: Pritchard Family Auto Stores-specific HTML parsing - div.well.matchable-heights (with conflict detection)
    well_cards = soup.select("div.well.matchable-heights")
    if well_cards:
        # Check if this looks like AutoCanada/Ken Garff pattern vs Pritchard pattern
        sample_card = well_cards[0]
        has_dealer_address = sample_card.select_one("span.di-dealer-address")
        has_dealer_phone = sample_card.select_one("span.dealer-phone")
        
        # If it has AutoCanada/Ken Garff specific elements, skip Pritchard parsing
        if not (has_dealer_address and has_dealer_phone):
            # This looks like Pritchard pattern
            for card in well_cards:
                name_el = card.select_one("h2")
                address_parts = []
                phone = ""
                website = page_url
                
                # Extract all text content and parse structure
                for p in card.find_all("p"):
                    text = p.get_text(strip=True)
                    if not text:
                        continue
                        
                    # Check if this is a phone number
                    if re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text):
                        phone = text
                    else:
                        # Assume it's part of the address
                        address_parts.append(text)
                
                # Look for website link
                website_el = card.select_one("a[href^='http']")
                if website_el:
                    website = website_el["href"]
                
                name = name_el.get_text(strip=True) if name_el else ""
                full_address = ", ".join(address_parts)
                
                # Parse the combined address
                street, city, state, zipc = parse_address(full_address)
                
                if name and full_address:
                    dealers.append({
                        "name": name,
                        "street": street,
                        "city": city,
                        "state": state,
                        "zip": zipc,
                        "phone": phone,
                        "website": website
                    })
            
            # Skip the original AutoCanada parsing since we handled these cards
        else:
            # This looks like AutoCanada/Ken Garff, proceed with original parsing
            pass

    # Strategy: AutoCanada-specific HTML parsing
    for card in soup.select("div.well.matchable-heights"):
        name_el = card.select_one("h2")
        website_el = None
        if name_el:
            parent_a = name_el.find_parent("a")
            if parent_a and parent_a.has_attr("href"):
                website_el = parent_a
        address_el = card.select_one("span.di-dealer-address")
        phone_el = card.select_one("span.dealer-phone.sales span")
        name = name_el.get_text(strip=True) if name_el else ""
        website = website_el["href"] if website_el else page_url
        phone = phone_el.get_text(strip=True) if phone_el else ""
        address_html = address_el.decode_contents() if address_el else ""
        # Split on <br> or newlines
        parts = re.split(r'<br\s*/?>|\n', address_html)
        parts = [BeautifulSoup(p, 'html.parser').get_text(" ", strip=True) for p in parts if p.strip()]
        address_text = ", ".join(parts)
        street, city, state, zipc = parse_address(address_text)
        # Set country based on province if missing
        if not state:
            if city in canadian_provinces:
                state = "Canada"
            else:
                state = "United States of America"
        if name or street:
            dealers.append({
                "name": name,
                "street": street,
                "city": city,
                "state": state,
                "zip": zipc,
                "phone": phone,
                "website": website
            })

    # Strategy: HGreg-specific HTML parsing
    hgreg_cards = soup.select("div.car-details")
    print(f"DEBUG: Found {len(hgreg_cards)} div.car-details elements", file=sys.stderr)
    for card in hgreg_cards:
        name_el = card.select_one("h2 a")
        address_el = card.select_one("p.extra-details.address")
        name = name_el.get_text(strip=True) if name_el else ""
        address = address_el.get_text(" ", strip=True) if address_el else ""
        print(f"DEBUG: HGreg card name: {name}, address: {address}", file=sys.stderr)
        # Parse address: "8505 Northwest 12th Street Doral, FL, United States 33126"
        street, city, state, zipc = "", "", "", ""
        m = re.match(r"(.+?)\\s+([\\w\\s]+),\\s*([A-Z]{2}),.*?(\\d{5})", address)
        if m:
            street = m.group(1).strip()
            city = m.group(2).strip()
            state = m.group(3)
            zipc = m.group(4)
        else:
            parts = address.split(",")
            if len(parts) >= 3:
                street = parts[0].strip()
                city = parts[1].strip()
                state_zip = parts[2].strip().split()
                if len(state_zip) == 2:
                    state, zipc = state_zip
        website = name_el['href'] if name_el and name_el.has_attr('href') else page_url
        dealers.append({
            "name": name,
            "street": street,
            "city": city,
            "state": state,
            "zip": zipc,
            "phone": "",
            "website": website
        })

    # Strategy: Ken Ganley-specific HTML parsing
    for card in soup.select("div.panel.panel-default"):
        name_el = card.select_one("h4.margin-bottom-x > strong")
        address_el = card.select_one("div.panel-body > p")
        # Find the p tag with 'Sales Phone' in the active tab-pane
        phone_el = None
        for p in card.select("div.tab-pane.active p"):
            if "Sales Phone" in p.get_text():
                phone_el = p
                break
        website_el = None
        for a in card.select("div.cta-section a"):
            if "visit" in a.get_text(strip=True).lower():
                website_el = a
                break
        name = name_el.get_text(strip=True) if name_el else ""
        address = address_el.get_text(" ", strip=True) if address_el else ""
        # Parse address: "28300 Lorain Rd, North Olmsted, OH 44070"
        street, city, state, zipc = "", "", "", ""
        m = re.match(r"(.+?),\s*([\w\s]+),\s*([A-Z]{2})\s*(\d{5})", address)
        if m:
            street = m.group(1).strip()
            city = m.group(2).strip()
            state = m.group(3)
            zipc = m.group(4)
        else:
            parts = address.split(",")
            if len(parts) >= 3:
                street = parts[0].strip()
                city = parts[1].strip()
                state_zip = parts[2].strip().split()
                if len(state_zip) == 2:
                    state, zipc = state_zip
        phone = ""
        if phone_el:
            phone_text = phone_el.get_text(" ", strip=True)
            m = re.search(r"Sales Phone:\s*(\d[\d-]+)", phone_text)
            if m:
                phone = m.group(1)
        website = website_el["href"] if website_el and website_el.has_attr("href") else page_url
        dealers.append({
            "name": name,
            "street": street,
            "city": city,
            "state": state,
            "zip": zipc,
            "phone": phone,
            "website": website
        })

    # Strategy: Group 1 subpage-specific HTML parsing
    for card in soup.select("div.location.dealer"):
        name_el = card.select_one("h3.af-brand-text")
        p_tags = card.find_all("p")
        street = p_tags[0].get_text(strip=True) if len(p_tags) > 0 else ""
        city, state, zipc = "", "", ""
        if len(p_tags) > 1:
            m = re.match(r"([\w\s\.-]+),\s*([A-Z]{2})\s*(\d{5})", p_tags[1].get_text(strip=True))
            if m:
                city = m.group(1).strip()
                state = m.group(2)
                zipc = m.group(3)
        phone = p_tags[2].get_text(strip=True) if len(p_tags) > 2 else ""
        website = ""
        for a in card.select("a"):
            if a.get_text(strip=True).lower() == "website" and a.has_attr("href"):
                website = a["href"]
                break
        dealers.append({
            "name": name_el.get_text(strip=True) if name_el else "",
            "street": street,
            "city": city,
            "state": state,
            "zip": zipc,
            "phone": phone,
            "website": website or page_url
        })

    # Strategy: Ken Garff-specific HTML parsing
    for card in soup.select("div.well.matchable-heights"):
        name_el = card.select_one("a > h2")
        website_el = card.select_one("a.button.primary-button.block")
        address_el = card.select_one("span.di-dealer-address")
        sales_phone_el = card.select_one("span.dealer-phone.sales span")
        name = name_el.get_text(strip=True) if name_el else ""
        website = website_el["href"] if website_el and website_el.has_attr("href") else page_url
        address = address_el.get_text(" ", strip=True) if address_el else ""
        # Parse address: "3455 North Digital Drive Lehi, UT 84043"
        street, city, state, zipc = "", "", "", ""
        m = re.match(r"(.+?) ([\w\s]+),\s*([A-Z]{2})\s*(\d{5})", address)
        if m:
            street = m.group(1).strip()
            city = m.group(2).strip()
            state = m.group(3)
            zipc = m.group(4)
        else:
            parts = address.split(",")
            if len(parts) >= 2:
                street = parts[0].strip()
                city_state_zip = parts[1].strip().split()
                if len(city_state_zip) >= 3:
                    city = " ".join(city_state_zip[:-2])
                    state = city_state_zip[-2]
                    zipc = city_state_zip[-1]
        phone = sales_phone_el.get_text(strip=True) if sales_phone_el else ""
        dealers.append({
            "name": name,
            "street": street,
            "city": city,
            "state": state,
            "zip": zipc,
            "phone": phone,
            "website": website
        })

    # Strategy: AutoBell fallback - parse h2/address pairs
    for h2 in soup.find_all("h2"):
        # Check if this h2 looks like a location (has a span with 'miles away')
        span = h2.find("span")
        if not span or "miles away" not in span.get_text():
            continue
        street = h2.get_text(separator=" ", strip=True).split(" miles away")[0]
        # Find the next <address> sibling
        address_el = h2.find_next_sibling("address")
        city, state, zipc = "", "", ""
        if address_el:
            address_lines = address_el.decode_contents().split("<br>")
            if len(address_lines) == 2:
                # First line is street (redundant), second is city/state/zip
                city_state_zip = BeautifulSoup(address_lines[1], "html.parser").get_text(" ", strip=True)
                m = re.match(r"(.+),\s*([A-Z]{2})\s*(\d{5})", city_state_zip)
                if m:
                    city = m.group(1)
                    state = m.group(2)
                    zipc = m.group(3)
        dealers.append({
            "name": street,
            "street": street,
            "city": city,
            "state": state,
            "zip": zipc,
            "phone": "",
            "website": page_url
        })

    # Strategy: Car wash sites (cleancarwashla.org style) - div.item-card9
    for card in soup.select("div.card.border-0"):
        # Look for the item-card9 within this card
        item_card = card.select_one("div.item-card9")
        if not item_card:
            continue
            
        name_el = item_card.select_one("h4")
        address_el = item_card.select_one("p")
        website_el = item_card.select_one("a")
        # Look for phone in the card-footer section
        phone_el = card.select_one("div.call-number")
        
        name = name_el.get_text(strip=True) if name_el else ""
        address = ""
        if address_el:
            # Extract just the address text, skip the icon
            address = address_el.get_text(strip=True)
            # Remove any leading location icon text
            if address.startswith("222 W"):  # Clean up if there's icon text
                address = address
        
        phone = phone_el.get_text(strip=True) if phone_el else ""
        
        website = website_el["href"] if website_el and website_el.has_attr("href") else page_url
        if website.startswith("/"):
            # Convert relative URL to absolute
            base = page_url.split("/")[0] + "//" + page_url.split("/")[2]
            website = base + website
            
        # Parse the address
        street, city, state, zipc = parse_address(address)
        
        if name and address:
            dealers.append({
                "name": name,
                "street": street,
                "city": city,
                "state": state,
                "zip": zipc,
                "phone": phone,
                "website": website
            })

    # Strategy: Open Road-specific HTML parsing - li.location-result
    for card in soup.select("li.location-result"):
        name_el = card.select_one("h2.name")
        address_el = card.select_one("div.address")
        
        name = name_el.get_text(strip=True) if name_el else ""
        address = address_el.get_text(" ", strip=True) if address_el else ""
        
        # Parse address: "108 Ridgedale Avenue<br>Morristown, NJ, United States"
        street, city, state, zipc = parse_address(address)
        
        if name and address:
            dealers.append({
                "name": name,
                "street": street,
                "city": city,
                "state": state,
                "zip": zipc,
                "phone": "",
                "website": page_url
            })

    # Strategy: Sierra Auto Group-specific HTML parsing - div.dealerInfo
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
        
        # Combine address parts
        full_address = f"{address1}, {address2}" if address1 and address2 else (address1 or address2)
        street, city, state, zipc = parse_address(full_address)
        
        if name and full_address:
            dealers.append({
                "name": name,
                "street": street,
                "city": city,
                "state": state,
                "zip": zipc,
                "phone": phone,
                "website": website
            })

    # Strategy: Gregory Auto Group-specific HTML parsing - Fusion builder columns
    for card in soup.select("div.fusion-layout-column"):
        name_el = card.select_one("h4.fusion-title-heading")
        text_el = card.select_one("div.fusion-text")
        website_el = None
        
        # Look for "Visit website" button or any fusion button
        for button in card.select("a.fusion-button"):
            if "website" in button.get_text(strip=True).lower():
                website_el = button
                break
        
        if not name_el:
            continue
            
        name = name_el.get_text(strip=True)
        
        # Initialize defaults
        street, city, state, zipc, phone = "", "", "", "", ""
        
        if text_el:
            text_content = text_el.get_text("\n", strip=True)
            
            # Parse text content which contains address and phone
            # Format: "Address\nCity, State Zip\nCall: (phone)"
            lines = [line.strip() for line in text_content.split("\n") if line.strip()]
            
            if len(lines) >= 1:
                # First line is usually the street address
                street = lines[0]
                
                # Look for city, state, zip in subsequent lines
                for line in lines[1:]:
                    # Check if this line looks like "City, State Zip"
                    city_state_match = re.match(r"^([^,]+),\s*([A-Z]{2})\s+(\d{5})$", line.strip())
                    if city_state_match:
                        city = city_state_match.group(1).strip()
                        state = city_state_match.group(2).strip()
                        zipc = city_state_match.group(3).strip()
                        continue
                        
                    # Check for phone number
                    if "call:" in line.lower():
                        phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', line)
                        if phone_match:
                            phone = phone_match.group()
                
                # If we didn't find structured address, try full address parsing
                if not city and len(lines) >= 2:
                    full_address = f"{street}, {lines[1]}"
                    street_parsed, city_parsed, state_parsed, zip_parsed = parse_address(full_address)
                    if city_parsed:  # Only use if parsing was successful
                        street, city, state, zipc = street_parsed, city_parsed, state_parsed, zip_parsed
        
        website = website_el["href"] if website_el and website_el.has_attr("href") else page_url
        
        # Only require name to be present (address might be optional for some listings)
        if name:
            dealers.append({
                "name": name,
                "street": street,
                "city": city,
                "state": state,
                "zip": zipc,
                "phone": phone,
                "website": website
            })

    # Strategy: Wash U Car Wash-specific HTML parsing 
    print(f"DEBUG: Looking for Wash U Car Wash patterns...", file=sys.stderr)
    wash_u_cards = soup.select("div[class*='pol-']")
    print(f"DEBUG: Found {len(wash_u_cards)} div[class*='pol-'] elements", file=sys.stderr)
    
    for card in wash_u_cards:
        name_el = card.select_one("p.sl-addr-list-title")
        address_el = card.select_one("li.sl-addr span")
        phone_el = card.select_one("li.sl-phone a")
        
        if not name_el:
            continue
            
        name = f"Wash U Car Wash - {name_el.get_text(strip=True)}"
        address = address_el.get_text(" ", strip=True) if address_el else ""
        phone = phone_el.get_text(strip=True) if phone_el else ""
        
        print(f"DEBUG: Wash U extracted - name: '{name}', address: '{address}', phone: '{phone}'", file=sys.stderr)
        
        # Parse address which may have <br> tags
        address = re.sub(r'<br\s*/?>', ' ', address)
        street, city, state, zipc = parse_address(address)
        
        if name and address:
            dealers.append({
                "name": name,
                "street": street,
                "city": city,
                "state": state,
                "zip": zipc,
                "phone": phone,
                "website": page_url
            })

    # Filter out non-dealerships
    def is_valid_dealership(d):
        bad_names = {"locations", "saved", "community news", "essential cookies", "sales", "service phone:", "parts phone:"}
        name = (d.get("name") or "").strip().lower()
        street = (d.get("street") or "").strip()
        website = (d.get("website") or "").strip()
        if not name or not street:
            return False
        if name in bad_names:
            return False
        if website.startswith("#") or website.startswith("/"):
            return False
        return True

    filtered = [d for d in dealers if is_valid_dealership(d)]
    print(f"Valid dealerships after filtering: {len(filtered)}", file=sys.stderr)

    # De-duplicate (improved: normalize name and street, case-insensitive, strip spaces)
    def norm(s):
        return re.sub(r'\s+', ' ', s or '').strip().lower()
    unique, seen = [], set()
    for d in filtered:
        name_norm = norm(d['name'])
        street_norm = norm(d['street'])
        if name_norm and street_norm:
            key = (name_norm, street_norm)
            if key not in seen:
                unique.append(d)
                seen.add(key)
        else:
            unique.append(d)  # keep entries missing name or street
    return unique

def extract_directory_links(html: str, base_url: str) -> list:
    """Extracts subpage links from a directory page (e.g., state/make/region links) using pattern matching."""
    soup = BeautifulSoup(html, "html.parser")
    links = []
    # Look for anchor tags in common directory containers
    containers = soup.select("div.af-location-container, .locations-directory, .state-list, .make-list, .location-list, .dealer-directory, .directory-list")
    if not containers:
        containers = [soup]  # fallback: search whole page
    # Directory patterns to match
    patterns = [
        "/locations/", "/dealers/", "/store-locations", "state=", "/by-", "/find-", "/inventory/", "/location/", "/our-locations", "/search/"
    ]
    for container in containers:
        for a in container.find_all("a", href=True):
            href = a["href"]
            if href.startswith("#") or href.startswith("javascript"): continue
            # Only add links that look like subpages (not external or mailto)
            if any(pat in href for pat in patterns):
                if href.startswith("http"):
                    links.append(href)
                elif href.startswith("/"):
                    base = base_url.split("/")[0] + "//" + base_url.split("/")[2]
                    links.append(base + href)
                else:
                    # relative path
                    links.append(base_url.rstrip("/") + "/" + href)
    # Remove duplicates
    links = list(dict.fromkeys(links))
    # Only return if a reasonable number of links are found
    if 3 <= len(links) <= 100:
        return links
    return []

def is_dealer_inspire(html: str) -> bool:
    return (
        "dealerinspire.com" in html or
        "Dealer Inspire" in html or
        "dealerinspire" in html
    )

# --------------------------- CLI SCRAPER ---------------------------

def _scrape_rows(dealer_name: str, url: str) -> list[dict]:
    print("Starting Playwright scrape for:", url, file=sys.stderr)
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    import time
    all_html = []
    with sync_playwright() as p:
        # Default: headless browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width":1920, "height":1080})
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        # Wait for AutoBell locations list to load (if present)
        try:
            page.wait_for_selector('.css-16af3dh li', timeout=20000)
            print("DEBUG: Waited for .css-16af3dh li selector (AutoBell locations)", file=sys.stderr)
        except Exception:
            print("DEBUG: .css-16af3dh li selector not found after waiting", file=sys.stderr)
        html = page.content()
        # Dealer Inspire detection and stealth logic
        if is_dealer_inspire(html):
            print("DEBUG: Dealer Inspire detected, relaunching with stealth settings", file=sys.stderr)
            browser.close()
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            html = page.content()
        # Special handling for Ken Garff contact-us page
        if "kengarff.com/contact-us" in url:
            try:
                page.wait_for_selector("div.well.matchable-heights", timeout=10000)
            except Exception:
                print("DEBUG: No div.well.matchable-heights found after initial load", file=sys.stderr)
            for _ in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(500)
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select("div.well.matchable-heights")
            print(f"DEBUG: After scrolling, found {len(cards)} div.well.matchable-heights elements", file=sys.stderr)
        else:
            html = page.content()
        # Check if this page already contains dealership cards
        soup = BeautifulSoup(html, "html.parser")
        has_dealer_cards = bool(
            soup.select("li.info-window, div.dealer-card, div.location-card, div.g1-location-card, div.well.matchable-heights, div.car-details, div.panel.panel-default")
        )
        if has_dealer_cards:
            # Extract and return immediately, no extra scrolling/waiting
            browser.close()
            print("Dealer cards detected on initial load, extracting immediately", file=sys.stderr)
            return extract_dealer_data(html, url)
        else:
            # Check if this is a directory page (many subpage links matching Group 1 pattern)
            subpage_links = [
                link for link in extract_directory_links(html, url)
                if "/dealers.html?state=" in link or "/dealers?state=" in link
            ]
            if len(subpage_links) > 0:
                print(f"Detected directory page with {len(subpage_links)} subpages", file=sys.stderr)
                for idx, sub_url in enumerate(subpage_links):
                    try:
                        print(f"Scraping subpage {idx+1}/{len(subpage_links)}: {sub_url}", file=sys.stderr)
                        page.goto(sub_url, wait_until="domcontentloaded", timeout=15000)
                        # Wait for dealer cards to load (if any)
                        try:
                            page.wait_for_selector("div.dealer-card, div.location-card, div.g1-location-card", timeout=10000)
                        except Exception:
                            print(f"DEBUG: Selector not found on subpage {sub_url}", file=sys.stderr)
                            pass
                        # Scroll to load all cards if needed
                        for _ in range(2):
                            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            page.wait_for_timeout(500)
                        sub_html = page.content()
                        print(f"DEBUG: Finished scraping subpage {idx+1}/{len(subpage_links)}", file=sys.stderr)
                        all_html.append(sub_html)
                    except Exception as e:
                        print(f"Failed to scrape subpage: {sub_url} ({e})", file=sys.stderr)
                browser.close()
                # Aggregate all dealership data
                all_dealers = []
                for html in all_html:
                    all_dealers.extend(extract_dealer_data(html, url))
                print(f"DEBUG: Total dealers extracted from subpages: {len(all_dealers)}", file=sys.stderr)
                return all_dealers
        # Not a directory page, or already contains dealer cards (should not reach here, but fallback)
        try:
            page.wait_for_selector("div.panel-body.pad-1x.pad-bottom-x", timeout=30000)
        except PlaywrightTimeoutError:
            pass
        for _ in range(10):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)
        html = page.content()
        browser.close()
    print("Finished Playwright scrape", file=sys.stderr)
    with open("debug_lithia.html", "w", encoding="utf-8") as f:
        f.write(html)
    return extract_dealer_data(html, url)

if __name__ == "__main__" and len(sys.argv) > 1:
    if len(sys.argv) != 3:
        print("Usage: python app.py \"Dealer Name\" \"Locations URL\"", file=sys.stderr)
        sys.exit(1)
    name_arg, url_arg = sys.argv[1], sys.argv[2]
    try:
        rows = _scrape_rows(name_arg, url_arg)
        print(json.dumps(rows), flush=True)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    sys.exit(0)

# --------------------------- STREAMLIT UI ---------------------------

if "scrape_cache" not in st.session_state:
    st.session_state.scrape_cache = {}

car_brands = [
    "Acura", "Airstream", "Alfa Romeo", "Aston Martin", "Audi", "Bentley", "BMW", "Bugatti", "Cadillac", "Chevrolet",
    "Ferrari", "FIAT", "Ford", "Genesis", "GMC", "Honda", "Hummer", "Hyundai", "Infiniti", "Isuzu", "Jaguar", "Kia",
    "Lamborghini", "Land Rover", "Lexus", "Lincoln", "Maserati", "Mazda", "McLaren", "Mercedes-Benz", "Mini",
    "Mitsubishi", "Nissan", "Polestar", "Porsche", "Rolls-Royce", "smart", "Sprinter", "Subaru", "Tesla", "Toyota",
    "Volkswagen", "Volvo", "Lotus", "INEOS", "Koenigsegg", "Harley-Davidson", "Rimac", "Karma", "Lucid", "Vinfast",
    "CDJR", "CDJRF", "Buick GMC", "Rivian", "Ford PRO", "GMC/Chevy Business Elite", "RAM Commercial", "Freightliner",
    "Western Star", "International", "Peterbilt", "Kenworth", "Mack", "Hino", "Capacity", "Autocar", "Fuso", "Maybach",
    "Pagani", "Chrysler", "Dodge", "Scion", "Jeep"
]

def classify_dealer_type(name, brand_list):
    name_lower = name.lower() if isinstance(name, str) else ''
    # Collision
    if any(word in name_lower for word in [
        'collision', 'body shop', 'autobody', 'auto body', 'repair center', 'collision repair', 'body repair', 'repair']):
        return 'Collision'
    # Fixed Ops / Service
    if any(word in name_lower for word in ['service', 'quick lane', 'express', 'maintenance', 'tire', 'lube']):
        return 'Fixed Ops'
    # Used Car Center
    if any(word in name_lower for word in ['used', 'pre-owned', 'auto sales', 'car sales']):
        return 'Used'
    # Franchised
    if any(brand.lower() in name_lower for brand in brand_list):
        return 'Franchised'
    # Fallback
    return 'Unknown'

def scrape_with_external(dealer_name: str, url: str) -> pd.DataFrame:
    key = f"{dealer_name}_{url}"
    if key in st.session_state.scrape_cache:
        return st.session_state.scrape_cache[key]
    import subprocess
    import sys
    import time
    print("Streamlit sys.executable:", sys.executable, file=sys.stderr)
    # Start the subprocess
    cmd = [sys.executable, sys.argv[0], dealer_name, url]
    with st.spinner("Scraping dealerships..."):
        status_box = st.empty()
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Use communicate to avoid deadlocks
        stdout, stderr = proc.communicate()
        output_lines = stderr.splitlines()
        # Show the last 5 lines as status
        if output_lines:
            status_box.info("\n".join(output_lines[-5:]))
        if proc.returncode != 0:
            st.error("Scraping failed. See details below.")
            st.text("\n".join(output_lines))
            raise RuntimeError("Scraping failed.")
        print("DEBUG: Extraction complete, loading JSON", file=sys.stderr)
        try:
            rows = json.loads(stdout or "[]")
            print(f"DEBUG: Loaded {len(rows)} rows", file=sys.stderr)
            df = pd.DataFrame(rows)
            print("DEBUG: DataFrame created", file=sys.stderr)
            df["Dealer Group"] = dealer_name
            # Remove any hardcoded assignment to 'Franchised' for Dealership Type
            # Assign Dealership Type using the classification function
            if "Dealership" in df.columns:
                df["Dealership Type"] = df["Dealership"].apply(lambda x: classify_dealer_type(x, car_brands))
            else:
                df["Dealership Type"] = df["name"].apply(lambda x: classify_dealer_type(x, car_brands))
            # Set Country based on state/province
            canadian_provinces = {"AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE", "QC", "SK", "YT"}
            if "State/Province" in df.columns:
                df["Country"] = df["State/Province"].apply(lambda x: "Canada" if str(x).strip() in canadian_provinces else "United States of America")
            else:
                df["Country"] = "United States of America"
            def extract_brand(name):
                name_lower = name.lower() if isinstance(name, str) else ''
                # Check for CDJRF (Chrysler, Jeep, Dodge, Ram, FIAT)
                if all(word in name_lower for word in ['chrysler', 'jeep', 'dodge', 'ram', 'fiat']):
                    return 'CDJRF'
                # Check for CDJR (Chrysler, Jeep, Dodge, Ram)
                if all(word in name_lower for word in ['chrysler', 'jeep', 'dodge', 'ram']):
                    return 'CDJR'
                found_brands = [brand for brand in car_brands if brand.lower() in name_lower]
                if found_brands:
                    return "; ".join(found_brands)
                return ""
            if "name" in df.columns:
                df["Car Brand"] = df["name"].apply(extract_brand)
            else:
                df["Car Brand"] = ""
            rename_map = {"name":"Dealership","street":"Address","city":"City","state":"State/Province","zip":"Postal Code","phone":"Phone","website":"Website"}
            df.rename(columns=rename_map, inplace=True, errors="ignore")
            print("DEBUG: DataFrame columns renamed", file=sys.stderr)
            # Standardize address abbreviations
            if "Address" in df.columns:
                df["Address"] = df["Address"].str.replace(r"\bStreet\b", "St", regex=True)
                df["Address"] = df["Address"].str.replace(r"\bAvenue\b", "Ave", regex=True)
                df["Address"] = df["Address"].str.replace(r"\bBoulevard\b", "Blvd", regex=True)
                df["Address"] = df["Address"].str.replace(r"\bHighway\b", "Hwy", regex=True)
                df["Address"] = df["Address"].str.replace(r"\bLane\b", "Ln", regex=True)
                df["Address"] = df["Address"].str.replace(r"\bDrive\b", "Dr", regex=True)
                df["Address"] = df["Address"].str.replace(r"\bRoad\b", "Rd", regex=True)
                df["Address"] = df["Address"].str.replace(r"\bParkway\b", "Pkwy", regex=True)
                df["Address"] = df["Address"].str.replace(r"\bExpressway\b", "Expy", regex=True)
                # Convert to title case, then restore common abbreviations
                df["Address"] = df["Address"].str.title()
                # Restore abbreviations to uppercase (even if followed by punctuation or end of string)
                for abbr in ["NE", "NW", "SE", "SW", "GMC", "FIAT", "RAM", "BMW", "USA", "II", "III", "IV"]:
                    df["Address"] = df["Address"].str.replace(rf"\b{abbr.title()}(?=\b|[.,;:!?\s]|$)", abbr, regex=True)
                # Remove trailing periods, commas, and spaces
                df["Address"] = df["Address"].str.replace(r"[.,\s]+$", "", regex=True)
            if "Dealership" in df.columns:
                df["Dealership"] = df["Dealership"].str.title()
                for abbr in ["NE", "NW", "SE", "SW", "GMC", "FIAT", "RAM", "BMW", "USA", "II", "III", "IV"]:
                    df["Dealership"] = df["Dealership"].str.replace(rf"\b{abbr.title()}(?=\b|[.,;:!?\s]|$)", abbr, regex=True)
            if "City" in df.columns:
                df["City"] = df["City"].str.title()
                df["City"] = df["City"].str.rstrip(", ")
            # Remove 'https://www.' from the beginning of Website column values
            if "Website" in df.columns:
                # Remove all leading http(s):// and www.
                df["Website"] = df["Website"].str.replace(r"^https?://(www\.)?", "", regex=True)
                # Replace backslashes with forward slashes
                df["Website"] = df["Website"].str.replace(r"\\+", "/", regex=True)
                # Remove trailing slashes
                df["Website"] = df["Website"].str.rstrip("/")
            # Reorder columns for Excel/CSV output
            desired_order = [
                "Dealership", "Dealer Group", "Dealership Type", "Car Brand", "Address", "City", "State/Province", "Postal Code", "Phone", "Country", "Website"
            ]
            # Only include columns that exist in the DataFrame
            cols_in_df = [col for col in desired_order if col in df.columns]
            other_cols = [col for col in df.columns if col not in cols_in_df]
            df = df[cols_in_df + other_cols]
            st.session_state.scrape_cache[key] = df
            print("DEBUG: DataFrame cached", file=sys.stderr)
            return df
        except Exception as e:
            st.error(f"Error after scraping: {e}")
            print(f"DEBUG: Exception after scraping: {e}", file=sys.stderr)
            st.text("\n".join(output_lines))
            raise


def main():
    st.set_page_config(page_title="Dealer Group Dealership Scraper", layout="centered")
    st.image("trackhawk_logo.png", width=200)
    st.title("Dealer Group Dealership Scraper")
    name = st.text_input("Dealer Group Name", placeholder="e.g., Lithia Motors")
    url = st.text_input("Dealer Locations Page URL")
    if st.button("Extract Dealerships"):
        try:
            df = scrape_with_external(name, url)
            if df.empty:
                st.error("No dealerships found.")
                return
            st.success(f"✅ {len(df)} valid dealerships extracted from the website")
            st.dataframe(df, use_container_width=True)

            # Save Excel to buffer
            buf = BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                df.to_excel(w, index=False)
            buf.seek(0)

            # Read back from buffer to double-check row count in Excel
            df_excel = pd.read_excel(buf)
            st.info(f"📄 {len(df_excel)} dealerships in the Excel file")

            st.download_button("📄 Excel", buf, f"{name}_locations.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.download_button("📑 CSV", df.to_csv(index=False).encode(), f"{name}_locations.csv", "text/csv")
        except Exception as e:
            st.error(f"Error: {e}")
    st.markdown("---")

if __name__ == "__main__":
    main()
