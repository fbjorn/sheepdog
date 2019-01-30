import pytest
from schema import Schema

from sheepdog.watcher.db import StatusValue, WebsitePollingResult


@pytest.mark.asyncio
async def test_empty_list(client):
    resp = await client.get('/api/websites/')
    json_resp = await resp.json()
    assert json_resp == {'websites': []}
    assert resp.status == 200


async def test_url_add(client):
    url = 'http://valid.url.com'
    resp = await client.post('/api/websites/', json={'url': url})
    json_resp = await resp.json()
    assert resp.status == 201
    assert json_resp['website_info']
    assert json_resp['website_info']['url'] == url
    url_id = json_resp['website_info']['url_id']

    resp = await client.get('/api/websites/')
    json_resp = await resp.json()
    assert json_resp['websites'][0]['url_id'] == url_id
    assert json_resp['websites'][0]['url'] == url

    assert Schema({'websites': [{'url': str, 'url_id': str}]}).validate(json_resp)


@pytest.mark.parametrize('invalid_url', ['http//', 'web.site', 'https://website', ''])
async def test_url_add_failed(invalid_url, client):
    resp = await client.post('/api/websites/', json={'url': invalid_url})
    assert resp.status == 400


async def test_delete_url(client):
    resp = await client.post('/api/websites/', json={'url': 'http://valid.url.com'})
    assert resp.status == 201
    url_id = (await resp.json())['website_info']['url_id']

    resp = await client.delete(f'/api/websites/{url_id}/')
    assert resp.status == 204

    resp = await client.get('/api/websites/')
    json_resp = await resp.json()
    assert json_resp == {'websites': []}


@pytest.mark.parametrize('status_code,response_time,expected_status', [
    (200, 1, StatusValue.OK),
    (200, 1000, StatusValue.SLOW),
    (400, 1, StatusValue.ERROR),
    (500, 1000, StatusValue.ERROR),
])
async def test_list_statuses(status_code, response_time, expected_status, db, client):
    url = 'https://valid.url.com'
    ws_info = db.add_url(url)
    db.update_statuses({
        ws_info.url: WebsitePollingResult(
            url=ws_info.url, status_code=status_code, response_time=response_time
        )
    })
    resp = await client.get('/api/websites/status/')
    json_resp = await resp.json()
    assert json_resp['websites'][0]['status'] == expected_status

    assert Schema({'websites': [{'url': str, 'url_id': str, 'status': str}]}).validate(json_resp)
