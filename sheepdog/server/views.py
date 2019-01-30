import aiohttp_jinja2
from aiohttp import web
from aiohttp.web import Application, json_response
from aiohttp.web_request import Request
from schema import Regex

from sheepdog.database.errors import AlreadyExists
from sheepdog.server.core import api_view, URL_REGEX, validate_params
from sheepdog.watcher.db import WebsiteStatusDB


async def list_websites(request: Request, db: WebsiteStatusDB):
    websites = db.list_websites()
    resp_data = [{'url_id': ws_info.url_id, 'url': ws_info.url} for ws_info in websites]
    return json_response(data={'websites': resp_data})


async def list_statuses(request: Request, db: WebsiteStatusDB):
    resp_data = db.list_websites(as_dict=True)
    return json_response(data={'websites': resp_data})


@validate_params({'url': Regex(URL_REGEX)})
async def add_website(request: Request, db: WebsiteStatusDB, json_params: dict):
    try:
        ws_info = db.add_url(json_params['url'])
    except AlreadyExists:
        return json_response(status=web.HTTPConflict.status_code)
    resp_data = {'url': ws_info.url, 'url_id': ws_info.url_id}
    return json_response(data={'website_info': resp_data}, status=web.HTTPCreated.status_code)


async def remove_website(request: Request, db: WebsiteStatusDB):
    url_id = request.match_info['url_id']
    db.remove_url(url_id)
    return json_response(data={}, status=web.HTTPNoContent.status_code)


async def main_page(request: Request, db: WebsiteStatusDB):
    websites = db.list_websites(as_dict=True)
    return aiohttp_jinja2.render_template(
        'website_statuses.jinja2',
        request,
        context={'websites': [ws for ws in websites if ws['status'] != 'unknown']}
    )


def setup_routes(app: Application, db: WebsiteStatusDB):
    app.add_routes([
        web.get('/api/websites/', handler=api_view(db)(list_websites)),
        web.post('/api/websites/', handler=api_view(db)(add_website)),
        web.delete('/api/websites/{url_id}/', handler=api_view(db)(remove_website)),
        web.get('/api/websites/status/', handler=api_view(db)(list_statuses)),
        web.get('/', handler=api_view(db)(main_page)),
    ])
