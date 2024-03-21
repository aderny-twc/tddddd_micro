from dataclasses import dataclass
from datetime import date


@dataclass(unsafe_hash=True)  # avoid errors sqlalchemy mapping (cause ID)
class OrderLine:
    orderid: str
    sku: str
    qty: int


class Batch:  # Партия товара
    def __init__(self, ref: str, sku: str, qty: int, eta: date | None) -> None:
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations = set()  # Order lines in the batch

    def allocate(self, line: OrderLine) -> None:
        """Order line allocation"""
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine) -> None:
        """Remove order line from batch"""
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        """Calculate all order lines qty"""
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other: "Batch") -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return True

        return self.eta > other.eta

    def __repr__(self):
        return f"<{self.sku} | {self.reference} | {self.eta}>"


class Product:
    def __init__(self, sku: str, batches: list[Batch]):
        # Главный идентификатор продукта
        self.sku = sku
        # Коллекция партий артикула
        self.batches = batches

    # Переместим службу предметной области
    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(
                b for b in sorted(self.batches) if b.can_allocate(line)
            )
            batch.allocate(line)
            return batch.reference
        except StopIteration:
            raise OutOfStock(f"Product with vendor code {line.sku} out of stock")


class OutOfStock(Exception):
    pass


def allocate(line: OrderLine, batches: list[Batch]) -> str:
    try:
        batch = next(
            b for b in sorted(batches) if b.can_allocate(line)
        )
    except StopIteration:
        raise OutOfStock(f"Product with vendor code {line.sku} out of stock")

    batch.allocate(line)
    return batch.reference
