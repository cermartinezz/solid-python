from dataclasses import dataclass
from typing import Optional

from src.payment_service.loggers import TransactionLogger
from src.payment_service.notifiers import NotifierProtocol
from src.payment_service.processors import (
    PaymentProcessorProtocol,
    RecurringPaymentProtocol,
    RefundPaymentProtocol,
)
from src.payment_service.validators import CustomerValidator, PaymentDataValidator
from .commons import CustomerData, PaymentData, PaymentResponse


@dataclass
class PaymentService:
    payment_processor: PaymentProcessorProtocol
    notifier: NotifierProtocol
    customer_validator: CustomerValidator
    payment_validator: PaymentDataValidator
    logger: TransactionLogger
    recurring_processor: Optional[RecurringPaymentProtocol] = None
    refund_processor: Optional[RefundPaymentProtocol] = None

    def process_transaction(
            self, customer_data: CustomerData, payment_data: PaymentData
    ) -> PaymentResponse:
        self.customer_validator.validate(customer_data)
        self.payment_validator.validate(payment_data)
        payment_response = self.payment_processor.process_transaction(
            customer_data, payment_data
        )
        self.notifier.send_confirmation(customer_data)
        self.logger.log_transaction(customer_data, payment_data, payment_response)
        return payment_response

    def process_refund(self, transaction_id: str):
        if not self.refund_processor:
            raise ValueError("this processor does not support refunds")

        refund_response = self.refund_processor.refund_payment(transaction_id)
        self.logger.log_refund(transaction_id, refund_response)
        return refund_response

    def setup_recurring(self, customer_data: CustomerData, payment_data: PaymentData):
        if not self.recurring_processor:
            raise ValueError("this processor does not support recurring")
        recurring_response = self.recurring_processor.setup_recurring_payment(
            customer_data, payment_data
        )
        self.logger.log_transaction(customer_data, payment_data, recurring_response)
        return recurring_response
