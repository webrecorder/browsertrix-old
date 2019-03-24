from fastapi import FastAPI

from crawlmanager.schema import *

from crawlmanager.crawl import CrawlManager, Crawl, init_redis, crawl_man

app = FastAPI()

init_redis()


# ============================================================================
@app.post('/crawls')
async def create_crawl(new_crawl: CreateCrawlRequest):
    return await crawl_man.create_new(new_crawl)


@app.put('/crawl/{crawl_id}/urls')
async def queue_urls(crawl_id: str, url_list: QueueUrlsRequest):
    crawl = await crawl_man.load_crawl(crawl_id)
    return await crawl.queue_urls(url_list.urls)


@app.get('/crawl/{crawl_id}', response_model=CrawlInfoResponse)
async def get_crawl(crawl_id: str):
    crawl = await crawl_man.load_crawl(crawl_id)
    return await crawl.get_info()


@app.get('/crawl/{crawl_id}/urls', response_model=CrawlInfoUrlsResponse)
async def get_crawl_urls(crawl_id: str):
    crawl = await crawl_man.load_crawl(crawl_id)
    return await crawl.get_info_urls()


@app.post('/crawl/{crawl_id}/start')
async def start_crawl(crawl_id: str, start_request: StartCrawlRequest):
    crawl = await crawl_man.load_crawl(crawl_id)
    return await crawl.start(start_request)


@app.post('/crawl/{crawl_id}/stop')
async def stop_crawl(crawl_id: str):
    crawl = await crawl_man.load_crawl(crawl_id)
    return await crawl.stop()


@app.get('/crawl/{crawl_id}/done')
async def is_done_crawl(crawl_id: str):
    crawl = await crawl_man.load_crawl(crawl_id)
    return await crawl.is_done()

@app.delete('/crawl/{crawl_id}')
async def delete_crawl(crawl_id: str):
    crawl = await crawl_man.load_crawl(crawl_id)
    return await crawl.delete()

