# coding: utf-8
import math
import sys
import gzip
from collections import defaultdict
import datetime
from itertools import product
import jieba
import csv
import pandas as pd
import json
import os


class Struct(object):
    def __init__(self, word, sentiment, pos, value, class_value):
        self.word = word
        self.sentiment = sentiment
        self.pos = pos
        self.value = value
        self.class_value = class_value


class Result(object):
    def __init__(self, score, score_words, not_word, degree_word):
        self.score = score
        self.score_words = score_words
        self.not_word = not_word
        self.degree_word = degree_word


class Score(object):
    # 七个情感大类对应的小类简称: 尊敬
    score_class = {'乐': ['PA', 'PE'],
                   '好': ['PD', 'PH', 'PG', 'PB', 'PK'],
                   '怒': ['NA'],
                   '哀': ['NB', 'NJ', 'NH', 'PF'],
                   '惧': ['NI', 'NC', 'NG'],
                   '恶': ['NE', 'ND', 'NN', 'NK', 'NL'],
                   '惊': ['PC']
                   }
    # 大连理工大学 -> ICTPOS 3.0
    POS_MAP = {
        'noun': 'n',
        'verb': 'v',
        'adj': 'a',
        'adv': 'd',
        'nw': 'al',  # 网络用语
        'idiom': 'al',
        'prep': 'p',
    }

    # 否定词 TODO 找否定语料库，从文件加载
    NOT_DICT = set(['不是', '不大', '没', '非', '莫', '弗', '毋', '没有','勿', '未', '否', '别', '無', '休',
    '缺乏', '缺少', '不', '甭', '勿', '别', '未', '反', '没', '否', '木有', '非', '无', '请勿', '无须', '并非', '毫无', '决不', '休想', '永不', '不要',
     '未尝', '未曾', '毋', '莫', '从未', '从未有过', '尚未', '一无', '并未', '尚无', '从没', '绝非', '远非', '切莫', '绝不', '毫不', '禁止', '忌', '拒绝',
     '杜绝', '弗'])


    def __init__(self, sentiment_dict_path, degree_dict_path, stop_dict_path):
        self.sentiment_struct, self.sentiment_dict = self.load_sentiment_dict(sentiment_dict_path)
        self.degree_dict = self.load_degree_dict(degree_dict_path)
        self.stop_words = self.load_stop_words(stop_dict_path)

    def load_stop_words(self, stop_dict_path):
        stop_words = [w.strip() for w in open(stop_dict_path, encoding='utf-8').readlines()]
        # print (stop_words[:100])
        return stop_words

    def remove_stopword(self, words):
        words = [w.strip() for w in words if w not in self.stop_words]
        return words

    def load_degree_dict(self, dict_path):
        """读取程度副词词典
        Args:
            dict_path: 程度副词词典路径. 格式为 word\tdegree
                       所有的词可以分为6个级别，分别对应极其, 很, 较, 稍, 欠, 超
       Returns:
            返回 dict = {word: degree}
        """
        degree_dict = {}
        with open(dict_path, 'r', encoding='UTF-8') as f:
            for line in f:
                line = line.strip()
                word, degree = line.split('\t')
                degree = float(degree)
                degree_dict[word] = degree
        return degree_dict

    def load_sentiment_dict(self, dict_path):
        """读取情感词词典
        Args:
            dict_path: 情感词词典路径. 格式请看 README.md
        Returns:
            返回 dict = {(word, postag): 极性}
        """
        sentiment_dict = {}
        sentiment_struct = []

        with open(dict_path, 'r', encoding='UTF-8') as f:
            # with gzip.open(dict_path) as f:
            for index, line in enumerate(f):
                if index == 0:  # title,即第一行的标题
                    continue
                items = line.split('\t')
                word = items[0]
                pos = items[1]
                sentiment = items[4]
                intensity = items[5]  # 1, 3, 5, 7, 9五档, 9表示强度最大, 1为强度最小.
                polar = items[6]  # 极性

                # 将词性转为 ICTPOS 词性体系
                pos = self.__class__.POS_MAP[pos]
                intensity = int(intensity)
                polar = int(polar)

                # 转换情感倾向的表现形式, 负数为消极, 0 为中性, 正数为积极
                # 数值绝对值大小表示极性的强度 // 分成3类，极性：褒(+1)、中(0)、贬(-1)； 强度为权重值
                value = None
                if polar == 0:  # neutral
                    value = 0
                elif polar == 1:  # positive
                    value = intensity
                elif polar == 2:  # negtive
                    value = -1 * intensity
                else:  # invalid
                    continue

                # key = (word, pos, sentiment )
                key = word
                sentiment_dict[key] = value

                # 找对应的大类
                for item in self.score_class.items():
                    key = item[0]
                    values = item[1]
                    # print(key)
                    # print(value)
                    for x in values:
                        if (sentiment == x):
                            class_value = key  # 如果values中包含，则获取key
                sentiment_struct.append(Struct(word, sentiment, pos, value, class_value))
        return sentiment_struct, sentiment_dict

    def findword(self, text):  # 查找文本中包含哪些情感词
        word_list = []
        for item in self.sentiment_struct:
            if item.word in text:
                word_list.append(item)
        return word_list

    def classify_words(self, words):
        # 这3个键是词的序号(索引)

        sen_word = {}
        not_word = {}
        degree_word = {}
        # 找到对应的sent, not, degree;      words 是分词后的列表
        for index, word in enumerate(words):
            if word in self.sentiment_dict and word not in self.__class__.NOT_DICT and word not in self.degree_dict:
                sen_word[index] = self.sentiment_dict[word]
            elif word in self.__class__.NOT_DICT and word not in self.degree_dict:
                not_word[index] = -1
            elif word in self.degree_dict:
                degree_word[index] = self.degree_dict[word]
        return sen_word, not_word, degree_word

    def get2score_position(self, words):
        sen_word, not_word, degree_word = self.classify_words(words)  # 是字典

        score = 0
        start = 0
        # 存所有情感词、否定词、程度副词的位置(索引、序号)的列表
        sen_locs = sen_word.keys()
        not_locs = not_word.keys()
        degree_locs = degree_word.keys()
        senloc = -1
        # 遍历句子中所有的单词words，i为单词的绝对位置
        for i in range(0, len(words)):
            if i in sen_locs:
                W = 1  # 情感词间权重重置
                not_locs_index = 0
                degree_locs_index = 0

                # senloc为情感词位置列表的序号,之前的sen_locs是情感词再分词后列表中的位置序号
                senloc += 1
                # score += W * float(sen_word[i])
                if (senloc == 0):  # 第一个情感词,前面是否有否定词，程度词
                    start = 0
                elif senloc < len(sen_locs):  # 和前面一个情感词之间，是否有否定词,程度词
                    # j为绝对位置
                    start = previous_sen_locs

                for j in range(start, i):  # 词间的相对位置
                    # 如果有否定词
                    if j in not_locs:
                        W *= -1
                        not_locs_index = j
                    # 如果有程度副词
                    elif j in degree_locs:
                        W *= degree_word[j]
                        degree_locs_index = j

                    # 判断否定词和程度词的位置：1）否定词在前，程度词减半(加上正值)；不是很   2）否定词在后，程度增强（不变），很不是
                if ((not_locs_index > 0) and (degree_locs_index > 0)):
                    if (not_locs_index < degree_locs_index):
                        degree_reduce = (float(degree_word[degree_locs_index] / 2))
                        W += degree_reduce
                        # print (W)
                score += W * float(sen_word[i])  # 直接添加该情感词分数
                # print(score)
                previous_sen_locs = i
        return score

    def getscore(self, text):#所有情感的得分
        word_list = self.findword(text)  ##查找文本中包含哪些情感词
        # 增加程度副词+否定词
        not_w = 1
        not_word = []
        for notword in self.__class__.NOT_DICT:  # 否定词
            if notword in text:
                not_w = not_w * -1
                not_word.append(notword)
        degree_word = []
        degree=0
        for degreeword in self.degree_dict.keys():
            if degreeword in text:
                degree = self.degree_dict[degreeword]
                # polar = polar + degree if polar > 0 else polar - degree
                degree_word.append(degreeword)
        # 7大类找对应感情大类的词语，分别统计分数= 词极性*词权重
        result = []
        for key in self.score_class.keys():  # 区分7大类
            score = 0
            score_words = []
            for word in word_list:

                if (key == word.class_value):
                    score = score + word.value
                    score_words.append(word.word)
            if score > 0:
                score = score + degree
            elif score < 0:
                score = score - degree  # 看分数>0，程度更强； 分数<0,程度减弱？
            score = score * not_w

            x = '{}_score={}; word={}; nor_word={}; degree_word={};'.format(key, score, score_words, not_word,
                                                                            degree_word)
            # x='{}'.format(score)
            # print(x)
            result.append(score)
            # key + '_score=%d; word=%s; nor_word=%s; degree_word=%s;'% (score, score_words,not_word, degree_word))
        return result

    #文件读取

