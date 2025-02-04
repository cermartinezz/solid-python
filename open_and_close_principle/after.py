import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

import stripe
from dotenv import load_dotenv
from pydantic import BaseModel
from stripe import Charge
from stripe.error import StripeError

_ = load_dotenv()


class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None


class CustomerData(BaseModel):
    name: str
    contact_info: ContactInfo


class PaymentData(BaseModel):
    amount: int
    source: str


@dataclass
class CustomerValidator:
    def validate(self, customer_data: CustomerData):
        # validation responsibilities
        if not customer_data.name:
            print("Invalid customer data: missing name")
            raise ValueError("Invalid customer data: missing name")

        if not customer_data.contact_info:
            print("Invalid customer data: missing contact info")
            raise ValueError("Invalid customer data: missing contact info")

        if (
                not customer_data.contact_info.email
                and not customer_data.contact_info.phone
        ):
            print("Invalid customer data: missing email or phone")
            raise ValueError("Invalid customer data: missing email or phone")


@dataclass
class PaymentDataValidator:
    def validate(self, transaction_data: PaymentData):
        # validation responsibilities
        if not transaction_data.source:
            print("Invalid payment data")
            raise ValueError("Invalid payment data")


class PaymentProcessor(ABC):
    @abstractmethod
    def process_transaction(
            self, customer_data: CustomerData, transaction_data: PaymentData
    ) -> Charge:
        pass


@dataclass
class StripePaymentProcessor(PaymentProcessor):

    def process_transaction(
            self, customer_data: CustomerData, transaction_data: PaymentData
    ) -> Charge:

        stripe.api_key = os.getenv("STRIPE_API_KEY")

        # payment processing responsibilities
        try:
            charge = stripe.Charge.create(
                amount=transaction_data.amount,
                currency="usd",
                source=transaction_data.source,
                description="Charge for " + customer_data.name,
            )
            print("Payment successful")
        except StripeError as e:
            print("Payment failed:", e)
            raise e

        return charge


class Notifier(ABC):
    @abstractmethod
    def send_confirmation(self, customer_data: CustomerData):
        pass


@dataclass
class EmailNotifier(Notifier):
    # notification responsibilities
    def send_confirmation(self, customer_data: CustomerData):
        from email.mime.text import MIMEText

        msg = MIMEText("Thank you for your payment.")
        msg["Subject"] = "Payment Confirmation"
        msg["From"] = "no-reply@example.com"
        msg["To"] = customer_data.contact_info.email

        print("Email sent to", customer_data.contact_info.email)


class SMSNotifier(Notifier):
    def send_confirmation(self, customer_data: CustomerData):
        phone_number = customer_data.contact_info.phone
        sms_gateway = "the custom SMS Gateway"
        print(
            f"send the sms using {sms_gateway}: SMS sent to {phone_number}: Thank you for your payment."
        )


@dataclass
class TransactionLogger:
    def log(self, customer_data: CustomerData, transaction_data: PaymentData, charge):
        # logging responsibilities
        with open("transactions.log", "a") as log_file:
            log_file.write(f"{customer_data.name} paid {transaction_data.amount}\n")
            log_file.write(f"Payment status: {charge['status']}\n")


@dataclass
class PaymentService:
    customer_validator = CustomerValidator()
    payment_validator = PaymentDataValidator()
    payment_processor: PaymentProcessor = field(default_factory=StripePaymentProcessor)
    notifier: Notifier = field(default_factory=EmailNotifier)
    logger = TransactionLogger()

    def process_transaction(
            self, customer_data: CustomerData, transaction_data: PaymentData
    ) -> Charge:
        self.customer_validator.validate(customer_data)
        self.payment_validator.validate(transaction_data)

        try:
            charge = self.payment_processor.process_transaction(
                customer_data, transaction_data
            )
            self.notifier.send_confirmation(customer_data)
            self.logger.log(customer_data, transaction_data, charge)
            return charge
        except StripeError as e:
            raise ValueError("Payment failed:", e)


if __name__ == "__main__":
    sms_notifier = SMSNotifier()
    payment_processor = PaymentService()

    customer_data_with_email = CustomerData(
        name="John Doe", contact_info=ContactInfo(email="cesar@martinez.com")
    )
    customer_data_with_phone = CustomerData(
        name="Jane Doe", contact_info=ContactInfo(phone="123123123123")
    )

    payment_data = PaymentData(amount=500, source="tok_mastercard")

    payment_processor.process_transaction(customer_data_with_email, payment_data)
    payment_processor.process_transaction(customer_data_with_phone, payment_data)

    try:
        payment_data = PaymentData(amount=500, source="tok_radarBlock")

        payment_processor.process_transaction(customer_data_with_phone, payment_data)
    except ValueError as e:
        print("Payment failed: {e}")
