"""
NEW LLM fallback strategy with hardcoded API key to bypass caching issues.
"""

import json
import os
import re
import sys
from typing import List, Dict, Any

from bs4 import BeautifulSoup
from openai import OpenAI

from ..base_scraper import ScraperStrategy
from ...utils.address_parser import parse_address
from ...utils.data_cleaner import data_cleaner


class NewLLMExtractorStrategy(ScraperStrategy):
    """Uses OpenAI to extract dealer data from HTML as a fallback strategy."""
    
    @property
    def strategy_name(self) -> str:
        return "NEW LLM Fallback Extractor"
    
    def can_handle(self, html: str, page_url: str) -> bool:
        """This strategy can handle any HTML content."""
        return True
    
    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealer locations using OpenAI LLM."""
        return self._extract_with_llm(html, page_url)
    
    def _extract_with_llm(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealer locations using OpenAI LLM - called by scraper service."""
        
        # Use hardcoded API key to bypass all environment issues
        api_key = os.environ.get("OPENAI_API_KEY")
        
        print(f"NEW LLM DEBUG: Using hardcoded API key: {api_key[:20]}...")
        
        # Clean HTML for LLM processing - MUCH smaller for rate limits
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript", "head", "meta", "link"]):
            tag.decompose()
        
        # Keep only text content, much smaller
        text_content = soup.get_text()
        
        # Smart content extraction - look for dealer-related content
        lines = text_content.split('\n')
        dealer_related_lines = []
        
        # Expanded keywords for better content detection
        dealer_keywords = ['location', 'dealer', 'address', 'phone', 'store', 'showroom', 'service', 'sales', 
                          'automotive', 'contact', 'hours', 'directions', 'visit', 'find us', 'our locations',
                          'ray skillman', 'indianapolis', 'indiana', 'zip', 'call', 'email', 'street', 'avenue']
        
        for line in lines:
            line = line.strip()
            if line and any(keyword.lower() in line.lower() for keyword in dealer_keywords):
                dealer_related_lines.append(line)
        
        # If we found dealer-related content, use more of it; otherwise try middle section
        if dealer_related_lines and len('\n'.join(dealer_related_lines)) > 500:
            text_html = '\n'.join(dealer_related_lines)[:8000]  # Much larger for Ray Skillman
            print(f"NEW LLM DEBUG: Using {len(text_html)} RELEVANT characters (found {len(dealer_related_lines)} relevant lines)")
        else:
            # Try middle section instead of beginning (avoid headers/nav)
            middle_start = len(text_content) // 3
            text_html = text_content[middle_start:middle_start + 8000]
            print(f"NEW LLM DEBUG: Using {len(text_html)} MIDDLE characters (no relevant content found)")
        
        print(f"NEW LLM DEBUG: Using {len(text_html)} characters (reduced from {len(html)})")
        
        PROMPT = """
You are an expert at extracting dealership location data from HTML content.

Extract ALL automotive dealerships mentioned in the HTML, including their addresses, phone numbers, and any other relevant details.

Return your response as a JSON array of objects, where each object represents a dealership with these fields:
- name: The dealership name
- street: Street address
- city: City name  
- state: State abbreviation
- zip: ZIP code
- phone: Phone number
- website: Website URL (if available)
- brands: Car brands sold (if mentioned)

If you find dealerships, return them in this exact JSON format. If no dealerships are found, return an empty array [].
"""
        
        client = OpenAI(api_key=api_key)
        
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": PROMPT}, 
                    {"role": "user", "content": text_html}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            response_text = completion.choices[0].message.content
            print(f"NEW LLM DEBUG: Got response: {response_text[:200]}...")
            
            # Parse JSON response
            try:
                response_data = json.loads(response_text)
                if isinstance(response_data, dict) and "dealerships" in response_data:
                    dealers = response_data["dealerships"]
                elif isinstance(response_data, list):
                    dealers = response_data
                elif isinstance(response_data, dict) and "dealers" in response_data:
                    dealers = response_data["dealers"]
                else:
                    print(f"NEW LLM DEBUG: Unexpected response format: {response_data}")
                    return []
                
                print(f"NEW LLM DEBUG: Extracted {len(dealers)} dealers via LLM")
                
                # Process each dealer
                processed_dealers = []
                for dealer in dealers:
                    if isinstance(dealer, dict) and dealer.get("name"):
                        # Helper function to safely extract string values
                        def safe_str(value):
                            if isinstance(value, list):
                                return ", ".join(str(v) for v in value).strip()
                            return str(value).strip() if value else ""
                        
                        processed_dealer = {
                            "name": safe_str(dealer.get("name", "")),
                            "street": safe_str(dealer.get("street", "")),
                            "city": safe_str(dealer.get("city", "")),
                            "state": safe_str(dealer.get("state", "")),
                            "zip": safe_str(dealer.get("zip", "")),
                            "phone": safe_str(dealer.get("phone", "")),
                            "website": safe_str(dealer.get("website", "")),
                            "car_brands": safe_str(dealer.get("brands", ""))
                        }
                        
                        # Only include dealers with at least name and some location info
                        if processed_dealer["name"] and (processed_dealer["street"] or processed_dealer["city"]):
                            processed_dealers.append(processed_dealer)
                
                return processed_dealers
                
            except json.JSONDecodeError as e:
                print(f"NEW LLM ERROR: Failed to parse JSON response: {e}")
                print(f"NEW LLM ERROR: Response was: {response_text}")
                return []
                
        except Exception as e:
            print(f"NEW LLM ERROR: API call failed: {str(e)}")
            return []
