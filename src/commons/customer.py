from typing import Optional

from pydantic import BaseModel

from src.commons import ContactInfo


class CustomerData(BaseModel):
    name: str
    contact_info: ContactInfo
    customer_id: Optional[str] = None
