# -*-coding:utf8-*-

import requests
import json
import random
import pymysql
from DBUtils.PooledDB import PooledDB
import datetime
import time

import logging as log


from multiprocessing.dummy import Pool as ThreadPool


def datetime_to_timestamp_in_milliseconds(d):
    def current_milli_time(): return int(round(time.time() * 1000))

    return current_milli_time()


def LoadUserAgents(uafile):
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.decode().strip()[:-1])
    random.shuffle(uas)
    return uas


log.basicConfig(level=log.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                handlers={log.FileHandler(filename='test.log', mode='a', encoding='utf-8')})

uas = LoadUserAgents("user_agents.txt")
head = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://space.bilibili.com/45388',
    'Origin': 'http://space.bilibili.com',
    'Host': 'space.bilibili.com',
    'AlexaToolbar-ALX_NS_PH': 'AlexaToolbar/alx-4.0',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
}


def get_proxy():
    return requests.get("http://my_propxy:5010/get/", timeout=2).json()


def delete_proxy(proxy):
    requests.get(
        "http://my_propxy:5010/delete/?proxy={}".format(proxy), timeout=2)


urls = []


def initUrls(start, step):
    conn = mysqlconnect()
    cur = conn.cursor()
    cur.execute("select mid from bilibili_error")
    results = list(cur.fetchall())
    cur.execute("delete from bilibili_error")
    conn.commit()
    for x in results:
        urls.append('https://space.bilibili.com/' + str(x[0]))
    for i in range(start, start+step):
        urls.append('https://space.bilibili.com/' + str(i))
    cur.close()
    conn.close()


mysqlpool = PooledDB(pymysql, 5, host='eam-mysql', user='root',
                     passwd='123456', db='bilibili', charset='utf8')  # 5为连接池里的最少连接数


def mysqlconnect():
    conn = mysqlpool.connection()
    return conn


def initError(limit):
    conn = mysqlconnect()
    cur = conn.cursor()
    cur.execute("select max(mid) from bilibili_user_info ")
    max = (cur.fetchone())[0]
    if(max > limit):
        max = limit
    cur.execute(
        "select mid from bilibili_user_info  order by mid ASC limit " + str(limit)+"")
    results = list(cur.fetchall())

    for i in range(max):
        if(i == results[0][0]):
            results.pop(0)
            if(len(results) == 0):
                break
        else:
            urls.append('https://space.bilibili.com/' + str(i))
            pass
    cur.execute("delete from bilibili_error")
    conn.commit()
    cur.close()
    conn.close()


def saveErrorUrl(id):
    conn = mysqlconnect()
    cur = conn.cursor()
    cur.execute("INSERT INTO bilibili_error (mid)VALUE("+id+")")
    conn.commit()
    cur.close()
    conn.close()


def getUserInfo(head, payload):
    retry_count = 2
    proxy = get_proxy().get("proxy")
    while retry_count > 0:
        try:
            jscontent = requests \
                .session() \
                .post('http://space.bilibili.com/ajax/member/GetInfo',
                      headers=head,
                      data=payload,
                      timeout=2,
                      proxies={"http": "http://{}".format(proxy), "https": "https://{}".format(proxy)}) \
                .text
            if(jscontent.__contains__("400")):  # ip被封了
                retry_count -= 1
                delete_proxy(proxy)
                log.debug("ip被封,删除代理池中代理")
                return getUserInfo(head, payload)
            try:
                return json.loads(jscontent)
            except Exception as e:
                log.error("其他异常" + (jscontent))
                return None

        except Exception as e:
            retry_count -= 1
            # 出错2次, 删除代理池中代理
            delete_proxy(proxy)
            log.debug("删除代理池中代理"+str(e))

    return None


time1 = time.time()

urls = []

# Please change the range data by yourself.


