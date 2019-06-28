import pytest
import model
import repository
import services


class FakeRepository(repository.AbstractRepository):

    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class FakeSession():
    committed = False

    def commit(self):
        self.committed = True


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch('b1', 'sku1', 100, None, repo, session)
    assert repo.get('b1') is not None
    assert session.committed


def test_allocate_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch('b1', 'sku1', 100, None, repo, session)
    result = services.allocate('o1', 'sku1', 10, repo, session)
    assert result == 'b1'


def test_allocate_errors_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch('b1', 'actualsku', 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match='Invalid sku nonexistentsku'):
        services.allocate('o1', 'nonexistentsku', 10, repo, FakeSession())


def test_commits():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch('b1', 'sku1', 100, None, repo, session)
    services.allocate('o1', 'sku1', 10, repo, session)
    assert session.committed is True


def test_deallocate_decrements_available_quantity():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch('b1', 'sku1', 100, None, repo, session)
    services.allocate('o1', 'sku1', 10, repo, session)
    batch = repo.get(reference='b1')
    assert batch.available_quantity == 90
    # services.deallocate(...
    ...
    assert  batch.available_quantity == 100

def test_deallocate_decrements_correct_quantity():
    ... #  TODO

def test_trying_to_deallocate_unallocated_batch():
    ... #  TODO: should this error or pass silently? up to you.
