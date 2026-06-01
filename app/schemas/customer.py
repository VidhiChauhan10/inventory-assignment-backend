from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is not None:
            cleaned = re.sub(r"[\s\-\(\)\+]", "", v)
            if not cleaned.isdigit() or len(cleaned) < 7 or len(cleaned) > 15:
                raise ValueError("Phone must contain 7-15 digits")
        return v


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is not None:
            cleaned = re.sub(r"[\s\-\(\)\+]", "", v)
            if not cleaned.isdigit() or len(cleaned) < 7 or len(cleaned) > 15:
                raise ValueError("Phone must contain 7-15 digits")
        return v


class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
