from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Schema

__all__ = [
    'CrawlDoneResponse',
    'CrawlInfo',
    'CrawlInfoResponse',
    'CrawlInfoUrlsResponse',
    'CrawlInfosResponse',
    'CreateCrawlRequest',
    'CreateNewCrawlResponse',
    'OperationSuccessResponse',
    'QueueUrlsRequest',
    'StartCrawlRequest',
    'StartCrawlResponse',
]

# ============================================================================
OptionalList = Optional[List[str]]
OptionalSet = Optional[Set[str]]


class CreateCrawlRequest(BaseModel):
    scope_type: str = Schema(
        'single-page', description='What type of crawl should be launched'
    )
    num_browsers: int = Schema(
        2, description='How many browsers should be used for the crawl'
    )
    num_tabs: int = Schema(1, description='How many tabs should be used for the crawl')


class CrawlInfoResponse(CreateCrawlRequest):
    id: str
    status: str = 'new'
    crawl_depth: int = 0

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
    scope_type: str
    num_browsers: int
    num_tabs: int
    crawl_depth: int


class CrawlInfoUrlsResponse(BaseModel):
    scopes: OptionalSet
    queue: OptionalList
    pending: OptionalList
    seen: OptionalSet


class OperationSuccessResponse(BaseModel):
    success: bool


class CreateNewCrawlResponse(OperationSuccessResponse):
    id: str


class QueueUrlsRequest(BaseModel):
    urls: List[str]


class StartCrawlRequest(BaseModel):
    browser: Optional[str]
    user_params: Dict[Any, Any] = dict()

    behavior_timeout: int = 0
    headless: bool = False
    screenshot_target_uri: Optional[str] = None


class StartCrawlResponse(OperationSuccessResponse):
    browsers: List[str]


class CrawlDoneResponse(BaseModel):
    done: bool