def weiboread(filepath):
    '''
    :param filepath: json的路径
    :param start: 帖子开始的索引
    :param end: 帖子结束的索引
    :return: 列表，元素为一篇帖子下所有评论的字符串
    '''
    out=[]
    try:
        f = open(filepath, encoding='utf-8')
        comment_list = json.load(f,strict=False)

        end=len(comment_list)
        # print(end)
        for i in range(0, end):
            out.append(''.join(comment_list[i]['评论']))#单一帖子的所有评论合成一个字符串
    except Exception as e:
        print(e)
    # print(out)
    # 返回列表，每个元素是帖子下所有评论的拼接
    return out


#输入int数字，返回'2020-01-01'
def timeitr(smonth,sday,emonth,eday,year=2020): #遍历一定范围内的日期，返回日期字符串列表，闭区间
    begin = datetime.date(year, smonth, sday)
    end = datetime.date(year, emonth, eday)
    outDaylst=[]
    for i in range((end - begin).days + 1):
        outday = begin + datetime.timedelta(days=i)
        outDaylst.append(str(outday))
    return outDaylst

#返回列表[最强情感的字符串 第二强情感的字符串]
def find_1st2nd_max(intlist_moodScore):
    moods = ["乐", "好", "怒", "哀", "惧", "恶", "惊"]
    max1st_index=intlist_moodScore.index(max(intlist_moodScore))
    mood1st=moods[max1st_index]

    min_index=intlist_moodScore.index(min(intlist_moodScore))#将最大值换为最小值去找第二强情感
    intlist_moodScore[max1st_index]=intlist_moodScore[min_index]
    max2nd_index=intlist_moodScore.index(max(intlist_moodScore))
    mood2nd=moods[max2nd_index]

    return [mood1st,mood2nd]


