"""
Group 1 Automotive specific scraping strategy.

This strategy handles the HTML structure used by
Group 1 Automotive dealer location pages.
"""

import re
import sys
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from ...utils.address_parser import parse_address
from ..base_scraper import ScraperStrategy


class Group1AutomotiveStrategy(ScraperStrategy):
    """Extracts dealer data from Group 1 Automotive HTML structure."""

    @property
    def strategy_name(self) -> str:
        return "Group 1 Automotive HTML"

    def can_handle(self, html: str, page_url: str) -> bool:
        """Check if page contains Group 1 Automotive structure."""
        soup = BeautifulSoup(html, "html.parser")

        # Look for Group 1 specific indicators (updated selectors)
        group1_indicators = soup.select("div.dealerResults__listing")

        # Also check URL or content for Group 1
        is_group1_page = (
            "group1auto" in page_url.lower()
            or "group1" in html.lower()
            or len(group1_indicators) > 0
        )

        return len(group1_indicators) > 0 and is_group1_page

    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealers from Group 1 Automotive HTML structure."""
        soup = BeautifulSoup(html, "html.parser")
        dealers = []

        # Extract from Group 1 listing elements
        for listing in soup.select("div.dealerResults__listing"):
            dealer = self._extract_dealer_from_listing(listing, page_url)
            if dealer:
                dealers.append(dealer)

        print(
            f"DEBUG: Group 1 Automotive strategy extracted {len(dealers)} dealers",
            file=sys.stderr,
        )
        return dealers

    def _extract_dealer_from_listing(self, listing, page_url: str) -> Dict[str, Any]:
        """Extract dealer information from a Group 1 listing element."""
        try:
            # Extract dealer name
            name_el = listing.select_one(".dealerResults__listing--name")
            name = name_el.get_text(strip=True) if name_el else ""

            # Debug: Print when name extraction fails
            if not name:
                print(
                    f"DEBUG: Name extraction failed for listing with HTML: {str(listing)[:200]}...",
                    file=sys.stderr,
                )
                return None

            # Extract address
            address_el = listing.select_one(".dealerResults__listing--address")
            address = address_el.get_text(strip=True) if address_el else ""

            # Extract phone (prefer sales phone)
            phone_el = listing.select_one(".dealerResults__listing--phoneSales a")
            if not phone_el:
                phone_el = listing.select_one(".dealerResults__listing--phoneService a")
            if not phone_el:
                phone_el = listing.select_one("a[href^='tel:']")

            phone = ""
            if phone_el:
                href = phone_el.get("href", "")
                if href.startswith("tel:"):
                    phone = href[4:]  # Remove 'tel:'
                else:
                    phone = phone_el.get_text(strip=True)

            # Extract website
            website_el = listing.select_one(".website")
            if not website_el:
                website_el = listing.select_one(
                    "a[href^='http']:not([href*='group1auto.com']):not([href*='tel:'])"
                )

            website = website_el.get("href", page_url) if website_el else page_url

            # Parse address into components using the old method for now
            street, city, state, zip_code = self._parse_address_components(address)

            # Debug: Print parsed components
            print(
                f"DEBUG: Address '{address}' -> Street: '{street}', City: '{city}', State: '{state}', Zip: '{zip_code}'",
                file=sys.stderr,
            )

            return {
                "Name": str(name).strip(),
                "Street": str(street).strip(),
                "City": str(city).strip(),
                "State": str(state).strip(),
                "Zip": str(zip_code).strip(),
                "Country": "USA",
                "Phone": re.sub(r"[^\d\-\(\)\s\+]", "", str(phone)).strip(),
                "Website": str(website).strip() if website else page_url,
                "DealerType": "New Car Dealer",
                "CarBrands": ", ".join(self._extract_brands_from_text(name)),
            }

        except Exception as e:
            print(
                f"DEBUG: Error extracting dealer from Group 1 listing: {e}",
                file=sys.stderr,
            )
            return None

    def _parse_address_components(self, address: str) -> tuple:
        """Parse address string into components."""
        if not address:
            return "", "", "", ""

        # Helper: normalize state to 2-letter code
        def normalize_state(state_str: str) -> str:
            state_lookup = {
                "ALABAMA": "AL",
                "ALASKA": "AK",
                "ARIZONA": "AZ",
                "ARKANSAS": "AR",
                "CALIFORNIA": "CA",
                "COLORADO": "CO",
                "CONNECTICUT": "CT",
                "DELAWARE": "DE",
                "FLORIDA": "FL",
                "GEORGIA": "GA",
                "HAWAII": "HI",
                "IDAHO": "ID",
                "ILLINOIS": "IL",
                "INDIANA": "IN",
                "IOWA": "IA",
                "KANSAS": "KS",
                "KENTUCKY": "KY",
                "LOUISIANA": "LA",
                "MAINE": "ME",
                "MARYLAND": "MD",
                "MASSACHUSETTS": "MA",
                "MICHIGAN": "MI",
                "MINNESOTA": "MN",
                "MISSISSIPPI": "MS",
                "MISSOURI": "MO",
                "MONTANA": "MT",
                "NEBRASKA": "NE",
                "NEVADA": "NV",
                "NEW HAMPSHIRE": "NH",
                "NEW JERSEY": "NJ",
                "NEW MEXICO": "NM",
                "NEW YORK": "NY",
                "NORTH CAROLINA": "NC",
                "NORTH DAKOTA": "ND",
                "OHIO": "OH",
                "OKLAHOMA": "OK",
                "OREGON": "OR",
                "PENNSYLVANIA": "PA",
                "RHODE ISLAND": "RI",
                "SOUTH CAROLINA": "SC",
                "SOUTH DAKOTA": "SD",
                "TENNESSEE": "TN",
                "TEXAS": "TX",
                "UTAH": "UT",
                "VERMONT": "VT",
                "VIRGINIA": "VA",
                "WASHINGTON": "WA",
                "WEST VIRGINIA": "WV",
                "WISCONSIN": "WI",
                "WYOMING": "WY",
                # DC and territories
                "DISTRICT OF COLUMBIA": "DC",
                "WASHINGTON DC": "DC",
                "DC": "DC",
            }
            cleaned = (state_str or "").strip().upper().rstrip(".")
            if len(cleaned) == 2 and cleaned.isalpha():
                return cleaned
            return state_lookup.get(cleaned, cleaned[:2])  # fallback to first 2 letters

        # Helper: remove trailing ", USA" and period
        def strip_country_and_period(text: str) -> str:
            t = (text or "").strip()
            t = t.rstrip(".")
            if t.upper().endswith(", USA"):
                t = t[:-5].rstrip()
            elif t.upper().endswith("USA"):
                t = t[:-3].rstrip().rstrip(",")
            return t

        # Group 1 format variations:
        # "Street | City, State ZIP" OR "Street, City | State ZIP"
        if "|" in address:
            parts = address.split("|")
            if len(parts) == 2:
                left_part = parts[0].strip()
                right_part = strip_country_and_period(parts[1])

                # Case 1: "Street | City, State [ZIP]"
                if "," in right_part:
                    last_comma = right_part.rfind(",")
                    if last_comma != -1:
                        city = right_part[:last_comma].strip()
                        state_zip = right_part[last_comma + 1 :].strip()
                        tokens = state_zip.split()
                        zip_code = ""
                        state_token = ""
                        if tokens:
                            if tokens[-1].isdigit() and len(tokens[-1]) == 5:
                                zip_code = tokens[-1]
                                state_token = " ".join(tokens[:-1])
                            else:
                                state_token = " ".join(tokens)
                        state_abbr = normalize_state(state_token)
                        return left_part, city, state_abbr, zip_code

                # Case 2: "Street, City | State [ZIP]"
                if "," in left_part:
                    street_city = left_part.split(",")
                    if len(street_city) == 2:
                        street = street_city[0].strip()
                        city = street_city[1].strip()

                        right_clean = strip_country_and_period(right_part)
                        tokens = right_clean.split()
                        zip_code = ""
                        state_token = ""
                        if tokens:
                            if tokens[-1].isdigit() and len(tokens[-1]) == 5:
                                zip_code = tokens[-1]
                                state_token = " ".join(tokens[:-1])
                            else:
                                state_token = " ".join(tokens)
                        state_abbr = normalize_state(state_token)
                        return street, city, state_abbr, zip_code

        # Fallback: "Street, City, State [ZIP][, USA]"
        addr_clean = strip_country_and_period(address)
        match = re.match(
            r"(.+),\s*(.+?),\s*([A-Za-z\.\s]+?)(?:\s+(\d{5}))?$", addr_clean
        )
        if match:
            street = match.group(1).strip()
            city = match.group(2).strip()
            state_abbr = normalize_state(match.group(3))
            zip_code = (match.group(4) or "").strip()
            return street, city, state_abbr, zip_code

        # Handle single comma format: "Street City, State ZIP" (no comma between street and city)
        parts = addr_clean.split(",")
        if len(parts) == 2:
            left_part = parts[0].strip()  # "15943 Gulf Freeway Webster"
            right_part = parts[1].strip()  # "TX 77598" or "Texas 77598" or "CA"

            # Parse state and optional ZIP from right part
            tokens = right_part.split()
            state = ""
            zip_code = ""
            if tokens:
                if tokens[-1].isdigit() and len(tokens[-1]) == 5:
                    zip_code = tokens[-1]
                    state = normalize_state(" ".join(tokens[:-1]))
                else:
                    state = normalize_state(" ".join(tokens))

                # Split left part by spaces to separate street from city
                # For addresses like "15943 Gulf Freeway Webster", we need to detect where street ends and city begins
                words = left_part.split()
                if len(words) >= 2:
                    # Common city names that might be multi-word
                    multi_word_cities = [
                        "Clear Lake",
                        "Sugar Land",
                        "Round Rock",
                        "El Paso",
                        "Santa Fe",
                        "Newport Beach",
                        "Beverly Hills",
                        "Panama City",
                        "Rock Hill",
                        "Rockville Centre",
                        "Landover Hills",
                    ]

                    # Check if last 2 words form a known multi-word city
                    if len(words) >= 3:
                        potential_city = " ".join(words[-2:])
                        if potential_city in multi_word_cities:
                            street = " ".join(words[:-2])
                            city = potential_city
                            return street, city, state, zip_code

                    # Default: assume last word is the city (most common case)
                    street = " ".join(words[:-1])
                    city = words[-1]
                    return street, city, state, zip_code

        # Fallback: split by commas (original logic)
        if len(parts) >= 3:
            street = parts[0].strip()
            city = parts[1].strip()
            # parts[2] might be "CA 90210" or just "CA" (and parts[3] could be "USA")
            state_zip_tokens = parts[2].strip().split()
            state = ""
            zip_code = ""
            if state_zip_tokens:
                if state_zip_tokens[-1].isdigit() and len(state_zip_tokens[-1]) == 5:
                    zip_code = state_zip_tokens[-1]
                    state = normalize_state(" ".join(state_zip_tokens[:-1]))
                else:
                    state = normalize_state(" ".join(state_zip_tokens))
            return street, city, state, zip_code

        return address, "", "", ""

    def _extract_brands_from_text(self, text: str) -> List[str]:
        """Extract car brands from dealer name."""
        brands = []
        brand_keywords = [
            "Toyota",
            "Honda",
            "Ford",
            "Chevrolet",
            "Chevy",
            "Nissan",
            "BMW",
            "Mercedes",
            "Audi",
            "Volkswagen",
            "VW",
            "Subaru",
            "Mazda",
            "Hyundai",
            "Kia",
            "Lexus",
            "Acura",
            "Infiniti",
            "Volvo",
            "Jaguar",
            "Land Rover",
            "Porsche",
            "Cadillac",
            "Buick",
            "GMC",
            "Dodge",
            "Chrysler",
            "Jeep",
            "Ram",
            "Lincoln",
            "Genesis",
        ]

        text_upper = text.upper()
        for brand in brand_keywords:
            if brand.upper() in text_upper:
                brands.append(brand)

        return brands
