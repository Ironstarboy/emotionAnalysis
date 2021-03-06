import datetime
from fake_useragent import UserAgent
import requests
import re
from bs4 import BeautifulSoup as bs
import time
import random


def print_run_time(func):
    def wrapper(*args, **kw):
        local_time = time.time()
        func(*args, **kw)
        spendTime=int(time.time() - local_time)
        print('总耗时 {}'.format(show_time(spendTime)))
    return wrapper

def show_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)

def get_random_header():#随机头
    ua = UserAgent()
    user_agent = ua.random
    return user_agent


def get_html_text(url):
    '''获取当前url源代码'''
    sleepTime=random.uniform(1,2.33)#等待时间，不要太小吧
    time.sleep(sleepTime)

    myheader=get_random_header()

    try:
        r=requests.request("GET",url,headers={'user-agent':myheader},timeout=3)
        r.encoding='utf-8'
        #r.apparent_encoding
        return r.text
    except Exception as e:
        return ''


'''
<div class="box-result clearfix" data-sudaclick="blk_result_index_3">
			
					<h2><a href="https://news.sina.com.cn/o/2019-12-26/doc-iihnzahk0127138.shtml" target="_blank">国家卫健委：目前全国传染病<font color="red">疫情</font>形势总体平稳</a>
					<span class="fgray_time">中国新闻网 2019-12-26 15:23:32</span></h2>
				<div class="r-img">
					<a href="https://news.sina.com.cn/o/2019-12-26/doc-iihnzahk0127138.shtml" target="_blank" class="a-img"><img alt="" class="left_img" width="120" onload="a_r_i(this);" onerror="set_right_url3(this,'http:\/\/n.sinaimg.cn\/spider20191226\/145\/w540h405\/20191226\/1c81-imfiehq4029080.jpg');" src="http://n.sinaimg.cn/spider20191226/145/w540h405/20191226/1c81-imfiehq4029080.jpg" /></a>
				</div>
			
				<div class="r-info">
					<p class="content"> 　　国家卫健委：目前中国传染病<font color="red">疫情</font>形势总体平稳  中新社北京12月26日电 (记者 李亚南)中国国家卫生健康委员会疾病预防控制局副局长王斌26日在北京表示</p>
				</div>
			</div>
'''
def getOutcomeHtmlText(htmltext):#得到包含搜索结果源代码文本 列表,格式如上
    soup = bs(htmltext, 'html.parser',)
    eachOutcomeText=soup.find_all('div',attrs={'class':"box-result clearfix"}) #返回每个搜索结果的对应源代码部分
    return eachOutcomeText


def save_outcome_info2csv(htmlText,filename):
    title = ''
    jumpUrl=''
    source_and_time=''
    source=''
    publish_time=''
    try:
        title = re.search('target="_blank">(.*?)</a>', htmlText).group(1).strip().replace('<font color="red">','').replace('</font>','')
        jumpUrl = re.search('<a href="(.*?)" target="_blank">',htmlText).group(1).strip()
        source_and_time=re.search('<span class="fgray_time">(.*?)</span>',htmlText).group(1).strip()
        spaceIndex=source_and_time.index(' ')
        source=source_and_time[:spaceIndex]
        publish_time=source_and_time[spaceIndex+1:spaceIndex+11]
    except Exception as e:
        print(e)

    with open(filename,'a+',encoding='utf-8') as f: #可能会出现编码错误，默认gbk好像
        try:
            f.write(title+',')
            f.write(jumpUrl+',')
            f.write(source+',')
            f.write(publish_time+'\n')
        except:
            f.write('\n')




def urlParam(stime, etime, page, keyword='%e8%82%ba%e7%82%8e', my_range='title'):#range：all全文 title标题
    '''time:2020-01-01'''
    out='https://search.sina.com.cn/?q={keyword}&c=news&range={my_range}&size=20&time=2020&stime={stime}%2000:00:00&etime={etime}%2023:59:59&num=10&page={page}'.format(keyword=keyword,my_range=my_range, stime=stime, etime=etime, page=page)
    return out


def timeitr(smonth,sday,emonth,eday,year=2020): #遍历一定范围内的日期，返回日期字符串列表，闭区间
    begin = datetime.date(year, smonth, sday)
    end = datetime.date(year, emonth, eday)
    outDaylst=[]
    for i in range((end - begin).days + 1):
        outday = begin + datetime.timedelta(days=i)
        outDaylst.append(str(outday))
    return outDaylst


@print_run_time
def run():
    #这里修改参数
    keyword='肺炎'
    my_range='all'#全文:all，标题:title
    fileName=r'test.csv'
    days=timeitr(1,18,1,18,2020)#闭区间，跨年需要分2段



    for ymd in days:#ymd:year month day
        for page in range(1):
            currentPageUrl=urlParam(ymd,ymd,str(page),keyword,my_range)
            currentPageText=get_html_text(currentPageUrl)
            outcomeTextList=getOutcomeHtmlText(currentPageText)
            for i in range(len(outcomeTextList)):
                text=str(outcomeTextList[i]).replace('\n','')
                save_outcome_info2csv(text,fileName)
        print(ymd+' done!')


    print('done!')

if __name__=='__main__':


    run()







