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
    crawlType: str = Schema(
        'single-page', description='What type of crawl should be launched'
    )
    crawlDepth: Optional[int] = None
    numBrowsers: int = Schema(
        1, description='How many browsers should be used for the crawl'
    )
    numTabs: int = Schema(1, description='How many tabs should be used for the crawl')
    seedURLs: OptionalList = None


class CrawlInfoResponse(CreateCrawlRequest):
    id: str
    status: str = 'new'
    browsers: OptionalList
    browsersDone: OptionalList


class CrawlInfosResponse(BaseModel):
    crawls: List[CrawlInfoResponse]


class CrawlInfo(BaseModel):
    """ Model for validate a:{crawl_id}:info key
    All fields should be set in the model
    """

    id: str
    status: str
    crawlType: str
    numBrowsers: int
    numTabs: int
    crawlDepth: int


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

    behaviorTimeout: int = 0
    headless: bool = False
    screenshotTargetUri: Optional[str] = None


class StartCrawlResponse(OperationSuccessResponse):
    browsers: List[str]


class CrawlDoneResponse(BaseModel):
    done: bool