def jstvRead(csv_path):
    csvFile = open(csv_path, "r",encoding='utf-8')
    reader = csv.reader(csvFile)
    out=[]
    for item in reader:
        out.append(item[3])
    #列表，每个元素是当日新闻正文
    return out


def weiboScore(smonth,sday,emonth,eday,year,stage):
    timeStage = timeitr(smonth, sday, emonth, eday, year)  # 日期参数
    for ymd in timeStage:
        weibo_path = r"../source/SplitedWeibo/stage{0:}/{1:}-/{2:}-blog-COV.json".format(stage,ymd,ymd)
        out_path = r"../out/weibo/{}weiboScore.csv".format(ymd)
        comment_list = weiboread(weibo_path)
        c = {
            "review": comment_list
        }
        weibodf = pd.DataFrame(c)
        # print(weibodf)

        # 文件写入
        outFile = open(out_path, 'a+', encoding='utf-8')

        # 写入表头
        moodlist = ["polar", "乐", "好", "怒", "哀", "惧", "恶", "惊", "最强情感", "次强情感"]
        for moodType_index in range(len(moodlist) - 1):
            outFile.write(moodlist[moodType_index] + ',')
        outFile.write(moodlist[-1] + '\n')

        # 写入极性和每种情感的得分，一条评论有太多否定词会出现负分
        for temp in weibodf['review']:
            score = Score(sentiment_dict_path, degree_dict_path, stop_dict_path)
            words = [x.strip() for x in jieba.cut(temp)]  # 分词
            words_noStopWords = score.remove_stopword(words)
            commentLen = len(words_noStopWords)
            # 分词->情感词间是否有否定词/程度词+前后顺序->分数累加

            # polar分
            result = score.get2score_position(words_noStopWords)  # polar
            polarScore = 0
            if (commentLen):  # 因爬虫原因，json的评论下可能没评论
                polarScore = float(result) / math.log(commentLen)
            outFile.write(str(polarScore) + ',')

            # 乐，好，怒，哀，惧，恶，惊
            emotionScore_list = score.getscore(words_noStopWords)  # 6种情感
            # 大连理工情感词典里表示好和恶的情感很多，消除情感字典情感词数量的影响
            weight = [1967, 10640, 388, 2314, 1179, 10282, 288]  # 每个情感词汇个数
            for i in range(len(emotionScore_list)):  # 除以对数评论字符串长度
                emotionScore_list[i] = emotionScore_list[i] / math.log((commentLen + 2) / math.log(weight[i]))

            emotionScore_list=changeScore(emotionScore_list)#分数修正

            for i in range(len(emotionScore_list)):
                outFile.write(str(emotionScore_list[i]) + ',')  # 写入情感分数

            moods1st2nd = find_1st2nd_max(emotionScore_list)
            outFile.write(moods1st2nd[0] + ',')
            outFile.write(moods1st2nd[1] + '\n')  # 写入最强，次强情感

        outFile.close()
        # woc 我靠 常见口头语表现为怒（微博评论区吵架会用到，表示惊叹也会用到），可能结果有些偏


