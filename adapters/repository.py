import abc
from domain import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, product: model.Product):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, sku: str) -> model.Product:
        raise NotImplementedError

    # @abc.abstractmethod
    # def list(self) -> list[model.Batch]:
    #     raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, product):
        self.session.add(product)

    def get(self, sku):
        return self.session.query(model.Product).filter_by(sku=sku).first()

    # def list(self):
    #     return self.session.query(model.Product).all()


class FakeRepository(AbstractRepository):
    def __init__(self, products):
        self._products = set(products)

    def add(self, product):
        self._products.add(product)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    # def list(self):
    #     return list(self._batches)
