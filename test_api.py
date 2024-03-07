import uuid
import requests

import config


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name: str | int = ""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name: str | int = ""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name: str | int = ""):
    return f"order-{name}-{random_suffix()}"


def test_api_returns_allocations(restart_api, add_stock):
    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)

    add_stock([
        (laterbatch, sku, 100, "2024-03-08"),
        (earlybatch, sku, 100, "2024-03-07"),
        (otherbatch, sku, 100, None),
    ])

    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}
    url = config.get_api_url()

    r = requests.post(f"{url}/allocate", json=data)

    assert r.status_code == 201
    assert r.json()["batchref"] == otherbatch



