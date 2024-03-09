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
        (otherbatch, othersku, 100, None),
    ])

    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}
    url = config.get_api_url()

    r = requests.post(f"{url}/allocate", json=data)

    assert r.status_code == 201
    assert r.json()["batchref"] == earlybatch


def test_allocations_are_persisted(restart_api, add_stock):
    sku = random_sku()
    batch1, batch2 = random_batchref(1), random_batchref(2)
    order1, order2 = random_orderid(1), random_orderid(2)

    add_stock([
        (batch1, sku, 10, "2024-03-07"),
        (batch2, sku, 10, "2024-03-08"),
    ])

    line1 = {"orderid": order1, "sku": sku, "qty": 10}
    line2 = {"orderid": order2, "sku": sku, "qty": 10}
    url = config.get_api_url()

    # Empty batch
    r = requests.post(f"{url}/allocate", json=line1)
    assert r.status_code == 201
    assert r.json()["batchref"] == batch1

    # Second order has to be in batch2
    r = requests.post(f"{url}/allocate", json=line2)
    assert r.status_code == 201
    assert r.json()["batchref"] == batch2


def test_400_message_for_out_of_stock(restart_api, add_stock):
    sku, smalL_batch, large_order = random_sku(), random_batchref(), random_orderid()
    add_stock([
        (smalL_batch, sku, 10, '2011-01-01'),
    ])
    data = {'orderid': large_order, 'sku': sku, 'qty': 20}
    url = config.get_api_url()

    r = requests.post(f'{url}/allocate', json=data)

    assert r.status_code == 400
    assert r.json()['message'] == f"Product with vendor code {sku} out of stock"


def test_400_message_for_invalid_sku(restart_api):
    unknown_sku, orderid = random_sku(), random_orderid()
    data = {'orderid': orderid, 'sku': unknown_sku, 'qty': 20}
    url = config.get_api_url()

    r = requests.post(f'{url}/allocate', json=data)

    assert r.status_code == 400
    assert r.json()['message'] == f"Wrong sku {unknown_sku}"


def test_happy_path_returns_201_and_allocated_batch(restart_api, add_stock):
    sku, othersku = random_sku(), random_sku('other')
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    add_stock([
        (laterbatch, sku, 100, '2024-03-08'),
        (earlybatch, sku, 100, '2024-03-07'),
        (otherbatch, othersku, 100, None),
    ])
    data = {'orderid': random_orderid(), 'sku': sku, 'qty': 3}

    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)

    assert r.status_code == 201
    assert r.json()['batchref'] == earlybatch


def test_unhappy_path_returns_400_and_error_message(restart_api):
    unknown_sku, orderid = random_sku(), random_orderid()
    data = {'orderid': orderid, 'sku': unknown_sku, 'qty': 20}
    url = config.get_api_url()

    r = requests.post(f'{url}/allocate', json=data)

    assert r.status_code == 400
    assert r.json()['message'] == f"Wrong sku {unknown_sku}"