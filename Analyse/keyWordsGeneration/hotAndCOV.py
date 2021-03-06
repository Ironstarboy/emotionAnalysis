import numpy as np
import matplotlib.pyplot as plt
import math
import os
import re
import Date
import time
import json
import jieba
import stage
import splitWeibo
from scipy.optimize import curve_fit
from scipy.stats import chi2_contingency

stageNo = 4
path = stage.stage[stageNo]['path']
beginDate = stage.stage[stageNo]['beginDate']
print(beginDate)
endDate = stage.stage[stageNo]['endDate']
print(endDate)
date = '1970-01-01-'

keywords = []
scoreList = []
starList = []
forwardList = []
commentList = []
allWeibo = []
weiboNumByDate = []
COVWeiboNumList = []
minimenCOV = 0

starRatio = []
forwardRatio = []
commentRatio = []
COVIndexByDate = []

def run():
    plt.rcParams['font.sans-serif'] = ['SimHei']
    loadALlWeibo()


def loadALlWeibo():
    global allWeibo
    global commentList
    global forwardList
    global starList
    global scoreList
    minimenCOV = getLimit()
    date = beginDate
    while Date.dateCmp(date, endDate) != 1:
        try:
            loadSingleDateWeibo(date)
            print(date + ' Loading Finished!')
        except Exception as e:
            print(e)
        date = Date.getNextDate(date)
        # break
    allWeibo = sorted(allWeibo, key=lambda x: x['疫情相关度'])
    scoreList = [x['疫情相关度'] for x in allWeibo]
    commentList = [x['评论数'] for x in allWeibo]
    starList = [x['点赞数'] for x in allWeibo]
    forwardList = [x['转发数'] for x in allWeibo]
    drawPic()
    # hotDegree = [getHot(x) for x in allWeibo]


def loadSingleDateWeibo(date):
    with open((path + '/' + date + '/' + date + 'blog-Scored.json') , mode='r', encoding='utf-8') as fp:
        curDateWeiboList = json.load(fp)
        for item in curDateWeiboList:
            allWeibo.append(item)
        return curDateWeiboList

def loadSingleDateCOVWeibo(date):
    with open((path + '/' + date + '/' + date + 'blog-COV.json') , mode='r', encoding='utf-8') as fp:
        curDateWeiboList = json.load(fp)
        for item in curDateWeiboList:
            allWeibo.append(item)
        return curDateWeiboList


def getLimit():
    with open((path + '/' + 'stageCOVWeiboByImportance.json') , mode='r', encoding='utf-8') as fp:
        curDateWeiboList = json.load(fp)
        length = len(curDateWeiboList)
        return curDateWeiboList[length - 1]['疫情相关度']


def drawPic():
    xplot = [x for x in range(1, len(allWeibo) + 1)]
    starList1 = [math.log10(x + 1) * 40 for x in starList]
    commentList1 = [math.log10(x + 1) * 40 for x in commentList]
    forwardList1 = [math.log10(x + 1) * 40 for x in forwardList]
    plt.scatter(xplot, starList1, color="g", s=5, marker=".", linewidth=1, label='点赞数')
    plt.scatter(xplot, commentList1, color="y", s=5, marker=".", linewidth=1, alpha=0.9, label='评论数')
    plt.scatter(xplot, forwardList1, color="b", s=5, marker=".", linewidth=1, alpha=0.9, label='转发数')
    plt.scatter(xplot, scoreList, s=2, color="5", marker=".", linewidth=1, alpha=0.9, label='疫情相关度')
    plt.rcParams['figure.dpi'] = 300
    plt.xlabel = '微博数量（从左到右递增）'
    plt.legend()
    plt.savefig(path + '/SaveTest-拟合.png', dpi=300)
    # plt.show()


# 计算某条微博的热度指标
# def getHot(x):
#     comment = x['评论数']
#     return x


def getHotRatioByDate():
    date = beginDate
    while Date.dateCmp(date, endDate) != 1:
        try:
            allCurDateWeibo = loadSingleDateWeibo(date)
            allCurDateCOVWeibo = loadSingleDateCOVWeibo(date)

            sumStar = 0
            sumComment = 0
            sumForward = 0

            COVStar = 0
            COVComment = 0
            COVForward = 0
            sumCOV = 0
            for item in allCurDateWeibo:
                sumStar += item['点赞数']
                sumComment += item['评论数']
                sumForward += item['转发数']
            for item in allCurDateCOVWeibo:
                sumCOV += item['疫情相关度']
                COVStar += item['点赞数']
                COVComment += item['评论数']
                COVForward += item['转发数']
            print(date + ' Loading Finished!')
            starRatio.append(COVStar / sumStar)
            commentRatio.append(COVComment / sumComment)
            forwardRatio.append(COVForward / sumForward)
            COVIndexByDate.append(sumCOV)
        except Exception as e:
            print(e)
        date = Date.getNextDate(date)
        # break
    print(forwardRatio)
    print(commentRatio)
    print(starRatio)
    drawHotRatioByDate()


def drawHotRatioByDate():
    global COVIndexByDate
    plt.rcParams['font.sans-serif'] = ['SimHei']
    xplot = [x for x in range(1, len(COVIndexByDate) + 1)]
    COVIndexByDate = [x / 1000 for x in COVIndexByDate]
    # commentList1 = [math.log10(x + 1) * 40 for x in commentList]
    # forwardList1 = [math.log10(x + 1) * 40 for x in forwardList]
    print(len(xplot))
    print(len(starRatio))
    print(len(commentRatio))
    print(len(forwardRatio))
    print(len(COVIndexByDate))
    plt.scatter(xplot, starRatio, color="g", s=8, marker=".", linewidth=1, label='点赞比例')
    plt.scatter(xplot, forwardRatio, color="y", s=8, marker=".", linewidth=1, alpha=0.9, label='转发比例')
    plt.scatter(xplot, commentRatio, color="b", s=8, marker=".", linewidth=1, alpha=0.9, label='评论比例')
    plt.scatter(xplot, COVIndexByDate, s=8, color="r", marker=".", linewidth=1, alpha=0.9, label='疫情相关度 / 200')
    plt.rcParams['figure.dpi'] = 300
    plt.xlabel = '微博数量（从左到右递增）'
    plt.legend()
    plt.savefig(path + '/SaveTest-热度.png', dpi=300)
    # plt.show()
#

if __name__ == '__main__':
    # run()
    getHotRatioByDate()