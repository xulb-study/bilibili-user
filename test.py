from multiprocessing.dummy import Pool as ThreadPool
import logging
logger = logging.getLogger("logger")


urls = []
acount = 0
for i in range(5000001, 5000100):
    urls.append(i)

    def getsource(url):
        global acount
        acount += 1
        logger.error("执行开始"+str(acount))
if __name__ == "__main__":
    pool = ThreadPool(40)
    try:
        if("aa".__contains__("a")):
            print("111")
        results = pool.map(getsource, urls)
    except Exception as e:
        logger.error(e)
    pool.close()
    pool.join()
