import math
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

from pydantic import BaseModel, Schema, UrlStr

__all__ = [
    'BrowserCookie',
    'BrowserOverrides',
    'CacheMode',
    'CaptureMode',
    'CookieSameSite',
    'CrawlDoneResponse',
    'CrawlInfo',
    'CrawlInfoResponse',
    'CrawlInfoUrlsResponse',
    'CrawlInfosResponse',
    'CrawlType',
    'CreateCrawlRequest',
    'CreateStartResponse',
    'EmulatedDevice',
    'EmulatedGeoLocation',
    'FullCrawlInfoResponse',
    'OperationSuccessResponse',
    'QueueUrlsRequest',
]

# ============================================================================
OptionalList = Optional[List[str]]
OptionalSet = Optional[Set[str]]
Number = Union[int, float]

UrlStr.max_length = math.inf
UrlStr.relative = True

class CrawlType(str, Enum):
    SINGLE_PAGE = 'single-page'
    ALL_LINKS = 'all-links'
    SAME_DOMAIN = 'same-domain'
    CUSTOM = 'custom'


class CaptureMode(str, Enum):
    RECORD = 'record'
    REPLAY = 'replay'
    LIVE = 'live'


class CacheMode(str, Enum):
    ALWAYS = 'always'
    NEVER = 'never'
    DEFAULT = 'default'


class CookieSameSite(str, Enum):
    STRICT = 'Strict'
    LAX = 'LAX'
    EXTENDED = 'Extended'
    NONE = 'None'



class EmulatedDevice(BaseModel):
    width: Number
    height: Number
    deviceScaleFactor: Optional[Number] = None
    maxTouchPoints: Optional[Number] = None
    isMobile: Optional[bool] = None
    hasTouch: Optional[bool] = None
    isLandscape: Optional[bool] = None


class EmulatedGeoLocation(BaseModel):
    latitude: Number
    longitude: Number


class BrowserCookie(BaseModel):
    name: str
    value: str
    url: Optional[UrlStr] = None
    domain: Optional[str] = None
    path: Optional[str] = None
    secure: Optional[bool] = None
    httpOnly: Optional[bool] = None
    expires: Optional[Number] = None
    sameSite: Optional[CookieSameSite] = None


class BrowserOverrides(BaseModel):
    user_agent: Optional[str] = None
    accept_language: Optional[str] = None
    navigator_platform: Optional[str] = None
    extra_headers: Optional[Dict[str, str]] = None
    cookies: Optional[List[BrowserCookie]] = None
    geo_location: Optional[EmulatedGeoLocation] = None
    device: Optional[EmulatedDevice] = None


class BaseCreateCrawl(BaseModel):
    crawl_type: CrawlType = Schema(
        CrawlType.SINGLE_PAGE, description='What type of crawl should be launched'
    )
    crawl_depth: Optional[int] = None
    num_browsers: int = Schema(
        2, description='How many browsers should be used for the crawl'
    )
    num_tabs: int = Schema(1, description='How many tabs should be used for the crawl')
    name: Optional[str] = Schema('', description='User friendly name for the crawl')
    coll: Optional[str] = Schema('live', description='Default Collection')

    mode: CaptureMode = Schema(CaptureMode.RECORD, description='Default Mode')

    screenshot_coll: Optional[str] = Schema(
        '', description='Collection to store screenshots, if any'
    )

    text_coll: Optional[str] = Schema(
        '', description='Collection to store full-text indexes, if any'
    )


class CreateCrawlRequest(BaseCreateCrawl):
    class Config:
        extra = 'forbid'

    seed_urls: List[Union[UrlStr, dict]] = []
    scopes: List[Dict[Any, Any]] = []

    cache: CacheMode = CacheMode.ALWAYS

    browser: Optional[str] = 'chrome:76'
    user_params: Dict[Any, Any] = dict()

    profile: Optional[str] = None

    ignore_extra: Optional[Dict[Any, Any]] = None

    behavior_max_time: int = 0
    headless: bool = False
    screenshot_target_uri: Optional[str] = None

    start: bool = True
    browser_overrides: Optional[BrowserOverrides] = None


class OperationSuccessResponse(BaseModel):
    success: bool


class CreateStartResponse(OperationSuccessResponse):
    id: str
    status: str = 'new'
    browsers: Optional[List[str]]


class CrawlInfoResponse(BaseCreateCrawl):
    id: str
    status: str = 'new'
    start_time: int = 0
    finish_time: int = 0
    browsers: OptionalList
    tabs_done: List[Dict[Any, Any]]
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
    text_coll: str
    mode: str
    status: str
    crawl_type: str
    crawl_depth: int
    num_browsers: int
    num_tabs: int
    start_time: int = 0
    finish_time: int = 0
    headless: bool = False
    browser_overrides: Optional[BrowserOverrides] = None


class CrawlInfoUrlsResponse(BaseModel):
    scopes: List[Dict[Any, Any]]
    queue: List[Dict[Any, Any]]
    pending: OptionalList
    seen: OptionalSet


class FullCrawlInfoResponse(CrawlInfo, CrawlInfoUrlsResponse):
    success: bool


class QueueUrlsRequest(BaseModel):
    urls: List[Union[UrlStr, dict]]


class CrawlDoneResponse(BaseModel):
    done: bool
