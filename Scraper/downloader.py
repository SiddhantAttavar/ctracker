import asyncio
import logging
import pathlib
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import httpx
from aiofile import async_open

logger = logging.getLogger("Scraper.Downloader")


@dataclass
class URL:
    request_type: str  # POST / GET
    url: str
    payload: Optional[dict] = None


class Downloader:
    """
    Use .run() after instantiating.

    - a queue of urls
    - a worker function that keeps running .download_and_store_one_url() till it's task is cancelled.
    - .download_and_store_one_url() takes one url from the queue and does what the name suggests.

    The whole program is IO heavy so GET requests and writing to disk are done asynchronously.
    """

    def __init__(
        self,
        client: httpx.AsyncClient,
        url_queue: asyncio.Queue,
        num_workers=25,
    ):
        self.client = client

        self.url_queue = url_queue
        self.num_workers = num_workers

        self.responses_stored = 0
        self.total_urls = self.url_queue.qsize()
        self.responses = []

    async def worker(self):
        while True:
            try:
                await self.download_and_store_one_url()
            except asyncio.CancelledError:
                return

    async def download_and_store_one_url(self):
        url: URL = await self.url_queue.get()
        logger.debug(f"Working on url {url}")
        try:
            match url.request_type:
                case "GET":
                    response = await self.client.get(url.url)
                case "POST":
                    response = await self.client.post(url=url.url, data=url.payload)
                case _:
                    raise Exception("The URL does not have a supported .request_type")

            if response.status_code != 200:
                error_message = (
                    f"{response.status_code} {response.reason_phrase} - {url}"
                )
                if response.status_code == 404:
                    logger.warning(error_message)
                else:
                    logger.error(error_message)
            else:
                # TODO: Write this into a database
                self.responses.append(response)

        except Exception as exc:
            logger.warning(f"{exc.__class__.__name__} while working on {url}")
        finally:
            self.responses_stored += 1
            logger.info(f"{self.responses_stored} / {self.total_urls} collected!")
            self.url_queue.task_done()

    async def run(self):
        workers = [asyncio.create_task(self.worker()) for _ in range(self.num_workers)]
        await self.url_queue.join()
        for worker in workers:
            worker.cancel()
        return self.responses


async def test():
    url_queue = asyncio.Queue()
    demo_urls = ["https://codeforces.com/profile/siddhantattavar"]
    for url in demo_urls:
        u = URL("GET", url)
        url_queue.put_nowait(u)
    async with httpx.AsyncClient() as client:
        downloader = Downloader(client=client, url_queue=url_queue)
        responses = await downloader.run()
    for response in responses:
        print(response)


if __name__ == "__main__":
    import time

    a = time.perf_counter()
    asyncio.run(test())
    delta = time.perf_counter() - a

    print(f"Completed in {delta} seconds")
