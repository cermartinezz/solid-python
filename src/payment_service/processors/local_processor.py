import uuid

from src.payment_service.commons import PaymentResponse
from src.payment_service.processors.payment import PaymentProcessorProtocol
from src.payment_service.processors.recurring import RecurringPaymentProtocol
from src.payment_service.processors.refunds import RefundPaymentProtocol


class LocalPaymentProcessor(
    PaymentProcessorProtocol, RefundPaymentProtocol, RecurringPaymentProtocol
):
    def process_transaction(self, customer_data, payment_data):
        print("Processing payment locally", customer_data.name)
        transaction_id = f"local-transaction-id-{uuid.UUID}"
        return PaymentResponse(
            status="success",
            amount=payment_data.amount,
            transaction_id=transaction_id,
            message="Payment successful",
        )

    def refund_payment(self, transaction_id):
        print("Refunding payment locally for transaction id", transaction_id)
        return PaymentResponse(
            status="success",
            amount=0,
            transaction_id=transaction_id,
            message="Refund successful",
        )

    def setup_recurring_payment(self, customer_data, payment_data):
        print("Setting up recurring payment locally")
        return PaymentResponse(
            status="success",
            amount=payment_data.amount,
            transaction_id=None,
            message="Recurring payment successful",
        )
