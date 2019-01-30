import pytest

from sheepdog.database.errors import AlreadyExists, KeyDoesNotExist
from sheepdog.watcher.db import StatusValue, WebsitePollingResult


def test_basic_operations(db):
    with pytest.raises(KeyDoesNotExist):
        db.get('key')
    assert db.get('missing_key', default='default') == 'default'

    db.set('key', 'value')
    assert db.get('key') == 'value'


def test_list_urls(db):
    assert db.list_websites() == []
    db.add_url('URL')
    websites = db.list_websites()
    assert len(websites) == 1
    assert websites[0].url == 'URL'
    assert websites[0].status == StatusValue.UNKNOWN
    with pytest.raises(AlreadyExists):
        db.add_url('URL')
    ws_dicts = db.list_websites(as_dict=True)
    assert ws_dicts[0]['url'] == 'URL'
    assert ws_dicts[0]['status'] == StatusValue.UNKNOWN


def test_update_urls(db):
    ws_info = db.add_url('URL')
    db.update_statuses({
        ws_info.url: WebsitePollingResult(
            url='URL', status_code=200, response_time=1),
        'non-existing-key': WebsitePollingResult(
            url='_url', status_code=200, response_time=1),
    })
    urls = db.list_websites()
    assert len(urls) == 1
    assert urls[0].url == 'URL'
    assert urls[0].status == StatusValue.OK
