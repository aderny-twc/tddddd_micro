from sqlalchemy import text

from service_layer import unit_of_work


def allocations(orderid: str, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = list(
            uow.session.execute(
                text(
                    "SELECT sku, batchref from allocations_view"
                    " WHERE orderid = :orderid"
                ),
                dict(orderid=orderid),
            )
        )

    return [{"sku": sku, "batchref": batchref} for sku, batchref in results]
