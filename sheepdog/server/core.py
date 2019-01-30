import re
from contextlib import wraps
from json import JSONDecodeError
from pathlib import Path

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp.web import Application, json_response, Response
from aiohttp.web_request import Request
from loguru import logger
from schema import Schema, SchemaError

from sheepdog.database.database import KeyValueFileDatabase

# borrowed from Django
URL_REGEX = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE
)


def api_view(db: KeyValueFileDatabase):
    def wrapper(fn):
        @wraps(fn)
        async def wrapped(request: Request, *args, **kwargs):
            try:
                return await fn(request, *args, db=db, **kwargs)
            except Exception:
                logger.exception('Error while handling request')
                return Response(status=web.HTTPServerError.status_code)

        return wrapped

    return wrapper


def validate_params(schema: dict):
    def wrapper(fn):
        @wraps(fn)
        async def wrapped(request: Request, *args, **kwargs):
            try:
                json_request = await request.json()
            except JSONDecodeError:
                json_request = {}
            try:
                Schema(schema).validate(json_request)
            except SchemaError as exc:
                return json_response(data=exc.autos, status=web.HTTPBadRequest.status_code)
            else:
                return await fn(request, *args, **kwargs, json_params=json_request)

        return wrapped

    return wrapper


def setup_jinja2(app: Application):
    tmpl_path = Path(__file__).parent.resolve() / 'templates'
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(tmpl_path.as_posix()))
