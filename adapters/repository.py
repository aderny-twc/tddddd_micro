import abc

from adapters import orm
from domain import model


class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen: set[model.Product] = set()

    def add(self, product: model.Product):
        product.events = []
        self._add(product)
        self.seen.add(product)

    @abc.abstractmethod
    def _add(self, product: model.Product):
        raise NotImplementedError

    def get(self, sku: str) -> model.Product:
        product = self._get(sku)
        if product:
            product.events = []
            self.seen.add(product)
        return product

    @abc.abstractmethod
    def _get(self, sku) -> model.Product:
        raise NotImplementedError

    def get_by_batchref(self, batchref: str) -> model.Product:
        product = self._get_by_batchref(batchref)
        if product:
            product.events = []
            self.seen.add(product)
        return product

    @abc.abstractmethod
    def _get_by_batchref(self, batchref: str) -> model.Product:
        raise NotImplementedError

    # @abc.abstractmethod
    # def list(self) -> list[model.Batch]:
    #     raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, product):
        self.session.add(product)

    def _get(self, sku):
        product = (
            self.session
            .query(model.Product)
            .filter_by(sku=sku)
            .with_for_update()
            .first()
        )
        if product:
            return product

    def _get_by_batchref(self, batchref: str) -> model.Product:
        return (
            self.session.query(model.Product)
            .join(model.Batch)
            .filter(orm.batches.c.reference == batchref)
            .first()
        )

    # def list(self):
    #     return self.session.query(model.Product).all()
