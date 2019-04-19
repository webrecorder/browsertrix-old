import math
from typing import Any, Dict, List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Schema, UrlStr

__all__ = [
    'CrawlDoneResponse',
    'CrawlInfo',
    'CrawlInfoResponse',
    'CrawlInfoUrlsResponse',
    'CrawlInfosResponse',
    'CrawlType',
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


class CrawlType(str, Enum):
    single_page = 'single-page'
    all_links = 'all-links'
    same_domain = 'same-domain'
    custom = 'custom'


class BaseCreateCrawl(BaseModel):
    crawl_type: CrawlType = Schema(
        CrawlType.single_page, description='What type of crawl should be launched'
    )
    crawl_depth: Optional[int] = None
    num_browsers: int = Schema(
        2, description='How many browsers should be used for the crawl'
    )
    num_tabs: int = Schema(1, description='How many tabs should be used for the crawl')
    name: Optional[str] = Schema('', description='User friendly name for the crawl')
    coll: Optional[str] = Schema('live', description='Default Collection')
    mode: Optional[str] = Schema('record', description='Default Mode')
    screenshot_coll: Optional[str] = Schema(
        '', description='Collection to store screenshots, if any'
    )


class StartCrawlRequest(BaseModel):
    browser: Optional[str] = 'chrome:67'
    user_params: Dict[Any, Any] = dict()

    behavior_run_time: int = 0
    headless: bool = False
    screenshot_target_uri: Optional[str] = None


class OperationSuccessResponse(BaseModel):
    success: bool


class StartCrawlResponse(OperationSuccessResponse):
    browsers: List[str]


class CreateCrawlRequest(BaseCreateCrawl):
    start: Optional[StartCrawlRequest]
    seed_urls: List[UrlStr] = []


class CrawlInfoResponse(BaseCreateCrawl):
    id: str
    status: str = 'new'
    start_time: int = 0
    browsers: OptionalList
    browsers_done: OptionalList
    headless: bool = False
    num_queue: int = 0
    num_seen: int = 0
    num_pending: int = 0


class CrawlInfosResponse(BaseModel):
    crawls: List[CrawlInfoResponse]


class CrawlInfo(BaseModel):
    """ Model for validate a:{crawl_id}:info key
    All fields should be set in the model
    """

    id: str
    name: str
    coll: str
    screenshot_coll: str
    mode: str
    status: str
    crawl_type: str
    crawl_depth: int
    num_browsers: int
    num_tabs: int
    start_time: int = 0
    headless: bool = False


class CrawlInfoUrlsResponse(BaseModel):
    scopes: OptionalSet
    queue: OptionalList
    pending: OptionalList
    seen: OptionalSet


class FullCrawlInfoResponse(CrawlInfo, CrawlInfoUrlsResponse):
    success: bool


class CreateNewCrawlResponse(OperationSuccessResponse):
    id: str
    status: str = 'new'
    browsers: Optional[List[str]]


class QueueUrlsRequest(BaseModel):
    urls: List[str]


class CrawlDoneResponse(BaseModel):
    done: bool