def getsource(url):
    log.info("执行开始")
    payload = {
        '_': datetime_to_timestamp_in_milliseconds(datetime.datetime.now()),
        'mid': url.replace('https://space.bilibili.com/', '')
    }
    ua = random.choice(uas)
    head = {
        'User-Agent': ua,
        'Referer': 'https://space.bilibili.com/' + str(random.randint(0, 50000)) + '?from=search&seid=' + str(random.randint(10000, 50000))
    }

    jsDict = getUserInfo(head, payload)
    if jsDict == None:
        jsDict = getUserInfo(head, payload)
        if jsDict == None:
            saveErrorUrl(url.replace('https://space.bilibili.com/', ''))
            return
    time2 = time.time()
    try:
        statusJson = jsDict['status'] if 'status' in jsDict.keys(
        ) else False
        if statusJson == True:
            if 'data' in jsDict.keys():
                jsData = jsDict['data']
                mid = jsData.get('mid')
                name = jsData.get('name')
                sex = jsData.get('sex')
                rank = jsData.get('rank')
                face = jsData.get('face')
                regtimestamp = jsData.get('regtime')
                regtime_local = time.localtime(regtimestamp)
                regtime = time.strftime("%Y-%m-%d %H:%M:%S", regtime_local)
                spacesta = jsData.get('spacesta')
                birthday = jsData.get('birthday') if 'birthday' in jsData.keys(
                ) else 'nobirthday'
                sign = jsData.get('sign')
                level = jsData['level_info']['current_level']
                OfficialVerifyType = jsData['official_verify']['type']
                OfficialVerifyDesc = jsData['official_verify']['desc']
                vipType = jsData['vip']['vipType']
                vipStatus = jsData['vip']['vipStatus']
                toutu = jsData['toutu']
                toutuId = jsData['toutuId']
                coins = jsData['coins']
                log.info("Succeed get user info: " +
                         str(mid) + "\t" + str(time2 - time1))
                try:
                    proxy = get_proxy().get("proxy")
                    res = requests.get(
                        'https://api.bilibili.com/x/relation/stat?vmid=' +
                        str(mid) + '&jsonp=jsonp',
                        timeout=2,
                        proxies={"http": "http://{}".format(proxy), "https": "https://{}".format(proxy)}).text
                    viewinfo = requests.get(
                        'https://api.bilibili.com/x/space/upstat?mid=' +
                        str(mid) + '&jsonp=jsonp',
                        timeout=2,
                        proxies={"http": "http://{}".format(proxy), "https": "https://{}".format(proxy)}).text
                    js_fans_data = json.loads(res)
                    js_viewdata = json.loads(viewinfo)
                    following = js_fans_data['data']['following']
                    fans = js_fans_data['data']['follower']
                    archiveview = js_viewdata['data']['archive']['view']
                    article = js_viewdata['data']['article']['view']
                except:
                    following = 0
                    fans = 0
                    archiveview = 0
                    article = 0
            else:
                saveErrorUrl(url.replace(
                    'https://space.bilibili.com/', ''))
                log.info('no data now')
                return
            try:
                # Please write your MySQL's information.
                conn = mysqlconnect()
                cur = conn.cursor()
                cur.execute('INSERT INTO bilibili_user_info(mid, name, sex, rank, face, regtime, spacesta, \
                                birthday, sign, level, OfficialVerifyType, OfficialVerifyDesc, vipType, vipStatus, \
                                toutu, toutuId, coins, following, fans ,archiveview, article) \
                    VALUES ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s",\
                            "%s","%s","%s","%s","%s", "%s","%s","%s","%s","%s","%s")'
                            %
                            (mid, name, sex, rank, face, regtime, spacesta,
                             birthday, sign, level, OfficialVerifyType, OfficialVerifyDesc, vipType, vipStatus,
                             toutu, toutuId, coins, following, fans, archiveview, article))
                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                log.error("sqlerror"+str(e))
        else:
            saveErrorUrl(url.replace('https://space.bilibili.com/', ''))
            log.error("Error: " + url)
    except Exception as e:
        saveErrorUrl(url.replace('https://space.bilibili.com/', ''))
        log.error("formaterror"+str(e))
        log.error(e)
        pass


if __name__ == "__main__":
    pool = ThreadPool(40)
    initError(1000)
    # initUrls(5000100, 1000000)

    try:
        results = pool.map(getsource, urls)
    except Exception as e:
        log.error(e)
    pool.close()
    pool.join()
