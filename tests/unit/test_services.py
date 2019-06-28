import pytest
from allocation import repository, services, unit_of_work


class FakeRepository(repository.AbstractRepository):

    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    ...



def test_add_batch():
    uow = FakeUnitOfWork()
    # fake_uow_starter = FakeUoWContextManager(uow) ?
    # fake_uow_starter = contextlib.nullcontext(uow) ?
    # services.add_batch('b1', 'sku1', 100, None, fake_uow_starter)
    services.add_batch('b1', 'sku1', 100, None, uow)
    assert uow.batches.get('b1') is not None
    assert uow.committed


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'sku1', 100, None, uow)
    result = services.allocate('o1', 'sku1', 10, uow)
    assert result == 'b1'


def test_allocate_errors_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'actualsku', 100, None, uow)

    with pytest.raises(services.InvalidSku, match='Invalid sku nonexistentsku'):
        services.allocate('o1', 'nonexistentsku', 10, uow)


def test_allocate_commits():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'sku1', 100, None, uow)
    services.allocate('o1', 'sku1', 10, uow)
    assert uow.committed
