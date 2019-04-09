import pytest
from allocation import services, exceptions, repository, unit_of_work


class FakeRepository(repository.AbstractRepository):

    def __init__(self, products):
        self._products = set(products)

    def add(self, product):
        self._products.add(product)

    def get(self, sku):
        return next((p for p in self._products if p.sku == sku), None)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):

    def __init__(self):
        self.init_repositories(FakeRepository([]))
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass



def test_add_batch_for_new_product():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'sku1', 100, None, uow)
    assert uow.products.get('sku1') is not None
    assert uow.committed


def test_add_batch_for_existing_product():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'sku1', 100, None, uow)
    services.add_batch('b2', 'sku1', 99, None, uow)
    assert 'b2' in [b.reference for b in uow.products.get('sku1').batches]


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'sku1', 100, None, uow)
    result = services.allocate('o1', 'sku1', 10, uow)
    assert result == 'b1'


def test_allocate_errors_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'actualsku', 100, None, uow)

    with pytest.raises(exceptions.InvalidSku, match='Invalid sku nonexistentsku'):
        services.allocate('o1', 'nonexistentsku', 10, uow)


def test_allocate_commits():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'sku1', 100, None, uow)
    services.allocate('o1', 'sku1', 10, uow)
    assert uow.committed
