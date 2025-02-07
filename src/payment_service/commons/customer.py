from typing import Optional

from pydantic import BaseModel

from src.payment_service.commons import ContactInfo


class CustomerData(BaseModel):
    name: str
    contact_info: ContactInfo
    customer_id: Optional[str] = None
