from src.payment_service.commons import CustomerData, PaymentData, PaymentResponse
from src.payment_service.processors.payment import PaymentProcessorProtocol


class OfflinePaymentProcessor(PaymentProcessorProtocol):
    def process_transaction(
            self, customer_data: CustomerData, payment_data: PaymentData
    ) -> PaymentResponse:
        print("Processing offline payment for", customer_data.name)
        return PaymentResponse(
            status="success",
            amount=payment_data.amount,
            transaction_id=None,
            message="Offline payment success",
        )
