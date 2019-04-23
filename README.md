# Browsertrix

[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black) [![Build Status](https://travis-ci.org/webrecorder/browsertrix.svg?branch=master)](https://travis-ci.org/webrecorder/browsertrix)

## High Fidelity Browser-Based Crawling Automation

Browsertrix is a brand new system from the Webrecorder project for automating browsers to perform complex scripted behaviors
as well as crawl multiple pages. (The name was originally used for an older project with similar goals).

Browsertrix uses Docker to manage the operation of multiple Chrome based browsers, operated via the CDP protocol, and uses [pywb](https://github.com/webrecorder/pywb) proxy mode for capture and replay.

It includes the following features:
* Crawling with different basic scope rules (Single Page, All Links, Same Domain, and custom)
* Execution of complex domain specific in-page behaviors (provided by [webrecorder/behaviors](https://github.com/webrecorder/behaviors))
* Capture or replay into designated pywb collections
* Optional screenshot creation of each page.
* Support for customized browser profiles to minimize capture of private information.

## Getting Started

### Installing Browsertrix

Browsertrix is currently designed to run with Docker and Docker Compose.
The Browsertrix CLI requires local Python 3.6+

To install, run:

```bash
git clone https://github.com/webrecorder/browsertrix
cd browsertrix
python setup.py install
./install-browsers.sh
docker-compose build
docker-compuse up -d
```

The `install-browsers.sh` script installs additional containers necessary for dynamic browser creation.
The script can be used to update the containers as well.

### Installing Browsertrix CLI

The Browsertrix CLI is installed by running `python setup.py install` and includes full functionality for running crawls and creating browser profiles.

Once installed, browsertrix commands are available via the `browsertrix` command.




## Testing

Browsertrix includes several test suites, also tested on automatically via Travis CI.

### Docker Integration Tests

Browsertrix includes a Docker-based test suite that runs crawls over content replayed from a WARC
(no live web content is accessed). This test suite requires Python 3.6+.

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

Browsertrix also includes a frontend (still under development) which will
have the same features as the CLI.

To access the browsertrix frontend, load `http://localhost:8000/`

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
