import os
from tempfile import NamedTemporaryFile

import pytest
from aiohttp import web

from sheepdog.server.views import setup_routes
from sheepdog.watcher.db import WebsiteStatusDB


@pytest.fixture
def db():
    with NamedTemporaryFile(mode='w') as tmp_file:
        db_path = f'{tmp_file.name}_test.yaml'
    yield WebsiteStatusDB(db_path)
    os.remove(db_path)


@pytest.fixture
def app(db):
    app = web.Application()
    setup_routes(app, db)
    yield app


@pytest.fixture
async def client(app, aiohttp_client, loop):
    yield await aiohttp_client(app)
