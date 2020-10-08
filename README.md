# sheepdog
Website monitoring service :sheep: :dog2:

> If you ended up in this repo please pay attention that this was just a test task before an interview

[![Build Status](https://travis-ci.org/fbjorn/sheepdog.svg?branch=master)](https://travis-ci.org/fbjorn/sheepdog)

## Installation
```bash
pip install pipenv
pipenv install --dev
```
##### Run tests and flake-8 checks
```bash
flake8
pytest
```

## Run service
```bash
cp config.template.yaml config.yaml
run_server
```
Then you can access front page at [localhost:8080](localhost:8080)

All configuration is made at your `config.yaml`

## API endpoints:

- GET /api/websites/
- POST /api/websites/
- DELETE /api/websites/{url_id}/
- GET /api/websites/status/

I recommend using `httpie` python package for API testing because it's concise yet powerful. Examples:
```bash
$ http GET :8080/api/websites/
HTTP/1.1 200 OK
Content-Length: 16
Content-Type: application/json; charset=utf-8
Date: Wed, 30 Jan 2019 20:33:10 GMT
Server: Python/3.7 aiohttp/4.0.0a0

{
    "websites": []
}
 
$ http POST :8080/api/websites/ url=https://google.com
HTTP/1.1 201 Created
Content-Length: 67
Content-Type: application/json; charset=utf-8
Date: Wed, 30 Jan 2019 20:34:09 GMT
Server: Python/3.7 aiohttp/4.0.0a0

{
    "website_info": {
        "url": "https://google.com",
        "url_id": "1d29c3"
    }
}

$ http GET :8080/api/websites/status/
HTTP/1.1 200 OK
Content-Length: 83
Content-Type: application/json; charset=utf-8
Date: Wed, 30 Jan 2019 20:34:40 GMT
Server: Python/3.7 aiohttp/4.0.0a0

{
    "websites": [
        {
            "status": "slow",
            "url": "https://google.com",
            "url_id": "1d29c3"
        }
    ]
}

$ http DELETE :8080/api/websites/1d29c3/
HTTP/1.1 204 No Content
Content-Length: 2
Content-Type: application/json; charset=utf-8
Date: Wed, 30 Jan 2019 20:35:03 GMT
Server: Python/3.7 aiohttp/4.0.0a0

```
