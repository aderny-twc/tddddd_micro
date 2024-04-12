import json

from tests.e2e import api_client, redis_client
from tests.utils import random_orderid, random_sku, random_batchref
from tenacity import Retrying, stop_after_delay


def test_change_batch_quantity_leading_to_reallocation():
    # Create two batches and order
    orderid, sku = random_orderid(), random_sku()
    earlier_batch, later_batch = random_batchref("early"), random_batchref("later")

    api_client.post_to_add_batch(earlier_batch, sku, qty=10, eta="2024-04-05")
    api_client.post_to_add_batch(later_batch, sku, qty=10, eta="2024-04-06")

    api_client.post_to_allocate(orderid, sku, 10)

    subscription = redis_client.subscribe_to("line_allocated")

    # Change product quantity in batch
    redis_client.publish_message("change_batch_quantity", {"batchref": earlier_batch, "qty": 5})

    # Wait until we get message about allocation
    messages = []
    for attempt in Retrying(stop=stop_after_delay(3), reraise=True):
        with attempt:
            message = subscription.get_message(timeout=1)
            if message:
                messages.append(message)
                print(message)
            data = json.loads(messages[-1]["data"])
            assert data["orderid"] == orderid
            assert data["batchref"] == later_batch
