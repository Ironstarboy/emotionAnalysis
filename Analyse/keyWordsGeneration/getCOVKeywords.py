"""
    从荔枝新闻关于新冠疫情的搜索结果中的新闻全文中利用textrank算法筛选关键词
    注意到stage0和stage1由于部分日期内荔枝新闻检索无结果，因而用当日的新浪新闻标题中提取的关键词代替
"""


from jieba import analyse
from pyecharts import options as opts
from pyecharts.charts import WordCloud
import math
import os
import re
import Date
import time
import json
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import numpy as np
import stage


stageNo = 6
path = stage.stage[stageNo]['path']
beginDate = stage.stage[stageNo]['beginDate']
print(beginDate)
endDate   = stage.stage[stageNo]['endDate']
print(endDate)
date = '1970-01-01-'
textrank = analyse.textrank

words = dict()

def run():
    date = beginDate
    i = 0
    fp = open(path + '/' + date + '/' + date + 'keywords.json', mode='r', encoding='utf-8')
    while True:
        try:
            curWords = json.load(fp)
        except Exception as e:
            print(e)
            date = Date.getNextDate(date)
            if Date.dateCmp(date, endDate) == 1:
                break
            try:
                fp = open(path + '/' + date + '/' + date + 'keywords.json', mode='r', encoding='utf-8')
            except Exception as e:
                print(e)
                continue
            continue
        print(curWords)
        for item in curWords:
            words[item[0]] = words.get(item[0], 0) + item[1]
        print(words)
        print(date + 'Finished')
        date = Date.getNextDate(date)
        print(date)
        if Date.dateCmp(date, endDate) == 1:
            print('Finished')
            break
        try:
            fp = open(path + '/' + date + '/' + date + 'keywords.json', mode='r', encoding='utf-8')
        except Exception as e:
            print(e)
            continue
        i += 1
        # if i > 30:
        #     break
    fp = open((path + '/' + 'keywords-Stage' + str(stageNo) + '.json'), mode='w', encoding='utf-8')
    wordl = sorted(words.items(), key=lambda items: items[1], reverse=True)
    # wordl = wordl[0:math.floor(i / 3)] # 只选取前面的四分之一的词汇
    wordsS = json.dumps(wordl, indent=4, separators=(',', ':'), ensure_ascii=False)
    fp.write(wordsS)
    fp.flush()


if __name__ == '__main__':
    run()