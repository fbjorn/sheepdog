from dataclasses import asdict, dataclass
from typing import Dict, List, Union

from sheepdog.database.database import KeyValueFileDatabase
from sheepdog.database.errors import AlreadyExists


@dataclass
class WebsitePollingResult:
    url: str
    status_code: int
    response_time: int


@dataclass
class WebsiteInfo:
    url_id: str
    status: str
    url: str


class StatusValue:
    OK = 'ok'
    ERROR = 'error'
    SLOW = 'slow'
    UNKNOWN = 'unknown'


class WebsiteStatusDB(KeyValueFileDatabase):
    _URLS_KEY = 'website_urls'
    _INITIAL_STATE = {_URLS_KEY: {}}

    def update_statuses(self, poll_result: Dict[str, WebsitePollingResult], slow_threshold: int = 250):
        new_state = self.get(self._URLS_KEY)
        known_urls = {ws_info['url']: url_id for url_id, ws_info in new_state.items()}
        for url, ws_info in poll_result.items():
            if url not in known_urls:
                continue
            status = StatusValue.OK
            if ws_info.status_code >= 400:
                status = StatusValue.ERROR
            elif ws_info.response_time > slow_threshold:
                status = StatusValue.SLOW
            url_id = known_urls[url]
            new_state[url_id]['status'] = status
        self.set(self._URLS_KEY, new_state)

    def add_url(self, url: str) -> WebsiteInfo:
        new_state = self.get(self._URLS_KEY)
        if any(website_info['url'] == url for website_info in new_state.values()):
            raise AlreadyExists
        url_id = self._generate_random_key()
        data = WebsiteInfo(url_id=url_id, status=StatusValue.UNKNOWN, url=url)
        new_state[url_id] = asdict(data)
        self.set(self._URLS_KEY, new_state)
        return data

    def list_websites(self, as_dict=False) -> Union[List[WebsiteInfo], List[dict]]:
        return [
            (info if as_dict else WebsiteInfo(**info))
            for info in self.get(self._URLS_KEY).values()
        ]

    def remove_url(self, url_id: str):
        new_state = {
            website.url_id: asdict(website)
            for website in self.list_websites() if website.url_id != url_id
        }
        self.set(self._URLS_KEY, new_state)
