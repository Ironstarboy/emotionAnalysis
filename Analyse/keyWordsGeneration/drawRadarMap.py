# 导入第三方模块
import numpy as np
import matplotlib.pyplot as plt
import math
import Date
import stage
import json

stageNo = 5
path = stage.stage[stageNo]['path']
beginDate = stage.stage[stageNo]['beginDate']
print(beginDate)
endDate = stage.stage[stageNo]['endDate']
print(endDate)
date = '1970-01-01-'


def run():
    date = beginDate
    while Date.dateCmp(date, endDate) != 1:
        try:
            drawRadar(date)
            print(date + ' Finished!')
        except Exception as e:
            print(e)
        date = Date.getNextDate(date)
        # break
    # drawRadar(endDate)


def drawRadar(date):
    # 中文和负号的正常显示
    plt.clf()
    plt.rcParams['font.sans-serif'] = 'Microsoft YaHei'
    plt.rcParams['axes.unicode_minus'] = False

    # 使用ggplot的绘图风格
    plt.style.use('ggplot')

    # 构造数据
    # values = [3.2, 2.1, 3.5, 2.8, 3]
    fp = open('weibo' + 'Stage2' + 'Score/' + date[0:10] + 'weiboScore.csv', mode='r', encoding='utf-8')
    values = getValuefromFile(fp)
    # print(values)
    feature = ['乐', '好', '怒', '哀', '惧', '恶', '惊']
    N = len(values[0])
    # print(values[0])
    print('N ' + str(N))
    Num = len(values)
    average = values[0]
    for i in range(0, N):
        for j in range(1, Num):
            average[i] += values[j][i]
        average[i] /= Num

    # 设置雷达图的角度，用于平分切开一个圆面
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
    # print(angles)

    # 为了使雷达图一圈封闭起来，需要下面的步骤
    values_ = []
    for item in values:
        item1 = np.concatenate((item, [item[0]]))
        # print(item)
        values_.append(item1)
    values = values_
    angles = np.concatenate((angles, [angles[0]]))
    average = np.concatenate((average, [average[0]]))
    # print(angles)

    # 绘图
    fig = plt.figure()
    ax = fig.add_subplot(111, polar=True)
    # 绘制折线图
    for item in values:
        # print(len(angles), len(item))
        # print(item)
        ax.plot(angles, item, '', linewidth=0.1, color='y', label='e', alpha=0)
        # print('filled Item' + str(item))
        # 填充颜色
        ax.fill(angles, item, color='y', alpha=0.05)
    # 绘制第二条折线图
    ax.plot(angles, average, '', linewidth=2, color='r', alpha=0.9, label='')
    ax.fill(angles, average, color='r',  alpha=0.25)
    for a, b in zip(angles, average):
        plt.text(a, b, (round(b, 2)), ha='center', va='bottom', color='black' , fontsize=10)
    # 添加每个特征的标签
    ax.set_thetagrids(angles * 180 / np.pi, feature)
    # 设置雷达图的范围
    maxN = max([max(x) for x in values])
    ax.set_ylim(-1, maxN)
    # 添加标题
    plt.title(date + '疫情相关重点微博评论心态分析')

    # 添加网格线
    ax.grid(True)
    # 设置图例
    # plt.legend(loc='best')

    # fp = open('jstvscore/' + date[0:10] + 'jstvScore.csv', mode='r', encoding='utf-8')
    # 显示图形
    plt.savefig(str(stage.stage[stageNo]['path'] + '/' + date + '/' + date + 'weiboEmotion.png'), dpi=200)


