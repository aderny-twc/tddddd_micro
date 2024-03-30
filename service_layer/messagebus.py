from domain import events
from typing import Callable


class FakeEmailSender:
    @staticmethod
    def send_mail(address: str, message: str) -> None:
        print("Send message to: ", address, ". Message: ", message)


def send_out_of_stock_notification(event: events.OutOfStock):
    email_sender = FakeEmailSender()
    email_sender.send_mail(
        "stock@made.com",
        f"SKU {event.sku} out of stock",
    )


def handle(event: events.Event):
    for handler in HANDLERS[type[event]]:
        handler(event)


HANDLERS: dict[type[events.Event], list[Callable]] = {
    events.OutOfStock: [send_out_of_stock_notification],
}
