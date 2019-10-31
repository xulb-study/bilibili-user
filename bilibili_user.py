# -*-coding:utf8-*-

import requests
import json
import random
import pymysql

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
    return requests.get("http://my_propxy:5010/get/").json()


def delete_proxy(proxy):
    requests.get("http://my_propxy:5010/delete/?proxy={}".format(proxy))


def getUserInfo(head, payload):
    retry_count = 2
    proxy = get_proxy().get("proxy")
    while retry_count > 0:
        try:
            return requests \
                .session() \
                .post('http://space.bilibili.com/ajax/member/GetInfo',
                      headers=head,
                      data=payload,
                      proxies={"http": "http://{}".format(proxy)}) \
                .text
        except Exception as e:
            retry_count -= 1
            # 出错2次, 删除代理池中代理
            delete_proxy(proxy)
            log.info("删除代理池中代理"+e)

    return None


time1 = time.time()

urls = []

# Please change the range data by yourself.

for i in range(0, 10000):
    url = 'https://space.bilibili.com/' + str(i)
    urls.append(url)

    def getsource(url):
        log.info("执行开始")
        payload = {
            '_': datetime_to_timestamp_in_milliseconds(datetime.datetime.now()),
            'mid': url.replace('https://space.bilibili.com/', '')
        }
        ua = random.choice(uas)
        head = {
            'User-Agent': ua,
            'Referer': 'https://space.bilibili.com/' + str(i) + '?from=search&seid=' + str(random.randint(10000, 50000))
        }

        jscontent = getUserInfo(head, payload)
        if jscontent == None:
            log.error("无效的地址"+url)
            jscontent = getUserInfo(head, payload)
            if jscontent == None:
                pass
        time2 = time.time()
        try:
            jsDict = json.loads(jscontent)
            statusJson = jsDict['status'] if 'status' in jsDict.keys(
            ) else False
            if statusJson == True:
                if 'data' in jsDict.keys():
                    jsData = jsDict['data']
                    mid = jsData['mid']
                    name = jsData['name']
                    sex = jsData['sex']
                    rank = jsData['rank']
                    face = jsData['face']
                    regtimestamp = jsData['regtime']
                    regtime_local = time.localtime(regtimestamp)
                    regtime = time.strftime("%Y-%m-%d %H:%M:%S", regtime_local)
                    spacesta = jsData['spacesta']
                    birthday = jsData['birthday'] if 'birthday' in jsData.keys(
                    ) else 'nobirthday'
                    sign = jsData['sign']
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
                            proxies={"http": "http://{}".format(proxy)}).text
                        viewinfo = requests.get(
                            'https://api.bilibili.com/x/space/upstat?mid=' +
                            str(mid) + '&jsonp=jsonp',
                            proxies={"http": "http://{}".format(proxy)}).text
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
                    log.info('no data now')
                try:
                    # Please write your MySQL's information.
                    conn = pymysql.connect(
                        host='eam-mysql', user='root', passwd='123456', db='bilibili', charset='utf8')
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
                except Exception as e:
                    log.error(e)
            else:
                log.error("Error: " + url)
        except Exception as e:
            log.error(e)
            pass

if __name__ == "__main__":
    pool = ThreadPool()
    try:
        results = pool.map(getsource, urls)
    except Exception as e:
        log.error(e)

    pool.close()
    pool.join()
