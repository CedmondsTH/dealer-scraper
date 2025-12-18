"""
JavaScript variable extraction strategy.

This strategy extracts dealer information from JavaScript variables
commonly used to store location data on dealer websites.
"""

import json
import re
import sys
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from ..base_scraper import ScraperStrategy


class JavaScriptStrategy(ScraperStrategy):
    """Extracts dealer data from JavaScript variable arrays."""

    @property
    def strategy_name(self) -> str:
        return "JavaScript Variables"

    def can_handle(self, html: str, page_url: str) -> bool:
        """Check if page contains JavaScript variables with location data."""
        # Look for common patterns in JavaScript
        patterns = [
            r"(?:var|let|const)\s+(?:locations|dealers|stores)\s*=\s*\[",
            r"window\.dealerData\s*=\s*\[",
            r"locationData:\s*\[",
            r"agile-store-locator",  # Agile Store Locator plugin
            r"ASL_REMOTE.*ajax_url",  # ASL AJAX configuration
        ]

        for pattern in patterns:
            if re.search(pattern, html, re.IGNORECASE):
                return True

        return False

    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealers from JavaScript variables."""
        soup = BeautifulSoup(html, "html.parser")
        dealers = []

        # Check for Agile Store Locator first
        if "agile-store-locator" in html.lower():
            print(f"DEBUG: Detected Agile Store Locator plugin", file=sys.stderr)
            asl_dealers = self._extract_asl_dealers(html, page_url)
            if asl_dealers:
                return asl_dealers

        # JavaScript variable patterns to search for
        patterns = [
            r"(?:var|let|const)\s+(?:locations|dealers|stores)\s*=\s*(\[.*?\]);",
            r"window\.dealerData\s*=\s*(\[.*?\]);",
            r"locationData:\s*(\[.*?\])",
        ]

        for script in soup.find_all("script"):
            script_text = script.string or ""

            for pattern in patterns:
                matches = re.finditer(pattern, script_text, re.DOTALL | re.IGNORECASE)

                for match in matches:
                    try:
                        json_str = match.group(1)
                        data_array = json.loads(json_str)

                        if isinstance(data_array, list):
                            for item in data_array:
                                dealer = self._extract_dealer_from_js_object(
                                    item, page_url
                                )
                                if dealer:
                                    dealers.append(dealer)

                    except json.JSONDecodeError as e:
                        print(
                            f"DEBUG: Failed to parse JavaScript JSON: {e}",
                            file=sys.stderr,
                        )
                        continue
                    except Exception as e:
                        print(
                            f"DEBUG: Error processing JavaScript data: {e}",
                            file=sys.stderr,
                        )
                        continue

        print(
            f"DEBUG: JavaScript strategy extracted {len(dealers)} dealers",
            file=sys.stderr,
        )
        return dealers

    def _extract_dealer_from_js_object(self, obj: Any, page_url: str) -> Dict[str, Any]:
        """Extract dealer information from a JavaScript object."""
        if not isinstance(obj, dict):
            return None

        try:
            # Extract name (try multiple possible keys)
            name = (
                obj.get("name")
                or obj.get("title")
                or obj.get("storeName")
                or obj.get("locationName")
                or ""
            )

            if not name:
                return None

            # Extract address components
            street = (
                obj.get("address")
                or obj.get("street")
                or obj.get("streetAddress")
                or ""
            )

            city = obj.get("city") or obj.get("locality") or ""

            state = obj.get("state") or obj.get("province") or obj.get("region") or ""

            zip_code = (
                obj.get("zip")
                or obj.get("zipCode")
                or obj.get("postalCode")
                or obj.get("postal")
                or ""
            )

            # Extract contact information
            phone = (
                obj.get("phone") or obj.get("telephone") or obj.get("phoneNumber") or ""
            )

            website = (
                obj.get("url") or obj.get("website") or obj.get("link") or page_url
            )

            return {
                "name": name,
                "street": street,
                "city": city,
                "state": state,
                "zip": zip_code,
                "phone": phone,
                "website": website,
            }

        except Exception as e:
            print(
                f"DEBUG: Error extracting dealer from JS object: {e}", file=sys.stderr
            )
            return None

    def _extract_asl_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealers from Agile Store Locator plugin data."""
        import base64
        from urllib.parse import urljoin

        import requests

        dealers = []
        ajax_url = None

        try:
            # First try to find direct ASL configuration
            ajax_patterns = [
                r'var ASL_REMOTE = \{[^}]*"ajax_url":"([^"]+)"',  # JSON format
                r"ajax_url.*?[\"'](https?://[^\"']*admin-ajax\.php)[\"']",  # Generic admin-ajax pattern
            ]

            for pattern in ajax_patterns:
                ajax_match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if ajax_match:
                    ajax_url = ajax_match.group(1).replace(
                        "\/", "/"
                    )  # Unescape slashes
                    break

            # If not found, try to decode base64 encoded scripts
            if not ajax_url:
                base64_pattern = r'src="data:text/javascript;base64,([^"]+)"'
                base64_matches = re.findall(base64_pattern, html)

                for b64_data in base64_matches:
                    try:
                        # Decode base64
                        decoded = base64.b64decode(b64_data + "==").decode(
                            "utf-8", errors="ignore"
                        )  # Add padding

                        # Look for ASL_REMOTE in decoded content
                        if "ASL_REMOTE" in decoded and "ajax_url" in decoded:
                            ajax_match = re.search(r'"ajax_url":"([^"]+)"', decoded)
                            if ajax_match:
                                ajax_url = ajax_match.group(1).replace("\/", "/")
                                print(
                                    f"DEBUG: Found ASL AJAX URL in base64: {ajax_url}",
                                    file=sys.stderr,
                                )
                                break
                    except Exception as e:
                        continue  # Skip malformed base64

            if ajax_url:
                print(f"DEBUG: Found ASL AJAX URL: {ajax_url}", file=sys.stderr)

                # Try to fetch location data via AJAX
                try:
                    # ASL typically uses these actions for loading stores
                    asl_actions = [
                        "asl_load_stores",
                        "asl_stores_load",
                        "asl_load_store",
                    ]

                    for action in asl_actions:
                        response = requests.get(
                            ajax_url,
                            params={
                                "action": action,
                                "nonce": "",  # Try without nonce first
                                "load_all": "1",  # Load all stores
                                "lat": "",  # No location filter
                                "lng": "",
                                "distance": "100000",  # Large distance to get all
                            },
                            headers={
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                                "Referer": page_url,
                            },
                            timeout=15,
                        )

                        if response.status_code == 200:
                            try:
                                data = response.json()
                                if data and len(str(data)) > 50:  # Has meaningful data
                                    print(
                                        f"DEBUG: ASL AJAX success with action '{action}': {len(str(data))} characters",
                                        file=sys.stderr,
                                    )
                                    break
                            except json.JSONDecodeError:
                                continue
                    else:
                        print(f"DEBUG: All ASL AJAX actions failed", file=sys.stderr)
                        return dealers

                    # Process successful response
                    print(
                        f"DEBUG: ASL AJAX response: {len(str(data))} characters",
                        file=sys.stderr,
                    )

                    # ASL can return stores in different formats
                    stores = []
                    if isinstance(data, list):
                        stores = data
                    elif isinstance(data, dict):
                        stores = data.get("stores", data.get("data", []))

                    print(
                        f"DEBUG: ASL found {len(stores)} stores in response",
                        file=sys.stderr,
                    )

                    for store in stores:
                        dealer = self._extract_asl_store(store, page_url)
                        if dealer:
                            dealers.append(dealer)

                except requests.RequestException as e:
                    print(f"DEBUG: ASL AJAX request failed: {e}", file=sys.stderr)
                except json.JSONDecodeError as e:
                    print(f"DEBUG: ASL AJAX response not JSON: {e}", file=sys.stderr)
            else:
                print(f"DEBUG: No ASL AJAX URL found", file=sys.stderr)

        except Exception as e:
            print(f"DEBUG: Error processing ASL data: {e}", file=sys.stderr)

        print(f"DEBUG: ASL extraction found {len(dealers)} dealers", file=sys.stderr)
        return dealers

    def _extract_asl_store(
        self, store: Dict[str, Any], page_url: str
    ) -> Dict[str, Any]:
        """Extract dealer information from an ASL store object."""
        try:
            # ASL store format typically includes: id, title, description, street, city, state, postal_code, phone, etc.
            name = store.get("title", "").strip()
            if not name:
                return None

            street = store.get("street", "").strip()
            city = store.get("city", "").strip()
            state = store.get("state", "").strip()
            zip_code = store.get("postal_code", "").strip()
            phone = store.get("phone", "").strip()

            return {
                "name": name,
                "street": street,
                "city": city,
                "state": state,
                "zip": zip_code,
                "phone": phone,
                "website": page_url,
            }

        except Exception as e:
            print(f"DEBUG: Error extracting ASL store: {e}", file=sys.stderr)
            return None
