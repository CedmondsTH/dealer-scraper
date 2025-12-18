"""
Hudson Automotive Group scraping strategy
"""

import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from src.scrapers.base_scraper import ScraperStrategy
from src.utils.address_parser import parse_address


class HudsonAutomotiveStrategy(ScraperStrategy):
    """Strategy for Hudson Automotive Group locations page"""

    @property
    def strategy_name(self) -> str:
        return "Hudson Automotive HTML"

    def can_handle(self, html: str, page_url: str) -> bool:
        """Check if this is a Hudson Automotive page"""
        return "hudsonauto.com" in page_url.lower()

    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealer information from Hudson Automotive locations page"""
        dealers = []
        soup = BeautifulSoup(html, "html.parser")

        # Hudson uses a specific structure with dealer names in h5 headings
        # and addresses in paragraphs
        dealer_cards = (
            soup.find_all("div", class_=lambda x: x and "cursor-pointer" in str(x))
            if soup.find_all("div", class_=lambda x: x and "cursor-pointer" in str(x))
            else []
        )

        # Also try finding by heading level 5 which contains dealership names
        if not dealer_cards:
            dealer_headings = soup.find_all("h5")
            for heading in dealer_headings:
                # Get the dealership name
                name = heading.get_text(strip=True)

                # Skip if not a valid name
                if not name or len(name) < 3:
                    continue

                # Find the address in the next paragraph sibling
                parent = heading.find_parent()
                if parent:
                    address_elem = parent.find("p")
                    if address_elem:
                        address_text = address_elem.get_text(strip=True)

                        # Parse the address (returns tuple: street, city, state, zip)
                        street, city, state, zip_code = parse_address(address_text)

                        if street and city:
                            dealer = {
                                "name": name,
                                "street": street,
                                "city": city,
                                "state": state,
                                "zip": zip_code,
                                "phone": "",
                                "website": "",
                                "page_url": page_url,
                            }
                            dealers.append(dealer)

        # Alternative: Look for any element containing both dealership name patterns and addresses
        if not dealers:
            # Hudson page has location names followed by addresses in a specific pattern
            text_content = soup.get_text()

            # Pattern: Dealership Name followed by address on next line
            # Example: "Hoover Toyota\n2686 John Hawkins Parkway, Hoover, AL 35244"
            lines = [line.strip() for line in text_content.split("\n") if line.strip()]

            i = 0
            while i < len(lines) - 1:
                current_line = lines[i]
                next_line = lines[i + 1] if i + 1 < len(lines) else ""

                # Check if current line looks like a dealership name
                # (contains common dealership words and is relatively short)
                dealership_keywords = [
                    "toyota",
                    "ford",
                    "honda",
                    "hyundai",
                    "chrysler",
                    "dodge",
                    "jeep",
                    "ram",
                    "chevrolet",
                    "gmc",
                    "buick",
                    "nissan",
                    "mazda",
                    "volkswagen",
                    "subaru",
                    "kia",
                ]

                is_dealership = any(
                    keyword in current_line.lower() for keyword in dealership_keywords
                )

                # Check if next line looks like an address (has numbers and state)
                has_address_pattern = re.search(r"\d+.*[A-Z]{2}\s+\d{5}", next_line)

                if is_dealership and has_address_pattern and len(current_line) < 100:
                    # Parse the address (returns tuple: street, city, state, zip)
                    street, city, state, zip_code = parse_address(next_line)

                    if street and city:
                        dealer = {
                            "name": current_line,
                            "street": street,
                            "city": city,
                            "state": state,
                            "zip": zip_code,
                            "phone": "",
                            "website": "",
                            "page_url": page_url,
                        }
                        dealers.append(dealer)
                        i += 2  # Skip the address line
                        continue

                i += 1

        print(f"DEBUG: Hudson Automotive strategy extracted {len(dealers)} dealers")
        return dealers
