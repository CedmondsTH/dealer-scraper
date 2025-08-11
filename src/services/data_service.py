"""
Data processing and transformation service.

This service handles all data processing operations including
validation, cleaning, transformation, and export formatting.
"""

import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from io import BytesIO

from ..utils.data_cleaner import data_cleaner
from ..utils.address_parser import address_parser


class DataService:
    """Service for data processing and transformation operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_dealer_data(self, raw_dealers: List[Dict[str, Any]], 
                          dealer_group: str) -> List[Dict[str, Any]]:
        """
        Process raw dealer data into standardized format.
        
        Args:
            raw_dealers: List of raw dealer dictionaries
            dealer_group: Name of the dealer group
            
        Returns:
            List of processed and standardized dealer records
        """
        try:
            self.logger.info(f"Processing {len(raw_dealers)} raw dealer records")
            
            # Step 1: Filter valid dealerships
            valid_dealers = [d for d in raw_dealers if data_cleaner.is_valid_dealership(d)]
            self.logger.info(f"Valid dealerships after filtering: {len(valid_dealers)}")
            
            # Step 2: Deduplicate
            unique_dealers = data_cleaner.deduplicate_dealers(valid_dealers)
            self.logger.info(f"Unique dealerships after deduplication: {len(unique_dealers)}")
            
            # Step 3: Standardize and enrich data
            processed_dealers = []
            for dealer in unique_dealers:
                processed_dealer = self._standardize_dealer_record(dealer, dealer_group)
                if processed_dealer:
                    processed_dealers.append(processed_dealer)
            
            self.logger.info(f"Final processed dealers: {len(processed_dealers)}")
            return processed_dealers
            
        except Exception as e:
            self.logger.error(f"Error processing dealer data: {str(e)}", exc_info=True)
            return []
    
    def _standardize_dealer_record(self, dealer: Dict[str, Any], 
                                 dealer_group: str) -> Optional[Dict[str, Any]]:
        """Standardize a single dealer record."""
        try:
            # Extract and clean basic info (handle both capitalized and lowercase keys)
            name = data_cleaner.normalize_name(dealer.get("name", "") or dealer.get("Name", ""))
            if not name:
                return None
            
            # Process address (handle both capitalized and lowercase keys)
            street = dealer.get("street", "") or dealer.get("Street", "")
            city = data_cleaner.normalize_city(dealer.get("city", "") or dealer.get("City", ""))
            state = (dealer.get("state", "") or dealer.get("State", "")).strip().upper()
            zip_code = (dealer.get("zip", "") or dealer.get("Zip", "")).strip()
            
            # Normalize address
            if street:
                street = address_parser.normalize_address_abbreviations(street)
            
            # Extract contact info (handle both capitalized and lowercase keys)
            phone = data_cleaner.extract_phone_number(dealer.get("phone", "") or dealer.get("Phone", ""))
            website = data_cleaner.normalize_website(dealer.get("website", "") or dealer.get("Website", ""))
            
            # Classify and enrich
            dealer_type = data_cleaner.classify_dealer_type(name)
            car_brands = data_cleaner.extract_car_brands(name)
            country = data_cleaner.determine_country(state)
            
            return {
                "Dealership": name,
                "Dealer Group": dealer_group,
                "Dealership Type": dealer_type,
                "Car Brand": car_brands,
                "Address": street,
                "City": city,
                "State/Province": state,
                "Postal Code": zip_code,
                "Phone": phone,
                "Country": country,
                "Website": website
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to standardize dealer record: {str(e)}")
            return None
    
    def create_dataframe(self, dealers: List[Dict[str, Any]]) -> pd.DataFrame:
        """Create a pandas DataFrame from dealer data."""
        if not dealers:
            return pd.DataFrame()
        
        df = pd.DataFrame(dealers)
        
        # Ensure column order
        desired_order = [
            "Dealership", "Dealer Group", "Dealership Type", "Car Brand", 
            "Address", "City", "State/Province", "Postal Code", 
            "Phone", "Country", "Website"
        ]
        
        # Only include columns that exist
        existing_cols = [col for col in desired_order if col in df.columns]
        other_cols = [col for col in df.columns if col not in existing_cols]
        
        return df[existing_cols + other_cols]
    
    def export_to_excel(self, dealers: List[Dict[str, Any]], 
                       filename: Optional[str] = None) -> BytesIO:
        """Export dealer data to Excel format."""
        df = self.create_dataframe(dealers)
        
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Dealer Locations")
        
        buffer.seek(0)
        return buffer
    
    def export_to_csv(self, dealers: List[Dict[str, Any]]) -> str:
        """Export dealer data to CSV format."""
        df = self.create_dataframe(dealers)
        return df.to_csv(index=False)
    
    def deduplicate_dealers(self, dealers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate dealer records."""
        return data_cleaner.deduplicate_dealers(dealers)