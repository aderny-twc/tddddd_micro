import abc
from domain import model


class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen: set[model.Product] = set()

    def add(self, product: model.Product):
        self._add(product)
        self.seen.add(product)

    @abc.abstractmethod
    def _add(self, product: model.Product):
        raise NotImplementedError

    def get(self, sku: str) -> model.Product:
        product = self._get(sku)
        if product:
            self.seen.add(product)
        return product

    @abc.abstractmethod
    def _get(self, sku) -> model.Product:
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
            product.events = []
            return product

    # def list(self):
    #     return self.session.query(model.Product).all()
