from typing import Protocol

from src.payment_service.commons import CustomerData, PaymentData, PaymentResponse


class RecurringPaymentProtocol(Protocol):
    def setup_recurring_payment(
            self, customer_data: CustomerData, payment_data: PaymentData
    ) -> PaymentResponse: ...
