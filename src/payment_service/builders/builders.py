from dataclasses import dataclass
from typing import Optional, Self

from src.payment_service.commons import PaymentData, CustomerData
from src.payment_service.factories.notifier_factory import NotifierFactory
from src.payment_service.factories.payment_processor_factory import (
    PaymentProcessorFactory,
)
from src.payment_service.loggers import TransactionLogger
from src.payment_service.notifiers import NotifierProtocol
from src.payment_service.processors import (
    PaymentProcessorProtocol,
    RecurringPaymentProtocol,
    RefundPaymentProtocol,
)
from src.payment_service.service import PaymentService
from src.payment_service.validators import CustomerValidator, PaymentDataValidator


@dataclass
class PaymentServiceBuilder:
    payment_processor: Optional[PaymentProcessorProtocol] = None
    notifier: Optional[NotifierProtocol] = None
    customer_validator: Optional[CustomerValidator] = None
    payment_validator: Optional[PaymentDataValidator] = None
    logger: Optional[TransactionLogger] = None
    recurring_processor: Optional[RecurringPaymentProtocol] = None
    refund_processor: Optional[RefundPaymentProtocol] = None

    def set_logger(self) -> Self:
        self.logger = TransactionLogger()
        return self

    def set_payment_validator(self) -> Self:
        self.payment_validator = PaymentDataValidator()
        return self

    def set_customer_validator(self) -> Self:
        self.customer_validator = CustomerValidator()
        return self

    def set_payment_processor(self, payment_data: PaymentData) -> Self:
        self.payment_processor = PaymentProcessorFactory.create_payment_processor(
            payment_data
        )
        return self

    def set_notifier(self, customer_data: CustomerData) -> Self:
        self.notifier = NotifierFactory.create_notifier(customer_data)
        return self

    def build(self):
        if not all(
                [
                    self.payment_processor,
                    self.notifier,
                    self.customer_validator,
                    self.payment_validator,
                    self.logger,
                ]
        ):
            missing = [
                name
                for name, value in [
                    ("payment_processor", self.payment_processor),
                    ("notifier", self.notifier),
                    ("customer_validator", self.customer_validator),
                    ("payment_validator", self.payment_validator),
                    ("logger", self.logger),
                ]
                if value is None
            ]
            raise ValueError(f"Missing values for {missing}")

        return PaymentService(
            payment_validator=self.payment_validator,
            customer_validator=self.customer_validator,
            logger=self.logger,
            notifier=self.notifier,
            payment_processor=self.payment_processor,
            refund_processor=self.refund_processor,
            recurring_processor=self.recurring_processor,
        )
