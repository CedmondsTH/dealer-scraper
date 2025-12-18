"""
Data models for the Dealer Scraper application.
Uses Pydantic for robust data validation and type safety.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Dealer(BaseModel):
    """
    Represents a standardized dealer location.
    """

    name: str = Field(..., alias="Dealership")
    group: str = Field(..., alias="Dealer Group")
    type: str = Field("Unknown", alias="Dealership Type")
    brands: str = Field("", alias="Car Brand")
    address: str = Field(..., alias="Address")
    city: str = Field(..., alias="City")
    state: str = Field(..., alias="State/Province")
    zip_code: str = Field(..., alias="Postal Code")
    phone: str = Field("", alias="Phone")
    country: str = Field("United States of America", alias="Country")
    website: str = Field("", alias="Website")

    model_config = {"populate_by_name": True, "extra": "ignore"}

    @field_validator("state")
    @classmethod
    def uppercase_state(cls, v: str) -> str:
        return v.strip().upper() if v else v

    @field_validator("website")
    @classmethod
    def clean_website(cls, v: str) -> str:
        if not v:
            return ""
        return v.strip()
