from src.payment_service.commons import PaymentData
from src.payment_service.commons.payment_data import PaymentType
from src.payment_service.processors import (
    PaymentProcessorProtocol,
    LocalPaymentProcessor,
    StripePaymentProcessor,
    OfflinePaymentProcessor,
)


class PaymentProcessorFactory:

    @staticmethod
    def create_payment_processor(payment_data: PaymentData) -> PaymentProcessorProtocol:
        match payment_data.type:
            case PaymentType.OFFLINE:
                return OfflinePaymentProcessor()
            case PaymentType.ONLINE:
                match payment_data.currency:
                    case "USD":
                        return StripePaymentProcessor()
                    case _:
                        return LocalPaymentProcessor()
            case _:
                raise ValueError("Invalid payment type")
