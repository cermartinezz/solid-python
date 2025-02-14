from dotenv import load_dotenv

from src.payment_service.builders.builders import PaymentServiceBuilder
from src.payment_service.commons import CustomerData, ContactInfo, PaymentData
from src.payment_service.commons.payment_data import PaymentType
from src.payment_service.loggers import TransactionLogger
from src.payment_service.notifiers import EmailNotifier, SMSNotifier, NotifierProtocol
from src.payment_service.processors import (
    StripePaymentProcessor,
    OfflinePaymentProcessor,
)
from src.payment_service.service import PaymentService
from src.payment_service.validators import CustomerValidator, PaymentDataValidator

_ = load_dotenv()


def get_email_notifier() -> EmailNotifier:
    return EmailNotifier()


def get_sms_notifier() -> SMSNotifier:
    sms_gateway = "YourSMSService"
    return SMSNotifier(sms_gateway)


def get_notifier_implementation(customer_data: CustomerData) -> NotifierProtocol:
    if customer_data.contact_info.phone:
        return get_sms_notifier()
    if customer_data.contact_info.email:
        return get_email_notifier()
    else:
        raise ValueError("No valid contact info provided")


def get_customer_data() -> CustomerData:
    customer_data_with_phone = CustomerData(
        name="Jane Doe", contact_info=ContactInfo(phone="1234567890")
    )

    return customer_data_with_phone


if __name__ == "__main__":
    # Set up the payment processors
    stripe_processor = StripePaymentProcessor()
    offline_processor = OfflinePaymentProcessor()
    customer_validator = CustomerValidator()
    payment_validator = PaymentDataValidator()
    logger = TransactionLogger()

    # Set up the customer data and payment data
    customer_data_with_email = CustomerData(
        name="John Doe", contact_info=ContactInfo(email="john@example.com")
    )
    customer_data_with_phone = CustomerData(
        name="Jane Doe", contact_info=ContactInfo(phone="1234567890")
    )

    # Set up the payment data
    payment_data = PaymentData(amount=100, source="tok_visa")

    # Set up the notifiers
    email_notifier = EmailNotifier()

    sms_gateway = "YourSMSService"
    sms_notifier = SMSNotifier(sms_gateway)

    # # Using Stripe processor with email notifier
    payment_service_email = PaymentService(
        payment_processor=stripe_processor,
        notifier=email_notifier,
        customer_validator=customer_validator,
        payment_validator=payment_validator,
        logger=logger,
        refund_processor=stripe_processor,
        recurring_processor=stripe_processor,
    )

    payment_service_email.process_transaction(customer_data_with_email, payment_data)

    # Using Stripe processor with SMS notifier
    payment_service_sms = PaymentService(
        payment_processor=stripe_processor,
        notifier=sms_notifier,
        customer_validator=customer_validator,
        payment_validator=payment_validator,
        logger=logger,
    )
    sms_payment_response = payment_service_sms.process_transaction(
        customer_data_with_phone, payment_data
    )

    # Example of processing a refund using Stripe processor
    transaction_id_to_refund = sms_payment_response.transaction_id
    if transaction_id_to_refund:
        payment_service_email.process_refund(transaction_id_to_refund)

    # Using offline processor with email notifier
    offline_payment_service = PaymentService(
        payment_processor=offline_processor,
        notifier=email_notifier,
        customer_validator=customer_validator,
        payment_validator=payment_validator,
        logger=logger,
    )
    offline_payment_response = offline_payment_service.process_transaction(
        customer_data_with_email, payment_data
    )

    # Attempt to refund using offline processor (will fail)
    try:
        if offline_payment_response.transaction_id:
            offline_payment_service.process_refund(
                offline_payment_response.transaction_id
            )
    except Exception as e:
        print(f"Refund failed and PaymentService raised an exception: {e}")

    # Attempt to set up recurring payment using offline processor (will fail)
    try:
        offline_payment_service.setup_recurring(customer_data_with_email, payment_data)

    except Exception as e:
        print(
            f"Recurring payment setup failed and PaymentService raised an exception {e}"
        )

    try:
        error_payment_data = PaymentData(amount=100, source="tok_radarBlock")
        payment_service_email.process_transaction(
            customer_data_with_email, error_payment_data
        )
    except Exception as e:
        print(f"Payment failed and PaymentService raised an exception: {e}")

    # Set up recurrence
    recurring_payment_data = PaymentData(amount=100, source="pm_card_visa")
    payment_service_email.setup_recurring(
        customer_data_with_email, recurring_payment_data
    )

    # implementation of Strategy pattern
    print(
        "-----------------------------------------------------------------------------"
    )
    print(
        "-----------------------------Using Strategy pattern--------------------------"
    )
    print(
        "-----------------------------------------------------------------------------"
    )
    customer_data = get_customer_data()
    dynamic_notifier = get_notifier_implementation(customer_data)

    payment_service = PaymentService(
        payment_processor=stripe_processor,
        notifier=dynamic_notifier,
        customer_validator=customer_validator,
        payment_validator=payment_validator,
        logger=logger,
        refund_processor=stripe_processor,
        recurring_processor=stripe_processor,
    )
    print("Processing transaction with dynamic notifier")
    payment_service.process_transaction(customer_data, payment_data)

    # implementation of Factory pattern
    print(
        "-----------------------------------------------------------------------------"
    )
    print(
        "-----------------------------Using Factory pattern---------------------------"
    )
    print(
        "-----------------------------------------------------------------------------"
    )
    print("Processing transaction with factory pattern using Stripe processor")
    print("payment_service", payment_service)
    payment_data = PaymentData(amount=100, source="tok_visa", currency="USD")
    payment_service = PaymentService.create_with_payment_processor(
        payment_data,
        notifier=dynamic_notifier,
        customer_validator=customer_validator,
        payment_validator=payment_validator,
        logger=logger,
    )

    payment_service.process_transaction(customer_data, payment_data)

    payment_data = PaymentData(
        amount=100, source="tok_visa", currency="USD", type=PaymentType.OFFLINE
    )
    payment_service = PaymentService.create_with_payment_processor(
        payment_data,
        notifier=dynamic_notifier,
        customer_validator=customer_validator,
        payment_validator=payment_validator,
        logger=logger,
    )
    print("Processing transaction with factory pattern using Offline processor")
    print("payment_service", payment_service)
    payment_service.process_transaction(customer_data, payment_data)

    payment_data = PaymentData(amount=100, source="tok_visa", currency="CAD")
    payment_service = PaymentService.create_with_payment_processor(
        payment_data,
        notifier=dynamic_notifier,
        customer_validator=customer_validator,
        payment_validator=payment_validator,
        logger=logger,
    )
    print("Processing transaction with factory pattern using Local processor")
    print("payment_service", payment_service)
    payment_service.process_transaction(customer_data, payment_data)

    # Builder Pattern
    print(
        "-----------------------------------------------------------------------------"
    )
    print("-----------------------------Using Build pattern---------------------------")
    print(
        "-----------------------------------------------------------------------------"
    )

    service = (
        PaymentServiceBuilder()
        .set_logger()
        .set_payment_validator()
        .set_customer_validator()
        .set_payment_processor(payment_data)
        .set_notifier(customer_data)
        .build()
    )

    print("Processing transaction with build pattern")
    payment_service.process_transaction(customer_data, payment_data)
