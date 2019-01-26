import uuid
from datetime import date, timedelta


from domain_model import (
    Shipment,
    allocate,
)


def random_id():
    return uuid.uuid4().hex[:10]


def test_can_allocate_to_stock():
    order = {'a-sku': 10}
    stock = {'a-sku': 1000}

    allocations = allocate(order, stock, shipments=[])

    assert allocations['a-sku'] == stock


def test_can_allocate_to_shipment():
    order = {'a-sku': 10}
    shipment = Shipment(eta=date.today(), lines={
        'a-sku': 1000
    })

    allocations = allocate(order, stock={}, shipments=[shipment])

    assert allocations['a-sku'] == shipment


def test_ignores_irrelevant_stock():
    order = {'sku1': 10}
    stock = {'sku2': 1000}
    shipment = Shipment(eta=date.today(), lines={
        'sku1': 1000,
    })

    allocations = allocate(order, stock=stock, shipments=[shipment])

    assert allocations['sku1'] == shipment


def test_can_allocate_to_correct_shipment():
    order = {'sku2': 10}
    shipment1 = Shipment(eta=date.today(), lines={
        'sku1': 1000,
    })
    shipment2 = Shipment(eta=date.today(), lines={
        'sku2': 1000,
    })

    allocations = allocate(order, stock={}, shipments=[shipment1, shipment2])

    assert allocations['sku2'] == shipment2


def test_allocates_to_stock_in_preference_to_shipment():
    order = {'sku1': 10}
    stock = {'sku1': 1000}
    shipment = Shipment(eta=date.today(), lines={
        'sku1': 1000,
    })

    allocations = allocate(order, stock, shipments=[shipment])

    assert allocations['sku1'] == stock


def test_can_allocate_multiple_lines_to_wh():
    order = {'sku1': 5, 'sku2': 10}
    stock = {'sku1': 1000, 'sku2': 1000}

    allocations = allocate(order, stock, shipments=[])
    assert allocations['sku1'] == stock
    assert allocations['sku2'] == stock


def test_can_allocate_multiple_lines_to_shipment():
    order = {'sku1': 5, 'sku2': 10}
    shipment = Shipment(eta=date.today(), lines={
        'sku1': 1000,
        'sku2': 1000,
    })

    allocations = allocate(order, stock={}, shipments=[shipment])

    assert allocations['sku1'] == shipment
    assert allocations['sku2'] == shipment


def test_can_allocate_to_both():
    order = {'sku1': 5, 'sku2': 10}
    shipment = Shipment(eta=date.today(), lines={
        'sku2': 1000,
    })
    stock = {'sku1': 1000}

    allocations = allocate(order, stock, shipments=[shipment])

    assert allocations['sku1'] == stock
    assert allocations['sku2'] == shipment


def test_can_allocate_to_both_preferring_stock():
    order = {'sku1': 1, 'sku2': 2, 'sku3': 3, 'sku4': 4}
    shipment = Shipment(eta=date.today(), lines={
        'sku1': 1000,
        'sku2': 1000,
        'sku3': 1000,
    })
    stock = {'sku3': 1000, 'sku4': 1000}

    allocations = allocate(order, stock, shipments=[shipment])

    assert allocations['sku1'] == shipment
    assert allocations['sku2'] == shipment
    assert allocations['sku3'] == stock
    assert allocations['sku4'] == stock


def test_mixed_allocations_are_avoided_if_possible():
    order = {'sku1': 10, 'sku2': 10}
    shipment = Shipment(eta=date.today(), lines={
        'sku1': 1000,
        'sku2': 1000,
    })
    stock = {'sku1': 1000}

    allocations = allocate(order, stock, shipments=[shipment])

    assert allocations['sku1'] == shipment
    assert allocations['sku2'] == shipment


def test_prefer_allocating_to_earlier_shipment():
    order = {'sku1': 10, 'sku2': 10}
    shipment1 = Shipment(eta=date.today(), lines={
        'sku1': 1000,
        'sku2': 1000,
    })
    tomorrow = date.today() + timedelta(days=1)
    shipment2 = Shipment(eta=tomorrow, lines={
        'sku1': 1000,
        'sku2': 1000,
    })
    stock = {}

    allocations = allocate(order, stock, shipments=[shipment2, shipment1])

    assert allocations['sku1'] == shipment1
    assert allocations['sku2'] == shipment1


def test_prefer_allocating_to_earlier_even_if_multiple_shipments():
    order = {'sku1': 10, 'sku2': 10, 'sku3': 10}
    shipment1 = Shipment(eta=date.today(), lines={
        'sku1': 1000,
    })
    tomorrow = date.today() + timedelta(days=1)
    shipment2 = Shipment(eta=tomorrow, lines={
        'sku2': 1000,
        'sku3': 1000,
    })
    later = tomorrow + timedelta(days=1)
    shipment3 = Shipment(eta=later, lines={
        'sku2': 1000,
        'sku3': 1000,
    })
    stock = {}

    allocations = allocate(order, stock, shipments=[shipment3, shipment2, shipment1])

    assert allocations['sku1'] == shipment1
    assert allocations['sku2'] == shipment2
    assert allocations['sku3'] == shipment2


def test_stock_not_quite_enough_means_we_use_shipment():
    order = {'sku1': 10, 'sku2': 10}
    stock = {'sku1': 10, 'sku2': 5}
    shipment = Shipment(eta=date.today(), lines={
        'sku1': 1000,
        'sku2': 1000,
    })

    allocations = allocate(order, stock, shipments=[shipment])

    assert allocations['sku1'] == shipment
    assert allocations['sku2'] == shipment


def test_cannot_allocate_if_insufficent_quantity_in_stock():
    order = {'a-sku': 10}
    stock = {'a-sku': 5}

    allocations = allocate(order, stock, shipments=[])

    assert 'a-sku' not in allocations


def test_cannot_allocate_if_insufficent_quantity_in_shipment():
    order = {'a-sku': 10}
    shipment = Shipment(eta=date.today(), lines={
        'a-sku': 5,
    })

    allocations = allocate(order, stock={}, shipments=[shipment])

    assert 'a-sku' not in allocations
