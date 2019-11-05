import asyncio
import time
import requests
from multiprocessing.dummy import Pool as ThreadPool
import logging
import logger
logger = logging.getLogger("logger")
urls = []
time1 = time.time()
acount = 0
for i in range(1000):
    urls.append(i)

    def getsource(url):
        time.sleep(1)
        global acount
        acount += 1
        logger.debug("执行开始"+str(acount))


def run():
    time3 = time.time()
    for i in range(10):
        loop.run_until_complete(hello())
    time4 = time.time()
    logger.info("耗时"+str(time4-time3))


async def hello():
    asyncio.sleep(1)
    jscontent = requests \
        .session() \
        .post('http://space.bilibili.com/ajax/member/GetInfo') \
        .text

   # print('Hello World:%s' % time.time())

loop = asyncio.get_event_loop()
if __name__ == "__main__":
    # pool = ThreadPool(40)
    # try:
    #     results = pool.map(getsource, urls)
    #     time2 = time.time()
    #     logger.info("耗时"+str(time2-time1))

    # except Exception as e:
    #     logger.error(e)
    # pool.close()
    # pool.join()
    run()

# 定义异步函数
