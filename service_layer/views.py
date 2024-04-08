from sqlalchemy import text

from service_layer import unit_of_work


def allocations(orderid: str, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = list(
            uow.session.execute(
                text(
                    "SELECT ol.sku, b.reference"
                    " FROM allocations as a"
                    " JOIN batches AS b ON a.batch_id = b.id"
                    " JOIN order_lines AS ol ON a.orderline_id = ol.id"
                    " WHERE ol.orderid = :orderid"
                ),
                dict(orderid=orderid)
            )
        )

    return [
        {"sku": sku, "batchref": batchref} for sku, batchref in results
    ]