def jstvSocre(smonth,sday,emonth,eday,year,stage):
    timeStage = timeitr(smonth, sday, emonth, eday, year)  # 日期参数
    for ymd in timeStage:
        try:
            jstv_csv_path = r"../source/jstv/stage{}/{}-/jstvRAW.csv".format(stage,ymd)#有些天会没有
            out_path = r"../out/jstv/{}jstvScore.csv".format(ymd)
            comment_list = jstvRead(jstv_csv_path)
            c = {
                "newsContent": comment_list
            }
            jstvdf = pd.DataFrame(c)
            # print(weibodf)

            # 文件写入
            outFile = open(out_path, 'a+', encoding='utf-8')

            # 写入表头
            moodlist = ["polar", "乐", "好", "怒", "哀", "惧", "恶", "惊", "最强情感", "次强情感"]
            for moodType_index in range(len(moodlist) - 1):
                outFile.write(moodlist[moodType_index] + ',')
            outFile.write(moodlist[-1] + '\n')

            # 写入极性和每种情感的得分，一条评论有太多否定词会出现负分
            for temp in jstvdf['newsContent']:
                score = Score(sentiment_dict_path, degree_dict_path, stop_dict_path)
                words = [x.strip() for x in jieba.cut(temp)]  # 分词
                words_noStopWords = score.remove_stopword(words)
                commentLen = len(words_noStopWords)
                # 分词->情感词间是否有否定词/程度词+前后顺序->分数累加

                # polar分
                result = score.get2score_position(words_noStopWords)  # polar
                polarScore = 0
                if (commentLen):  # 因爬虫原因，json的评论下可能没评论
                    polarScore = float(result) / math.log(commentLen)
                outFile.write(str(polarScore) + ',')

                # 乐，好，怒，哀，惧，恶，惊
                emotionScore_list = score.getscore(words_noStopWords)  # 6种情感
                # 大连理工情感词典里表示好和恶的情感很多，消除情感字典情感词数量的影响
                weight = [1967, 10640, 388, 2314, 1179, 10282, 288]  # 每个情感词汇个数
                for i in range(len(emotionScore_list)):  # 除以对数评论字符串长度
                    emotionScore_list[i] = emotionScore_list[i] / math.log((commentLen + 2) / math.log(weight[i]))

                #由于有负分，进行情感修正
                emotionScore_list=changeScore(emotionScore_list)

                for i in range(len(emotionScore_list)):
                    outFile.write(str(emotionScore_list[i]) + ',')  # 写入情感分数

                moods1st2nd = find_1st2nd_max(emotionScore_list)
                outFile.write(moods1st2nd[0] + ',')
                outFile.write(moods1st2nd[1] + '\n')  # 写入最强，次强情感
        except Exception as e:
            print(e)
        outFile.close()


