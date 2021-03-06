"""
    画散点图的例程
"""

import matplotlib.pyplot as plt
import numpy as np
import json

path = 'jstv'
beginDate = '2019-12-08-'
endDate   = '2019-12-26-'
date = '1970-01-01-'


def run():
    filePath = path + '/' + 'keywords-Stage1.json'
    fp = open(filePath, mode='r', encoding='utf-8')
    a = json.load(fp)
    plt.rcParams['font.sans-serif'] = ['SimHei']  # for Chinese characters
    plt.rcParams['figure.dpi'] = 300
    plt.xlabel = '横坐标'

    x = [i[0] for i in a]
    y = [i[1] for i in a]
    maxN = max(y)
    y = [i / maxN for i in y]
    x = x[0:15]
    y = y[0:15]
    plt.plot(x, y, color="r", linestyle="-", marker="^", linewidth=1)
    plt.show()


if __name__ == '__main__':
    run()