from tests.e2e import api_client
from tests.e2e.api_client import post_to_add_batch
from tests.utils import random_sku, random_batchref, random_orderid


def test_success_path_returns_202_and_batch_is_allocated(restart_api, postgres_db):
    orderid = random_orderid()
    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    post_to_add_batch(laterbatch, sku, 100, "2011-01-02")
    post_to_add_batch(earlybatch, sku, 100, "2011-01-01")
    post_to_add_batch(otherbatch, othersku, 100, None)

    r = api_client.post_to_allocate(orderid, sku, qty=3)
    assert r.status_code == 202

    r = api_client.get_allocation(orderid)
    assert r.ok
    assert r.json() == [
        {"sku": sku, "batchref": earlybatch}
    ]


def test_fail_path_returns_400_and_error_message(restart_api, postgres_db):
    unknown_sku, orderid = random_sku(), random_orderid()
    r = api_client.post_to_allocate(
        orderid, unknown_sku, qty=20, expect_success=False
    )
    assert r.status_code == 400
    assert r.json()["message"] == f"Wrong sku {unknown_sku}"

    r = api_client.get_allocation(orderid)
    assert r.status_code == 404
