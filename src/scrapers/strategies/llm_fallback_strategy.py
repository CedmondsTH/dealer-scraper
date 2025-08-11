from typing import List, Dict, Any
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from ..base_scraper import ScraperStrategy
from ...services.rule_store import RuleStore, DomainRule


PROMPT = (
    "You are an information extractor. Given an HTML snippet of a dealer group page, "
    "return a JSON array of objects with keys: Name, Street, City, State, Zip, Phone, Website. "
    "Only include real physical locations present in the snippet. Use two-letter US state codes. "
    "Return JSON only, no extra text."
)


class LLMExtractorStrategy(ScraperStrategy):
    def __init__(self, store: RuleStore | None = None) -> None:
        self.store = store or RuleStore()

    @property
    def strategy_name(self) -> str:
        return "LLM Fallback Extractor"

    def can_handle(self, html: str, page_url: str) -> bool:
        # Always false here; this strategy will be invoked by service only when count=0
        return False

    # Not used by the main flow; provided for completeness/testing
    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        return self._extract_with_llm(html, page_url)

    def _extract_with_llm(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        try:
            from openai import OpenAI
        except Exception:
            return []

        # Compact HTML: strip scripts/styles; keep text+links
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text_html = str(soup)[:40000]

        # Get API key from environment
        api_key = os.environ.get("OPENAI_API_KEY")
        
        # TEMPORARY: Hardcode API key for testing
        if not api_key:
            print("ERROR: No API key in environment, using hardcoded key for testing")
            api_key = os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            print("ERROR: No API key available")
            return []
        
        print(f"DEBUG: Using OpenAI API key: {api_key[:20]}...")

        client = OpenAI(api_key=api_key)
        
        try:
            completion = client.chat.completions.create(
                model=os.environ.get("LLM_MODEL", "gpt-4o-mini"),
                messages=[{"role": "system", "content": PROMPT}, {"role": "user", "content": text_html}],
                temperature=0,
                response_format={"type": "json_object"} if os.environ.get("LLM_JSON_OBJECT") else None,
            )
        except Exception as e:
            print(f"ERROR: LLM API call failed: {str(e)}")
            if "rate limit" in str(e).lower():
                print("ERROR: OpenAI API rate limit exceeded. The scraper will continue without LLM fallback.")
            elif "quota" in str(e).lower():
                print("ERROR: OpenAI API quota exceeded. Please check your billing.")
            else:
                print(f"ERROR: OpenAI API error: {str(e)}")
            return []

        content = completion.choices[0].message.content
        # Try to find JSON array in the response
        import json
        try:
            data = json.loads(content)
            if isinstance(data, dict) and "items" in data:
                items = data["items"]
            elif isinstance(data, list):
                items = data
            else:
                items = []
        except Exception:
            # Fallback: extract first JSON array
            m = re.search(r"\[(?:.|\n)*\]", content)
            import json
            items = json.loads(m.group(0)) if m else []

        # Validate and normalize; also attempt to promote a basic learned rule
        parsed = urlparse(page_url)
        host = (parsed.hostname or "").lower()
        rule_saved = False
        dealers: List[Dict[str, Any]] = []
        for it in items:
            name = (it.get("Name") or it.get("name") or "").strip()
            street = (it.get("Street") or it.get("street") or "").strip()
            city = (it.get("City") or it.get("city") or "").strip()
            state = (it.get("State") or it.get("state") or "").strip().upper()
            zip_code = (it.get("Zip") or it.get("zip") or "").strip()
            phone = (it.get("Phone") or it.get("phone") or "").strip()
            website = (it.get("Website") or it.get("website") or page_url).strip()

            if not name or not (street or (city and state)):
                continue
            if state and not re.match(r"^[A-Z]{2}$", state):
                continue
            if zip_code and not re.match(r"^\d{5}(-\d{4})?$", zip_code):
                zip_code = ""
            if phone and not re.search(r"\d{3}[-.\s]?\d{3}[-.\s]?\d{4}", phone):
                phone = ""

            dealers.append({
                "Name": name,
                "Street": street,
                "City": city,
                "State": state,
                "Zip": zip_code,
                "Phone": phone,
                "Website": website,
                "Country": "USA",
                "DealerType": "New Car Dealer",
                "CarBrands": "",
            })

        # Heuristic promotion (very conservative): if we found >= 3 items, store rules
        if len(dealers) >= 3:
            # Store domain-specific rule
            domain_rule = DomainRule(
                host=host,
                path_pattern=re.escape(parsed.path or "/"),
                version=1,
                card_selector="section, div, li",  # coarse; refined later by operator or auto-tuner
                fields={
                    "name": "b, strong, h2, h3",
                    "street": "p, .address, .street", 
                    "city_state_zip": ".address, p",
                    "phone": "a[href^='tel:'], .phone",
                    "website": "a[href^='http']",
                },
                dom_signature="",
                success_count=0,
            )
            
            # Store pattern-based rule for similar layouts
            pattern_signature = self._generate_layout_signature(html)
            if pattern_signature:
                pattern_rule = DomainRule(
                    host="*pattern*",  # Special host for pattern matching
                    path_pattern=pattern_signature,  # Use signature as pattern
                    version=1,
                    card_selector=".location-item, .dealer-location, .store-location, [class*='location'][class*='item'], [class*='dealer'][class*='card'], section:has(.address)",
                    fields={
                        "name": "h3, h4, h5, .location-name, .dealer-name, .store-name, strong:first-of-type, b:first-of-type",
                        "street": ".address .street, .location .address, .address-line, [class*='street'], .addr:first-line", 
                        "city_state_zip": ".address .city-state-zip, .location .city-state, .address-line:last-of-type, [class*='city-state']",
                        "phone": "a[href^='tel:'], .phone, [class*='phone'], [href*='tel:']",
                        "website": "a[href^='http']:not([href*='directions']):not([href*='maps']), [href*='http']",
                    },
                    dom_signature=pattern_signature,
                    success_count=1,
                )
                
            try:
                self.store.upsert(domain_rule)
                if pattern_signature:
                    self.store.upsert(pattern_rule)
                rule_saved = True
            except Exception:
                pass

        return dealers

    def _generate_layout_signature(self, html: str) -> str:
        """Generate a layout signature based on HTML structure patterns."""
        try:
            soup = BeautifulSoup(html, "lxml")
            
            # Analyze structure patterns
            signatures = []
            
            # Count common container patterns
            sections = len(soup.find_all(['section', 'div', 'article'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['location', 'dealer', 'store', 'office', 'branch']
            )))
            if sections >= 3:
                signatures.append(f"containers:{sections}")
            
            # Check for list patterns
            lists = soup.find_all(['ul', 'ol'])
            list_items = sum(len(lst.find_all('li')) for lst in lists)
            if list_items >= 3:
                signatures.append(f"lists:{list_items}")
            
            # Check for address-like patterns
            address_patterns = soup.find_all(text=lambda text: text and re.search(
                r'\d+\s+[A-Za-z\s]+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Dr|Drive)',
                text
            ))
            if len(address_patterns) >= 3:
                signatures.append("addresses:multiple")
            
            # Check for phone patterns
            phone_patterns = soup.find_all(text=lambda text: text and re.search(
                r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
                text
            ))
            if len(phone_patterns) >= 3:
                signatures.append("phones:multiple")
            
            # Check for state patterns (common in dealer listings)
            state_patterns = soup.find_all(text=lambda text: text and re.search(
                r'\b[A-Z]{2}\s+\d{5}',  # State code + ZIP
                text
            ))
            if len(state_patterns) >= 3:
                signatures.append("states:multiple")
            
            # Generate final signature
            if len(signatures) >= 2:  # Need at least 2 pattern indicators
                return "layout:" + "|".join(sorted(signatures))
            
            return ""
            
        except Exception:
            return ""

