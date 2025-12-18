"""
Parsing utilities for extracting and standardizing data.

This module contains utilities for parsing addresses, phone numbers,
and other structured data from various formats.
"""

import re
from typing import Tuple


def parse_address(address_text: str) -> Tuple[str, str, str, str]:
    """
    Parse a combined address string into street, city, state/province, and postal code.
    
    Handles both US (ZIP code) and Canadian (Postal Code) formats.
    
    Args:
        address_text: Combined address string
        
    Returns:
        Tuple of (street, city, state, postal_code)
    """
    street, city, state, postal_code = "", "", "", ""

    # Regex patterns for postal codes
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


def extract_phone_number(text: str) -> str:
    """
    Extract phone number from text.
    
    Args:
        text: Text that may contain a phone number
        
    Returns:
        Extracted phone number or empty string
    """
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    match = re.search(phone_pattern, text)
    return match.group() if match else ""


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove common unwanted characters
    text = re.sub(r'[^\w\s\-.,()#&]', '', text)
    
    return text


def normalize_for_comparison(text: str) -> str:
    """
    Normalize text for comparison purposes (deduplication, etc.).
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text for comparison
    """
    if not text:
        return ""
    
    return re.sub(r'\s+', ' ', text).strip().lower()


def extract_directory_links(html: str, base_url: str, patterns: list = None) -> list:
    """
    Extract subpage links from a directory page using pattern matching.
    
    Args:
        html: HTML content to parse
        base_url: Base URL for relative links
        patterns: List of URL patterns to match (optional)
        
    Returns:
        List of extracted URLs
    """
    from bs4 import BeautifulSoup
    from config.settings import Constants
    
    if patterns is None:
        patterns = Constants.DIRECTORY_PATTERNS
    
    soup = BeautifulSoup(html, "html.parser")
    links = []
    
    # Look for anchor tags in common directory containers
    containers = soup.select(
        "div.af-location-container, .locations-directory, .state-list, "
        ".make-list, .location-list, .dealer-directory, .directory-list"
    )
    if not containers:
        containers = [soup]  # fallback: search whole page
    
    for container in containers:
        for a in container.find_all("a", href=True):
            href = a["href"]
            if href.startswith("#") or href.startswith("javascript"):
                continue
            
            # Only add links that look like subpages
            if any(pattern in href for pattern in patterns):
                if href.startswith("http"):
                    links.append(href)
                elif href.startswith("/"):
                    base = base_url.split("/")[0] + "//" + base_url.split("/")[2]
                    links.append(base + href)
                else:
                    # relative path
                    links.append(base_url.rstrip("/") + "/" + href)
    
    # Remove duplicates and return reasonable number of links
    links = list(dict.fromkeys(links))
    if 3 <= len(links) <= 100:
        return links
    return []