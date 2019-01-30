import asyncio
import math
from typing import Dict

from aiohttp import client, ClientError, TraceConfig
from loguru import logger

from sheepdog.watcher.db import WebsitePollingResult, WebsiteStatusDB


def time_tracer(collector: dict):
    # https://github.com/aio-libs/aiohttp/issues/670
    # https://github.com/aio-libs/aiohttp/issues/1692

    async def on_request_start(session, context, params):
        context.on_request_start = session.loop.time()
        context.raw_url = str(params.url)

    async def on_request_end(session, context, params):
        total_time = math.floor((session.loop.time() - context.on_request_start) * 1000)
        collector[context.raw_url] = WebsitePollingResult(
            url=context.raw_url,
            status_code=params.response.status,
            response_time=total_time
        )

    async def on_request_exception(session, context, params):
        collector[context.raw_url] = WebsitePollingResult(
            url=context.raw_url,
            status_code=999,
            response_time=0,
        )

    trace_config = TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_end.append(on_request_end)
    trace_config.on_request_exception.append(on_request_exception)
    return trace_config


class WebSiteWatcher:

    def __init__(self, interval: int, db: WebsiteStatusDB, slow_threshold: int = None):
        self._interval = interval
        self._stop_event = asyncio.Event()
        self._db = db
        self._slow_threshold = slow_threshold

    def stop(self):
        self._stop_event.set()

    @staticmethod
    async def _fetch_website(url: str, session: client.ClientSession):
        try:
            async with session.get(url) as response:
                await response.text()
        except ClientError:
            pass  # information is saved in on_request_exception

    async def check_all_websites(self) -> Dict[str, WebsitePollingResult]:
        result_dict = {}
        urls = [website.url for website in self._db.list_websites()]
        async with client.ClientSession(trace_configs=[time_tracer(result_dict)]) as session:
            tasks = [
                asyncio.ensure_future(self._fetch_website(url, session))
                for url in urls
            ]
            if tasks:
                await asyncio.wait(tasks)
        logger.debug(f'Scan complete: {result_dict}')
        self._db.update_statuses(result_dict, slow_threshold=self._slow_threshold)
        return result_dict

    async def start(self):
        while not self._stop_event.is_set():
            try:
                await self.check_all_websites()
            except Exception:
                logger.exception('Error while scanning web sites')
                pass
            try:
                await asyncio.wait_for(self._stop_event.wait(), self._interval)
                return
            except asyncio.TimeoutError:
                pass
