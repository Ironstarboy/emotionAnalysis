import datetime
from fake_useragent import UserAgent
import requests
import re
from bs4 import BeautifulSoup as bs
import time
import random
import newsSpyder


def urlParam(page, keyword='肺炎'):
    '''time:2020-01-01'''
    out='https://so.jstv.com/?keyword={keyword}&page={page}'.format(keyword=keyword,page=page)
    return out


def getOutcomeHtmlText(htmltext):
    'soup得到搜索页面对应结果的源代码部分 列表'
    soup = bs(htmltext, 'html.parser', )
    eachOutcomeText = soup.find_all('div', attrs={'class': "lzxw_per_r"})  # 返回每个搜索结果的对应源代码部分，这个class会漏信息，父级又多信息可恶
    return eachOutcomeText


def get_content_htmlText(htmlText):
    '获取新闻正文网页的源代码中正文部分，包含标题'
    soup = bs(htmlText, 'html.parser', )
    contentText = soup.find_all('div', attrs={'class': "article"})  # 返回每个搜索结果的对应源代码部分

    return contentText



def write_jumpUrl2csv(htmlText,filename):
    jumpUrl = ''
    try:
        jumpUrl = re.search('<a href="(.*?)" target="_blank">', htmlText).group(1).strip()#每一页会有部分搜索结果无法匹配
    except Exception as e:
        jumpUrl=''

    with open(filename, 'a+',encoding='utf-8') as f:  # 可能会出现编码错误
        try:
            f.write(jumpUrl + '\n')
        except:
            pass
    pass


def save_newsDetial(news_wholehtml,article_htmltext,fileName): #article_htmltext:soup之后的一小段text
    '存标题，正文，时间，来源到csv'
    title=''
    content=''
    publish_time=''
    source=''

    try:
        title=re.search('<title>(.*?)</title>',news_wholehtml[:300]).group(1)

        something_with_content = re.findall('<p( cms-style="font-L")?>(.*?)</p>', article_htmltext)#匹配下来是元组列表，且包含<p>\u3000等冗余信息
        content_with_word=''
        for tup in something_with_content:
            content_with_word += tup[1]
        content = re.sub('[\u3000]|[</?span>]|(</?strong>)|( )', '', content_with_word)


        publish_time_withClock=re.search('<span class="time">(.*?) </span>',article_htmltext).group(1)#匹配下来带时分秒
        spaceIndex=publish_time_withClock.index(' ')
        publish_time=publish_time_withClock[:spaceIndex]

        source=re.search('<span class="source">来源：(.*?)</span>',article_htmltext).group(1)
    except Exception as e:
        print('新闻正文 正则匹配错误')


    with open(fileName,'a+',encoding='utf-8') as f:
        f.write(publish_time + ',')
        f.write(title+',')
        f.write(source+',')
        f.write(content + '\n')


def save_outComeUrl(spage,epage,keyword,outcomeUrl_filename):
    ' 先把2000页的的结果的url存到本地文件'
    for pageNum in range(spage,epage+1):
        current_pageOutcome_url = urlParam(str(pageNum), keyword)  # 获取当前页数和keyword的url
        current_pageOutcome_text = newsSpyder.get_html_text(current_pageOutcome_url)  # 获取当前搜索结果页面的源代码
        outcomePrecise_htmlText_list = getOutcomeHtmlText(current_pageOutcome_text)

        for outcomePrecise_htmltext in outcomePrecise_htmlText_list:
            write_jumpUrl2csv(str(outcomePrecise_htmltext).replace('\n', ''), outcomeUrl_filename)
    print("搜索结果跳转链接已经爬取并保存！")



@newsSpyder.print_run_time
def run():
    #这里修改参数
    keyword='肺炎'
    total_page=2000#一般有几千页
    spage = 1#给多台机器部署的时候，修改这里的爬取 起始页码 和 中止页码,闭区间
    epage = 200
    outcomeUrl_filename='jstv_肺炎_搜索结果链接_{}-{}.csv'.format(spage,epage)#存所有搜索结果跳转链接的文件
    newsDetail_filename='jstv_肺炎_{}-{}.csv'.format(spage,epage)#存新闻正文等细节新的文件


    save_outComeUrl(spage,epage,keyword,outcomeUrl_filename)


    count=0
    with open(outcomeUrl_filename,'r', encoding='utf-8') as f:
        urllines = f.readlines()
    for url in urllines:
        if url!='':
            count+=1
            url=url.replace('\n','')
            text=newsSpyder.get_html_text(url)
            content_htmltext_list=get_content_htmlText(text)
            for content_htmltext in content_htmltext_list:
                save_newsDetial(text,str(content_htmltext).replace('\n',''),newsDetail_filename)
        if (count%50)==0:
            print('已爬取{}个正文'.format(count))

    print('done!')

if __name__=='__main__':

    run()




