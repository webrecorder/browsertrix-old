from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Extra, Schema, UrlStr

from .types_ import (
    AnyDict,
    AnyDictList,
    Number,
    OptionalAnyDict,
    OptionalBool,
    OptionalNumber,
    OptionalSetStr,
    OptionalStr,
    OptionalStrList,
)

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

UrlStr.max_length = None  # type: ignore
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
    deviceScaleFactor: OptionalNumber = None
    maxTouchPoints: OptionalNumber = None
    isMobile: OptionalBool = None
    hasTouch: OptionalBool = None
    isLandscape: OptionalBool = None


class EmulatedGeoLocation(BaseModel):
    latitude: Number
    longitude: Number


class BrowserCookie(BaseModel):
    name: str
    value: str
    url: Optional[UrlStr] = None
    domain: OptionalStr = None
    path: OptionalStr = None
    secure: OptionalBool = None
    httpOnly: OptionalBool = None
    expires: OptionalNumber = None
    sameSite: Optional[CookieSameSite] = None


class BrowserOverrides(BaseModel):
    user_agent: OptionalStr = None
    accept_language: OptionalStr = None
    navigator_platform: OptionalStr = None
    extra_headers: Optional[Dict[str, str]] = None
    cookies: Optional[List[BrowserCookie]] = None
    geo_location: Optional[EmulatedGeoLocation] = None
    device: Optional[EmulatedDevice] = None


class BaseCreateCrawl(BaseModel):
    crawl_type: CrawlType = Schema(  # type: ignore
        CrawlType.SINGLE_PAGE, description='What type of crawl should be launched'
    )
    crawl_depth: int = Schema(  # type: ignore
        -1,
        description='How may pages out from the starting seed(s) should the crawl go',
    )
    num_browsers: int = Schema(  # type: ignore
        2, description='How many browsers should be used for the crawl'
    )
    num_tabs: int = Schema(
        1, description='How many tabs should be used for the crawl'
    )  # type: ignore
    name: OptionalStr = Schema(
        '', description='User friendly name for the crawl'
    )  # type: ignore
    coll: OptionalStr = Schema('live', description='Default Collection')  # type: ignore

    mode: CaptureMode = Schema(
        CaptureMode.RECORD, description='Default Mode'
    )  # type: ignore

    screenshot_coll: OptionalStr = Schema(  # type: ignore
        '', description='Collection to store screenshots, if any'
    )

    text_coll: OptionalStr = Schema(  # type: ignore
        '', description='Collection to store full-text indexes, if any'
    )


class CreateCrawlRequest(BaseCreateCrawl):
    class Config:
        extra: Extra = Extra.forbid

    seed_urls: List[UrlStr] = []
    scopes: AnyDictList = []

    cache: CacheMode = CacheMode.ALWAYS

    browser: OptionalStr = 'chrome:73'
    user_params: AnyDict = {}

    profile: OptionalStr = None

    ignore_extra: OptionalAnyDict = None

    behavior_max_time: Number = 0
    headless: bool = False
    screenshot_target_uri: OptionalStr = None

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
    browsers: OptionalStrList
    tabs_done: AnyDictList
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
    scopes: AnyDictList
    queue: AnyDictList
    pending: OptionalStrList
    seen: OptionalSetStr


class FullCrawlInfoResponse(CrawlInfo, CrawlInfoUrlsResponse):
    success: bool


class QueueUrlsRequest(BaseModel):
    urls: List[str]


class CrawlDoneResponse(BaseModel):
    done: bool
