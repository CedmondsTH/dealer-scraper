import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from ..base_scraper import ScraperStrategy


class DealerDotComContentBlocksStrategy(ScraperStrategy):
    """Parses Dealer.com pages that present locations as rich text blocks
    inside `ddc-content content-default` containers (e.g., Anderson Automotive).
    """

    @property
    def strategy_name(self) -> str:
        return "Dealer.com Content Blocks HTML"

    def can_handle(self, html: str, page_url: str) -> bool:
        soup = BeautifulSoup(html, "lxml")

        # Dealer.com indicator
        provider_meta = soup.select_one('meta[name="providerID"][content="DDC"]')
        has_ddc_blocks = bool(
            soup.select("div.ddc-content.content-default .text-content-container")
        )
        # Some sites (e.g., Baker Auto Group home) list stores without a Locations title
        visit_site_links = [
            a
            for a in soup.find_all("a")
            if "visit site" in (a.get_text(" ", strip=True) or "").lower()
        ]
        has_visit_site = len(visit_site_links) >= 2
        mentions_dealer_com = (
            "dealer.com" in (soup.get_text(" ", strip=True) or "").lower()
        )

        # Be permissive: run on pages with repeated Visit Site links or DDC content blocks
        return has_ddc_blocks or has_visit_site

    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "lxml")
        dealers: List[Dict[str, Any]] = []

        blocks = soup.select("div.ddc-content.content-default .text-content-container")
        if not blocks:
            # Fallback: collect containers around repeated "Visit Site" links
            visit_links = [
                a
                for a in soup.find_all("a")
                if "visit site" in (a.get_text(" ", strip=True) or "").lower()
            ]
            candidates = []
            for a in visit_links:
                # Go up to a reasonable container (Dealer.com often nests within a few divs)
                container = a
                for _ in range(4):
                    if (
                        container
                        and container.parent
                        and container.parent.name in ("div", "section", "li", "article")
                    ):
                        container = container.parent
                    else:
                        break
                if container and container not in candidates:
                    candidates.append(container)
            # Use candidates as blocks if present
            if candidates:
                blocks = candidates

        phone_regex = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
        # Accept multiple city/state/zip formats commonly found on Dealer.com content blocks
        city_state_zip_patterns = [
            re.compile(
                r"^([^,<>]+),\s*([A-Z]{2})\s*(\d{5})(?:-\d{4})?$"
            ),  # City, ST 12345
            re.compile(
                r"^([^,<>]+)\s+([A-Z]{2}),\s*(\d{5})(?:-\d{4})?$"
            ),  # City ST, 12345
            re.compile(
                r"^([^,<>]+)\s+([A-Z]{2})\s*(\d{5})(?:-\d{4})?$"
            ),  # City ST 12345 (no comma)
            re.compile(
                r"^([^,<>]+),\s*([A-Za-z][A-Za-z ]+)\s*(\d{5})(?:-\d{4})?$"
            ),  # City, StateName 12345
            re.compile(
                r"^([^,<>]+)\s+([A-Za-z][A-Za-z ]+),\s*(\d{5})(?:-\d{4})?$"
            ),  # City StateName, 12345
            re.compile(
                r"^([^,<>]+),\s*([A-Z]{2})\s*(\d{4})(?:-\d{4})?$"
            ),  # City, ST 1234 (handle bad 4-digit zips)
            re.compile(
                r"^([^,<>]+)\s+([A-Z]{2}),\s*(\d{4})(?:-\d{4})?$"
            ),  # City ST, 1234 (handle bad 4-digit zips)
            re.compile(r"^([^,<>]+),\s*([A-Z]{2})$"),  # City, ST (no zip)
            re.compile(r"^([^,<>]+)\s+([A-Z]{2})$"),  # City ST (no zip)
            re.compile(
                r"^([^,<>]+),\s*([A-Za-z][A-Za-z ]+)$"
            ),  # City, StateName (no zip)
        ]

        # Map full state names to 2-letter codes when encountered
        state_map = {
            "alabama": "AL",
            "alaska": "AK",
            "arizona": "AZ",
            "arkansas": "AR",
            "california": "CA",
            "colorado": "CO",
            "connecticut": "CT",
            "delaware": "DE",
            "district of columbia": "DC",
            "florida": "FL",
            "georgia": "GA",
            "hawaii": "HI",
            "idaho": "ID",
            "illinois": "IL",
            "indiana": "IN",
            "iowa": "IA",
            "kansas": "KS",
            "kentucky": "KY",
            "louisiana": "LA",
            "maine": "ME",
            "maryland": "MD",
            "massachusetts": "MA",
            "michigan": "MI",
            "minnesota": "MN",
            "mississippi": "MS",
            "missouri": "MO",
            "montana": "MT",
            "nebraska": "NE",
            "nevada": "NV",
            "new hampshire": "NH",
            "new jersey": "NJ",
            "new mexico": "NM",
            "new york": "NY",
            "north carolina": "NC",
            "north dakota": "ND",
            "ohio": "OH",
            "oklahoma": "OK",
            "oregon": "OR",
            "pennsylvania": "PA",
            "rhode island": "RI",
            "south carolina": "SC",
            "south dakota": "SD",
            "tennessee": "TN",
            "texas": "TX",
            "utah": "UT",
            "vermont": "VT",
            "virginia": "VA",
            "washington": "WA",
            "west virginia": "WV",
            "wisconsin": "WI",
            "wyoming": "WY",
        }

        for block in blocks:
            # Flatten text but preserve simple block order via <div> boundaries
            # Many Dealer.com blocks have <div><font><b>Name</b></font></div> followed by address lines
            lines: List[str] = []
            for child in block.find_all(["div", "p", "li"], recursive=True):
                t = child.get_text(" ", strip=True)
                if t:
                    lines.append(t)

            if not lines:
                continue

            # Name is often first meaningful line (bolded)
            name = lines[0].strip()
            # Guard against blocks that are only images or empty labels
            if not name or len(name) < 3:
                continue

            street = city = state = zip_code = phone = ""

            # Scan remaining lines for street + city/state/zip + phone
            for i in range(1, len(lines)):
                line = lines[i]
                # Remove common prefixes like "Directions" / "Get Directions"
                line = re.sub(r"^(Directions|Get Directions)\s+", "", line, flags=re.I)
                # Try multiple city/state/zip patterns
                match = None
                for pat in city_state_zip_patterns:
                    match = pat.match(line)
                    if match:
                        break
                if match:
                    city, state, zip_code = match.groups()
                    state_clean = state.strip()
                    # Normalize full state name to abbreviation if needed
                    if len(state_clean) > 2:
                        state_abbr = state_map.get(state_clean.lower())
                        if state_abbr:
                            state_clean = state_abbr
                    state = state_clean.upper()
                    # street is usually the immediate previous line
                    if i - 1 >= 0:
                        street = lines[i - 1].strip()
                    # continue scanning for phone below
                    continue

            # Phone anywhere in the block
            for ln in lines:
                pm = phone_regex.search(ln)
                if pm:
                    phone = pm.group(0)
                    break

            # Website: prefer a target link under this block (Visit Site)
            site = page_url
            # prioritize Visit Site
            link = None
            for a in block.find_all("a", href=True):
                if "visit site" in (a.get_text(" ", strip=True) or "").lower():
                    link = a
                    break
            if not link:
                link = block.find("a", href=True)
            if link and link["href"].startswith("http"):
                site = link["href"]

            if name and (street or (city and state)):
                dealers.append(
                    {
                        "Name": name,
                        "Street": street,
                        "City": city,
                        "State": state,
                        "Zip": zip_code,
                        "Country": "USA",
                        "Phone": phone,
                        "Website": site,
                        "DealerType": "New Car Dealer",
                        "CarBrands": "",
                    }
                )

        return dealers
