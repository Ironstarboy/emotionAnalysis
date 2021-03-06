"""
从荔枝新闻的正文中提取关键词分天存到对应的文件夹中，考虑到疫情初期基本没有什么疫情相关新闻（2020年1月1日以前），
故改用新浪新闻标题生成2019年12月部分的关键词
"""

from jieba import analyse
from pyecharts import options as opts
from pyecharts.charts import WordCloud
import math
import os
import re
import Date
import time

# 汉字包
hanziS = u"[\u4e00-\u9fa5]+"
hanzi = re.compile(hanziS)
textrank = analyse.textrank  # 引入jieba中的TextRank
beginDate = '2019-12-04-'
endDate = '2020-1-1-'

# 特殊停用词
ExtraStopWords = ['荔枝', '新闻', 'trog']

# TODO
def run():
    date = beginDate
    i = 0
    while True:
        filePath = "jstv/" + date + "/" + "jstvRAW.csv"
        print(filePath)
        text = readNews(filePath)
        if text == '':
            date = Date.getNextDate(date)
            continue
        keywords = textrank(text, topK=36, withWeight=True, withFlag=True)
        print(keywords)
        words = []
        for item in keywords:
            a = list()
            items = str()
            curWord = str(item[0]).split('/')[0]
            if curWord in ExtraStopWords:
                continue
            a.append(curWord)
            a.append(math.floor((item[1] * 100)))
            words.append(tuple(a))
        # print(words)
        wordsS = str(words)
        wordsS = wordsS.replace("'", '"')
        wordsS = wordsS.replace("(", '[')
        wordsS = wordsS.replace(")", ']')
        print(wordsS)
        outPath = "jstv/" + date + "/" + date + "keywords.json"
        with open(outPath, mode='w', encoding='utf-8') as f3:
            f3.write(wordsS)
        fig = wordcloud_base(words)
        figRute = 'jstv/' + date + '/' + date + 'keywords.html'
        fig.render(figRute)
        date = Date.getNextDate(date)
        print(date)
        time.sleep(3)
        if Date.dateCmp(date, endDate) == 1 or i > 1000:
            break
        i += 1


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# 直接返回单个新闻的全部内容
def readNews(filepath):
    outContent = ""
    try:
        with open(filepath, mode='r' , encoding='utf-8') as f:
            # for i in range(0, 100):
            #     outContent += f.readline()
            outContent = f.read()
    except Exception as e:
        print("文件不存在")
        return ''
    return outContent


def wordcloud_base(words) -> WordCloud:
    c = (
        WordCloud()
            .add("", words, word_size_range=[20, 100], shape='roundRect')  # SymbolType.ROUND_RECT
            .set_global_opts(title_opts=opts.TitleOpts(title='WordCloud词云'))
    )
    return c


# 生成按日区分的荔枝新闻原文，并建立好后续处理所需要用到的文件夹
def splitJSTVByDate(filepath):
    with open(filepath, mode='r', encoding='utf-8') as f:
        date = '1970-01-01'
        f2 = open('jstv/Begin.data', mode='w', encoding='utf-8')
        curLine = 1
        while True:
            tmpLine = f.readline()
            if (tmpLine == ""):
                break
            print(curLine)
            curLine += 1
            tmpItems = tmpLine.split(',')
            tmpDate = Date.getDate(tmpItems[0])
            if (tmpDate != date):
                f2.write(tmpLine)
                try:
                    os.mkdir(('jstv/' + tmpDate))
                except Exception as e:
                    print(e)
                    continue
                date = tmpDate
                f2 = open(file=('jstv/' + tmpDate + '/jstvRAW.csv'), mode='w+', encoding='utf-8')
            else:
                f2.write(tmpLine)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run()
    #  splitJSTVByDate("jstv/jstv_2001-2800.csv") 对所有源文件操作一次


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
