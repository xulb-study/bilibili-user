import logging as log
from multiprocessing.dummy import Pool as ThreadPool
urls = []
for i in range(5000001, 5000100):
    urls.append(i)

    def getsource(url):
        log.error("执行开始"+str(url))
if __name__ == "__main__":
    pool = ThreadPool(40)
    try:
        if("aa".__contains__("a")):
            print("111")
        results = pool.map(getsource, urls)
    except Exception as e:
        log.error(e)
    pool.close()
    pool.join()