def changeScore(scoreList):
    '''

    :param scoreList:
    :return:
    '''

    key = [ "乐", "好", "怒", "哀", "惧", "恶", "惊"]
    '''
    乐 反义 0.4哀 0.1恶 0.5惧
    好 反义 0.5惧 0.5恶
    怒 反义 乐
    哀 反义 0.4好 0.6乐
    惧 反义 好
    恶 反义 乐
    惊 反义 0.6乐 0.4好
    '''
    anti_dict = {
        #    乐  好  怒  哀  惧  恶  惊"
        '乐': [0, 0, 0, 0.4, 0.5, 0.1, 0],
        '好': [0, 0, 0, 0, 0.5, 0.5, 0],
        '怒': [1, 0, 0, 0, 0, 0, 0],
        '哀': [0.6, 0.4, 0, 0, 0, 0, 0],
        '惧': [0, 1, 0, 0, 0, 0, 0],
        '恶': [0, 1, 0, 0, 0, 0, 0],
        '惊': [0.6, 0.4, 0, 0, 0, 0, 0]

    }
    initial_mood_score_dict = dict(zip(key, scoreList))
    minusScore_dict = {}  # {'惧': -1.7929313807730507}
    for kv in initial_mood_score_dict.items():
        if (kv[1] < -0.000000001 ):
            minusScore_dict[kv[0]] = kv[1]

    adj_scoreList_dict = dict(zip(key, scoreList))

    for kv in minusScore_dict:
        adj_scoreList_dict[kv[0]] = 0.0
    # print(minusScore_dict,adj_scoreList_dict,end=' ')
    for kv in minusScore_dict.items():
        moodType = kv[0]
        score = kv[1]

        if (moodType == '乐'):
            adj_scoreList_dict['哀'] += -0.5 * score
            adj_scoreList_dict['恶'] += -0.1 * score
            adj_scoreList_dict['惧'] += -0.4 * score
        if (moodType == '好'):
            adj_scoreList_dict['惧'] += -0.5 * score
            adj_scoreList_dict['恶'] += -0.5 * score
        if (moodType == '怒'):
            adj_scoreList_dict['乐'] += -score
        if (moodType == '哀'):
            adj_scoreList_dict['好'] += -0.5 * score
            adj_scoreList_dict['乐'] += -0.5 * score
        if (moodType == '惧'):
            adj_scoreList_dict['好'] += -score
        if (moodType == '恶'):
            adj_scoreList_dict['好'] += -0.7 * score
            adj_scoreList_dict['乐'] += -0.3 * score
        if (moodType == '惊'):
            adj_scoreList_dict['乐'] += -0.4 * score
            adj_scoreList_dict['好'] += -0.6 * score
    # print(adj_scoreList_dict)
    adjScore_list=list(adj_scoreList_dict.values())#添加修正后的分数
    return adjScore_list

if __name__ == '__main__':
    sentiment_dict_path = r"../source/sentiment_words_chinese.tsv"
    degree_dict_path = r"../source/degree_dict.txt"
    stop_dict_path = r"../source/哈工大停用词表.txt"
    # weibo_path=r"../source/2019-12-08info.json"
    # out_path=r"../source/Score.csv"

    weiboScore(4,29,6,20,2020,5)

    # jstvSocre(6,21,12,21,2020,6)


