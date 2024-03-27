import uuid


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name: str | int = ""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name: str | int = ""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name: str | int = ""):
    return f"order-{name}-{random_suffix()}"
