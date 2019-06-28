import uuid
import pytest
import requests

import config

def random_ref(prefix):
    return prefix + '-' + uuid.uuid4().hex[:10]

def post_to_add_batch(ref, sku, qty, eta):
    url = config.get_api_url()
    r = requests.post(
        f'{url}/add_batch',
        json={'ref': ref, 'sku': sku, 'qty': qty, 'eta': eta}
    )
    assert r.status_code == 201


@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
def test_happy_path_returns_201_and_allocated_batch():
    sku, othersku = random_ref('s1'), random_ref('s2')
    batch1, batch2, batch3 = random_ref('b1'), random_ref('b2'), random_ref('b3')
    post_to_add_batch(batch1, sku, 100, '2011-01-02')
    post_to_add_batch(batch2, sku, 100, '2011-01-01')
    post_to_add_batch(batch3, othersku, 100, None)
    data = {
        'orderid': random_ref('o'),
        'sku': sku,
        'qty': 3,
    }
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)
    assert r.status_code == 201
    assert r.json()['batchref'] == batch2


@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
def test_unhappy_path_returns_400_and_error_message():
    sku, order = random_ref('s'), random_ref('o')
    data = {'orderid': order, 'sku': sku, 'qty': 20}
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)
    assert r.status_code == 400
    assert r.json()['message'] == f'Invalid sku {sku}'

@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
def test_deallocate():
    sku, order1, order2 = random_ref('s'), random_ref('o1'), random_ref('o2')
    batch = random_ref('b')
    post_to_add_batch(batch, sku, 100, '2011-01-02')
    url = config.get_api_url()
    # fully allocate
    r = requests.post(f'{url}/allocate', json={
        'orderid': order1, 'sku': sku, 'qty': 100
    })
    assert r.json()['batchid'] == batch

    # cannot allocate second order
    r = requests.post(f'{url}/allocate', json={
        'orderid': order2, 'sku': sku, 'qty': 100
    })
    assert r.status_code == 400

    # deallocate
    r = requests.post(f'{url}/deallocate', json={
        'orderid': order1, 'sku': sku,
    })
    assert r.ok

    # now we can allocate second order
    r = requests.post(f'{url}/allocate', json={
        'orderid': order2, 'sku': sku, 'qty': 100
    })
    assert r.ok
    assert r.json()['batchid'] == batch
