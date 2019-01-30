import asyncio

from aiohttp import web

from sheepdog.conf import Conf
from sheepdog.server.core import setup_jinja2
from sheepdog.server.utils import init_logging
from sheepdog.server.views import setup_routes
from sheepdog.watcher.db import WebsiteStatusDB
from sheepdog.watcher.watcher import WebSiteWatcher


def start_server():
    conf = Conf.load()
    init_logging(conf)
    db = WebsiteStatusDB(conf.db_path)
    watcher = WebSiteWatcher(interval=conf.polling_interval, slow_threshold=conf.slow_threshold, db=db)
    app = web.Application()
    setup_jinja2(app)
    setup_routes(app, db)
    asyncio.ensure_future(watcher.start())
    web.run_app(app, host=conf.host, port=conf.port, )
    watcher.stop()


if __name__ == '__main__':
    start_server()
