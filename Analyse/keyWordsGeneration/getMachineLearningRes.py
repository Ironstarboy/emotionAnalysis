
import numpy as np
import matplotlib.pyplot as plt
import math
import os
import re
import Date
import time
import json
import stage
import splitWeibo


path = 'stage3/2020-02-21-/2020-02-21-blog.json'
score_path = 'stage3/2020-02-21-/test_result_oneday.txt'
out_path = 'stage3/2020-02-21-/valuedBlog.json'

allWeibo = []

def run():
    fp =  open(path, mode='r', encoding='utf-8')
    fp2 = open(score_path, mode='r', encoding='utf-8')
    allWeibo = json.load(fp)
    curPositive = 0
    curNegative = 0
    curMid = 0
    for weibo in allWeibo:
        num = len(weibo['评论'])
        for i in range(0, num):
            line = fp2.readline()
            possibility = line.split(' ')
            pos = float(possibility[0])
            neg = float(possibility[1])
            if (pos - neg) > 0.1:
                curPositive += 1
            elif (neg - pos) < 0.1:
                curNegative += 1
            else:
                curMid += 1
        weibo['积极评论数'] = curPositive
        weibo['消极评论数'] = curNegative
        weibo['中性评论数'] = curMid
    fp3 = open(out_path, mode='w', encoding='utf-8')
    json.dump(allWeibo, fp3, indent=4, separators=(',', ':'), ensure_ascii=False)



if __name__ == '__main__':
    run()