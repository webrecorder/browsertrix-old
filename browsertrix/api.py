from fastapi import APIRouter, FastAPI
from starlette.middleware.cors import ALL_METHODS, CORSMiddleware
from starlette.responses import FileResponse, UJSONResponse
from starlette.staticfiles import StaticFiles

from .crawl import CrawlManager
from .schema import (
    CrawlDoneResponse,
    CrawlInfoResponse,
    CrawlInfoUrlsResponse,
    CrawlInfosResponse,
    CreateCrawlRequest,
    CreateStartResponse,
    FullCrawlInfoResponse,
    OperationSuccessResponse,
    QueueUrlsRequest,
)

app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=ALL_METHODS, allow_headers=["*"]
)
crawl_man = CrawlManager()
crawl_router = APIRouter()


# ============================================================================
@app.post('/crawls', response_model=CreateStartResponse, response_class=UJSONResponse)
async def create_crawl(new_crawl: CreateCrawlRequest):
    return await crawl_man.create_new(new_crawl)


@app.get('/crawls', response_model=CrawlInfosResponse, response_class=UJSONResponse)
async def get_all_crawls():
    return await crawl_man.get_all_crawls()


@crawl_router.put(
    '/{crawl_id}/urls',
    response_model=OperationSuccessResponse,
    response_class=UJSONResponse,
)
async def queue_urls(crawl_id: str, url_list: QueueUrlsRequest):
    return await crawl_man.queue_crawl_urls(crawl_id, url_list.urls)


@crawl_router.get(
    '/{crawl_id}', response_model=CrawlInfoResponse, response_class=UJSONResponse
)
async def get_crawl(crawl_id: str):
    return await crawl_man.get_crawl_info(crawl_id)


@crawl_router.get(
    '/{crawl_id}/urls',
    response_model=CrawlInfoUrlsResponse,
    response_class=UJSONResponse,
)
async def get_crawl_urls(crawl_id: str):
    return await crawl_man.get_crawl_urls(crawl_id)


@crawl_router.get(
    '/{crawl_id}/info',
    response_model=FullCrawlInfoResponse,
    response_class=UJSONResponse,
)
async def get_full_crawl_info(crawl_id: str):
    return await crawl_man.get_full_crawl_info(crawl_id)


@crawl_router.post(
    '/{crawl_id}/start',
    response_model=CreateStartResponse,
    response_class=UJSONResponse,
)
async def start_crawl(crawl_id: str):
    return await crawl_man.start_crawl(crawl_id)


@crawl_router.post(
    '/{crawl_id}/stop',
    response_model=OperationSuccessResponse,
    response_class=UJSONResponse,
)
async def stop_crawl(crawl_id: str):
    return await crawl_man.stop_crawl(crawl_id)


@crawl_router.get(
    '/{crawl_id}/done', response_model=CrawlDoneResponse, response_class=UJSONResponse
)
async def is_done_crawl(crawl_id: str):
    return await crawl_man.is_crawl_done(crawl_id)


@crawl_router.delete(
    '/{crawl_id}', response_model=OperationSuccessResponse, response_class=UJSONResponse
)
async def delete_crawl(crawl_id: str):
    return await crawl_man.delete_crawl(crawl_id)


@app.route('/')
def ui(*args, **kwargs):
    return FileResponse('static/index.html')


app.include_router(crawl_router, prefix='/crawl', tags=['crawl'])
app.mount('/static', StaticFiles(directory='static', check_dir=True), 'static')
app.add_event_handler('startup', crawl_man.startup)
app.add_event_handler('shutdown', crawl_man.shutdown)
