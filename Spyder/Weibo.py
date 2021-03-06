import json
import requests
import time
import random
from pyquery import PyQuery as pq

limitOfErrors = 10
startPage = 0


def run():
    BrowserHeaders = {
        'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    }

    # 微博用户主页api通用url
    url = 'https://m.weibo.cn/api/container/getIndex'

    # 所有要爬的用户的uid
    uid_list = ['2212518065']

    # 最外层循环，每次爬取完成一个用户
    for uid in uid_list:
        # url+parm得到特定用户主页API地址
        param = {
            'type': 'uid',
            'value': uid,
        }
        # 发起请求，得到用户主页
        response = requests.get(url=url, params=param, headers=BrowserHeaders)
        homepage = response.json()

        userInfo = {
            '微博用户名': homepage['data']['userInfo']['screen_name'],
            '微博主页地址': homepage['data']['userInfo']['profile_url'],
            '微博认证名': homepage['data']['userInfo']['verified_reason'],
            '微博说明': homepage['data']['userInfo']['description'],
            '关注数量': homepage['data']['userInfo']['follow_count'],
            '粉丝数量': homepage['data']['userInfo']['followers_count'],
        }

        print(userInfo)
        # 将该字典存入文件并覆盖原文件，如原先无该文件则创建
        with open('dingxiangdoctor.json', 'w', encoding='utf-8') as fp:
            fp.write('[\n')
            fp.write(json.dumps(userInfo, indent=4, separators=(',', ':'), ensure_ascii=False))
            # fp.write('\n')
        fp = open('dingxiangdoctor.json', 'a', encoding='utf-8')

        # 取containerid
        tab_list = homepage['data']['tabsInfo']['tabs']
        containerid = ''

        for tab in tab_list:
            if (tab['tabKey'] == 'weibo'):
                containerid = tab['containerid']

        # 将containerid参数加入parm时通过url+parm就可以爬取到包含该user发布微博内容的第一个数据包，而后可以根据该数据包拿到接下来的ID
        param['containerid'] = containerid

        i = 0  # 本次运行期间已爬取的微博数量
        pageNo = startPage
        errCount = 0
        page = homepage

        cookie = input('Input First Cookie\n')
        BrowserHeaders['cookie'] = cookie

        # 不断发起请求，获取用户微博内容
        while True:
            pageNo += 1
            param['page'] = str(pageNo)
            response = requests.get(url=url, params=param, headers=BrowserHeaders)
            page = response.json()
            # print(page)
            print('' + str(pageNo))

            # 每一次循环对应每一页内第几条微博
            for card in page['data']['cards']:
                try:
                    if card['card_type'] == 9:
                        print(card['mblog']['created_at'])
                        content_dic = {
                            "微博地址:": card['scheme'],
                            "发布时间": card['mblog']['created_at'],
                            "转发数": card['mblog']['reposts_count'],
                            "评论数": card['mblog']['comments_count'],
                            "点赞数:": card['mblog']['attitudes_count'],
                            "微博内容:": get_weibo_content(card['mblog']['id']),
                            "评论": get_comment(card['mblog']['mid'], card['scheme'], BrowserHeaders['cookie'])
                        }
                        fp.write(',\n')
                        fp.write(json.dumps(content_dic, indent=4, separators=(',', ':'), ensure_ascii=False))
                        fp.flush()
                        print('已爬取' + str(i) + ' 条微博')
                        print(pageNo)
                        i += 1
                except Exception as e:
                    print(e)
                    errCount += 1
                    if errCount == limitOfErrors:  # 达到一定数量的错误数后要求
                        print('爬取当前出错页面是' + str(pageNo))
                        BrowserHeaders['cookie'] = input('New Cookie\n')
                        errCount = 0
                        continue
                # 注意到最后得手动改一下结尾才能变成json（补一个]）


# 获取微博正文
def get_weibo_content(id):
    url = 'https://m.weibo.cn/statuses/extend'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    }
    param = {
        'id': id
    }
    response = requests.get(url=url, params=param, headers=headers)
    return pq(response.json()['data']['longTextContent']).text()


# 获取微博评论，默认爬取全部
def get_comment(mid, scheme, cookie):
    url = 'https://m.weibo.cn/comments/hotflow'
    headers = {
        'Accept': 'application / json, text / plain, * / *',
        'MWeibo-Pwa': '1',
        'Referer': scheme,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'X-XSRF-TOKEN': 'c7e587',
        'cookie': cookie
    }
    param = {
        'id': mid,
        'mid': mid,
        'max_id_type': '0'
    }

    # 获取第一个评论数据包
    response = requests.get(url=url, params=param, headers=headers)
    comment_page = response.json()

    # 此处代表获得了一个空包，可能由于各种错误导致
    if comment_page['ok'] == 0:
        return []

    comment_content = []

    for user in comment_page['data']['data']:
        comment_content.append(pq(user['text']).text())

    # 只要还有数据就继续爬取
    if comment_page['data']['max_id'] != 0:
        while True:
            try:
                param['max_id'] = comment_page['data']['max_id']  # 获取
                response = requests.get(url=url, params=param, headers=headers)
                comment_page = response.json()
                if comment_page['ok'] == 0 or comment_page['data']['max_id'] == 0:  # 如果是空包或者没有更多内容则跳出
                    break
                for user in comment_page['data']['data']:
                    comment_content.append(pq(user['text']).text())
                sleepTime = random.uniform(1, 2.13)
                time.sleep(sleepTime)
            except Exception as e:
                print(url)
                print(e)
                print("爬取评论出错，可能需要更新Cookie")
                headers['Cookie'] = input('Cookie')
                # headers['TOKEN'] = input('token')
                continue
    return comment_content


if __name__ == "__main__":
    run()
