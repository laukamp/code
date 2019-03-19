import pytest

import model
import services


def test_returns_allocation():
    line = model.OrderLine('o1', 'sku1', 10)
    batch = model.Batch('b1', 'sku1', 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())
    assert result == 'b1'


def test_error_for_invalid_sku():
    line = model.OrderLine('o1', 'nonexistentsku', 10)
    batch = model.Batch('b1', 'actualsku', 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match='Invalid sku nonexistentsku'):
        services.allocate(line, repo, FakeSession())
