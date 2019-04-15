crawlmanager
=============================
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Getting Started

## Running

crawlmanager is designed to run with Docker and Docker Compose.
To run, launch:

```bash
docker-compose build; docker-compuse up -d
```

To access the crawlmanager frontend, load `http://localhost:8000/`

## Testing

Crawlmanager includes several test suites, also tested on automatically via Travis CI.

### Docker Integration Tests

Crawlmanager includes a Docker-based test suite that runs crawls over content replayed from a WARC
(no live web content is accessed). This requires Python 3.6+

To run this test suite, run:

```bash
bash ./tests/start-test-compose.sh
pip install -U -r test-docker-requirements.txt
py.test --headless ./tests/test_live_crawl.py
bash ./tests/stop-test-compose.sh
```

### Local API Tests

To install and run local tests of the API (without Docker), run the following:
(Python 3.7+ is required)

```bash
pip install -U -r requirements.txt -r test-local-requirements.txt
py.test ./tests/test_api.py
```

## Frontend

The frontend React app is found in `./frontend` and can be started via:

```
yarn run develop
```

(The develop server is started at `http://localhost:8001` to avoid conflict with production)

To build the production bundle, run:
```
yarn run build-prod
```

This should update the production server running at `http://localhost:8000`
