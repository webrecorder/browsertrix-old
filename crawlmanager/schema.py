import math
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Schema, UrlStr

__all__ = [
    'CrawlDoneResponse',
    'CrawlInfo',
    'CrawlInfoResponse',
    'CrawlInfoUrlsResponse',
    'CrawlInfosResponse',
    'CreateCrawlRequest',
    'CreateNewCrawlResponse',
    'FullCrawlInfoResponse',
    'OperationSuccessResponse',
    'QueueUrlsRequest',
    'StartCrawlRequest',
    'StartCrawlResponse',
]

# ============================================================================
OptionalList = Optional[List[str]]
OptionalSet = Optional[Set[str]]

UrlStr.max_length = math.inf
UrlStr.relative = True


class BaseCreateCrawl(BaseModel):
    crawl_type: str = Schema(
        'single-page', description='What type of crawl should be launched'
    )
    crawl_depth: Optional[int] = None
    num_browsers: int = Schema(
        2, description='How many browsers should be used for the crawl'
    )
    num_tabs: int = Schema(1, description='How many tabs should be used for the crawl')


class CreateCrawlRequest(BaseCreateCrawl):
    seed_urls: List[UrlStr] = []


class CrawlInfoResponse(BaseCreateCrawl):
    id: str
    status: str = 'new'
    browsers: OptionalList
    browsers_done: OptionalList


class CrawlInfosResponse(BaseModel):
    crawls: List[CrawlInfoResponse]


class CrawlInfo(BaseModel):
    """ Model for validate a:{crawl_id}:info key
    All fields should be set in the model
    """

    id: str
    status: str
    crawl_type: str
    crawl_depth: int
    num_browsers: int
    num_tabs: int


class CrawlInfoUrlsResponse(BaseModel):
    scopes: OptionalSet
    queue: OptionalList
    pending: OptionalList
    seen: OptionalSet


class OperationSuccessResponse(BaseModel):
    success: bool


class FullCrawlInfoResponse(CrawlInfo, CrawlInfoUrlsResponse):
    success: bool


class CrawlFullInfosResponse(OperationSuccessResponse):
    crawls: List[CrawlInfoResponse]


class CreateNewCrawlResponse(OperationSuccessResponse):
    id: str
    status: str = 'new'


class QueueUrlsRequest(BaseModel):
    urls: List[str]


class StartCrawlRequest(BaseModel):
    browser: Optional[str] = 'chrome:67'
    user_params: Dict[Any, Any] = dict()

    behavior_run_time: int = 0
    headless: bool = False
    screenshot_target_uri: Optional[str] = None


class StartCrawlResponse(OperationSuccessResponse):
    browsers: List[str]


class CrawlDoneResponse(BaseModel):
    done: bool
