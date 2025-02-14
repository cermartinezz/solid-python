from src.payment_service.commons import CustomerData
from src.payment_service.notifiers import SMSNotifier, EmailNotifier, NotifierProtocol


class NotifierFactory:
    @staticmethod
    def create_notifier(customer_data: CustomerData) -> NotifierProtocol:
        if customer_data.contact_info.phone:
            return SMSNotifier("YourSMSService")
        if customer_data.contact_info.email:
            return EmailNotifier()
        else:
            raise ValueError("No valid contact info provided")