def drawAllPic():
    # 中文和负号的正常显示
    plt.clf()
    plt.rcParams['font.sans-serif'] = 'Microsoft YaHei'
    plt.rcParams['axes.unicode_minus'] = False

    # 使用ggplot的绘图风格
    plt.style.use('ggplot')

    values = []
    date = beginDate
    while Date.dateCmp(date, endDate) != 1:
        try:
            fp = open('weibo' + 'Stage2' + 'Score/' + date[0:10] + 'weiboScore.csv', mode='r',
                      encoding='utf-8')
            tmpDateValues = getValuefromFile(fp)
            for item in tmpDateValues:
                values.append(item)
            print(date + ' Finished!')
        except Exception as e:
            print(e)
        date = Date.getNextDate(date)

    # print(values)
    feature = ['乐', '好', '怒', '哀', '惧', '恶', '惊']
    N = len(values[0])
    # print(values[0])
    print('N ' + str(N))
    Num = len(values)
    average = values[0]
    for i in range(0, N):
        for j in range(1, Num):
            average[i] += values[j][i]
        average[i] /= Num

    # 设置雷达图的角度，用于平分切开一个圆面
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
    # print(angles)

    # 为了使雷达图一圈封闭起来，需要下面的步骤
    values_ = []
    for item in values:
        item1 = np.concatenate((item, [item[0]]))
        # print(item)
        values_.append(item1)
    values = values_
    angles = np.concatenate((angles, [angles[0]]))
    average = np.concatenate((average, [average[0]]))
    # print(angles)

    # 绘图
    fig = plt.figure()
    ax = fig.add_subplot(111, polar=True)
    # 绘制折线图
    for item in values:
        # print(len(angles), len(item))
        # print(item)
        ax.plot(angles, item, '', linewidth=0.1, color='y', label='e', alpha= 0.0)
        # print('filled Item' + str(item))
        # 填充颜色
        ax.fill(angles, item, color='y', alpha= 0.01)
    # 绘制第二条折线图
    ax.plot(angles, average, '', linewidth=2, color='r', alpha=0.9, label='')
    ax.fill(angles, average, color='r',  alpha=0.25)

    # 添加每个特征的标签
    ax.set_thetagrids(angles * 180 / np.pi, feature)
    # 设置雷达图的范围
    maxN = max([max(x) for x in values])
    ax.set_ylim(-1, maxN)
    # 添加标题
    plt.title('阶段 ' + str(stageNo) + ' 疫情相关重点微博评论心态分析')
    for a, b in zip(angles, average):
        plt.text(a, b, (round(b, 2)), ha='center', va='bottom', color='black' , fontsize=10)
    # 添加网格线
    ax.grid(True)
    # 设置图例
    # plt.legend(loc='best')

    # fp = open('jstvscore/' + date[0:10] + 'jstvScore.csv', mode='r', encoding='utf-8')
    # 显示图形
    plt.savefig(str(stage.stage[stageNo]['path'] + '/weiboEmotion.png'), dpi=200)
    plt.show()


def getValuefromFile(fp):
    tmpLine = fp.readline()
    desList = tmpLine.split(',')[1:8]
    valuesList = []
    tmpLine = fp.readline()
    while tmpLine != '':
        rawValue = [math.log2(float(x) + 1) for x in tmpLine.split(',')[1:8]]
        valuesList.append(rawValue)
        tmpLine = fp.readline()
        # print(rawValue)
    return valuesList


def getPolarfromFile(fp):
    tmpLine = fp.readline()
    des = tmpLine.split(',')[0]
    valuesList = []
    tmpLine = fp.readline()
    while tmpLine != '':
        rawValue = float(tmpLine.split(',')[0])
        valuesList.append(rawValue)
        tmpLine = fp.readline()
        # print(rawValue)
    return valuesList


def drawPolarByDate():
    # 中文和负号的正常显示
    plt.clf()
    plt.rcParams['font.sans-serif'] = 'Microsoft YaHei'
    plt.rcParams['axes.unicode_minus'] = False

    averagePolarList = []

    date = beginDate
    while Date.dateCmp(date, endDate) != 1:
        try:
            fp = open('weibo' + 'Stage2' + 'Score/' + date[0:10] + 'weiboScore.csv', mode='r', encoding='utf-8')
            curPolarList = getPolarfromFile(fp)
            curPolar = np.average(curPolarList)
            averagePolarList.append(curPolar)
            print(date + ' Finished!')
        except Exception as e:
            print(e)
        date = Date.getNextDate(date)
    print('Average' + str(averagePolarList))
    xplot = [x for x in range(1, len(averagePolarList) + 1)]
    avgList = []
    for item in averagePolarList:
        if item > 0:
            avgList.append(math.log2(item))
        else:
            avgList.append(-math.log2(-item))
    plt.xticks(np.arange(0, len(avgList) + 2, 2))
    plt.plot(xplot, avgList, color="b", marker=".", linewidth=1, alpha=0.9, label='极性')
    plt.title('阶段 ' + str(stageNo) + ' 疫情相关重点微博评论心态分析')
    plt.axhline(y=0, color="purple")
    plt.legend()
    plt.savefig(str(stage.stage[stageNo]['path'] + '/weiboPolar.png'), dpi=200)
    plt.show()



if __name__ == '__main__':
    # run()
    # drawAllPic()
    drawPolarByDate()