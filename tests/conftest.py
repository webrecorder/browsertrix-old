import os
from os import environ

import pytest
import yaml
from mock import patch as mock_patch
from starlette.testclient import TestClient

from .utils import init_fake_redis

crawl_names = []
crawls = []


def pytest_addoption(parser):
    default_file = os.path.join(os.path.dirname(__file__), "crawl_tests.yaml")
    parser.addoption("--crawl-file", action="store", default=default_file)
    parser.addoption("--run-only", action="store", default="")
    parser.addoption("--headless", action="store_true", default=False)

@pytest.fixture
def headless(request):
    return request.config.getoption("--headless")


def pytest_generate_tests(metafunc):
    if "crawl" in metafunc.fixturenames:
        init_crawl_data(
            metafunc.config.getoption("--crawl-file"),
            metafunc.config.getoption("--run-only"),
        )

        metafunc.parametrize("crawl", crawls, ids=crawl_names, scope="class")


def init_crawl_data(filename, run_only):
    """ Load the crawl YAML
    """
    global crawl_names
    global crawls
    if crawl_names and crawls:
        return

    run_only_list = run_only.split(",") if run_only else None

    crawls_root = None
    with open(filename) as fh:
        crawls_root = yaml.safe_load(fh.read())

    for crawl in crawls_root["crawls"]:
        if crawl.get("skip"):
            continue

        if run_only_list and crawl["name"] not in run_only_list:
            continue

        crawl_names.append(crawl["name"])
        crawls.append(crawl)


@pytest.fixture(scope="class")
def api_test_client(request):
    from browsertrix.api import app

    with TestClient(app) as tc:
        request.cls.client = tc
        yield



@pytest.fixture(scope="class")
def browsertrix_use_fake_redis(request):
    with mock_patch("browsertrix.utils.init_redis", init_fake_redis):
        yield
