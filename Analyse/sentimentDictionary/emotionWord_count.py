# coding: utf-8
import pandas as pd
import jieba
import time
import json


stopWord_path=r"../source/哈工大停用词表.txt"
# -------------------------------------情感词典读取-------------------------------
# 注意：
# 1.词典中怒的标记(NA)识别不出被当作空值,情感分类列中的NA都给替换成NAU
# 2.大连理工词典中有情感分类的辅助标注(有NA),故把情感分类列改好再替换原词典中

# 扩展前的词典
df = pd.read_excel(r"../source/大连理工大学中文情感词汇本体.xlsx")
# print(df.head(10)) #输出10行看下格式

df = df[['词语', '词性种类', '词义数', '词义序号', '情感分类', '强度', '极性']]
# df.head()

# -------------------------------------七种情绪的运用-------------------------------
Happy = []
Good = []
Surprise = []
Anger = []
Sad = []
Fear = []
Disgust = []

# df.iterrows()功能是迭代遍历每一行
for idx, row in df.iterrows():
    if row['情感分类'] in ['PA', 'PE']:
        Happy.append(row['词语'])
    if row['情感分类'] in ['PD', 'PH', 'PG', 'PB', 'PK']:
        Good.append(row['词语'])
    if row['情感分类'] in ['PC']:
        Surprise.append(row['词语'])
    if row['情感分类'] in ['NB', 'NJ', 'NH', 'PF']:
        Sad.append(row['词语'])
    if row['情感分类'] in ['NI', 'NC', 'NG']:
        Fear.append(row['词语'])
    if row['情感分类'] in ['NE', 'ND', 'NN', 'NK', 'NL']:
        Disgust.append(row['词语'])
    if row['情感分类'] in ['NAU']:  # 修改: 原NA算出来没结果
        Anger.append(row['词语'])

    # 正负计算不是很准 自己可以制定规则
Positive = Happy + Good + Surprise
Negative = Anger + Sad + Fear + Disgust
print('情绪词语列表整理完成')
# print(Anger)  #输出看下anger里有哪些词

# ---------------------------------------中文分词---------------------------------

# 添加自定义词典和停用词
# jieba.load_userdict("user_dict.txt")
def stopwordslist(filepath):
    stopwords = [line.strip() for line in open(filepath,'r',encoding='utf-8').readlines()]
    return stopwords

stop_list=stopwordslist(stopWord_path)


def txt_cut(sentence):
    return [w for w in jieba.lcut(sentence) if w not in stop_list]  # 可增加len(w)>1,lcut直接返回列表


# ---------------------------------------情感计算---------------------------------
def emotion_caculate(text):
    text = text.replace('\n', '')  # 停用词里加\n会转义成\\n,手动剔除一下

    positive = 0
    negative = 0

    anger = 0
    disgust = 0
    fear = 0
    sad = 0
    surprise = 0
    good = 0
    happy = 0

    anger_list = []
    disgust_list = []
    fear_list = []
    sad_list = []
    surprise_list = []
    good_list = []
    happy_list = []

    wordlist = txt_cut(text) # ['武汉', '好想你', '热干面', '致敬', '白衣天使', '致敬', '英雄', '加油', '加油', '加油', '一定', '好好', '勇敢', '站', '起来', '行']
    # wordlist = jieba.lcut(text)
    wordset = set(wordlist)
    wordfreq = []
    for word in wordset:
        freq = wordlist.count(word)
        if word in Positive:
            positive += freq
        if word in Negative:
            negative += freq
        if word in Anger:
            anger += freq
            anger_list.append(word)
        if word in Disgust:
            disgust += freq
            disgust_list.append(word)
        if word in Fear:
            fear += freq
            fear_list.append(word)
        if word in Sad:
            sad += freq
            sad_list.append(word)
        if word in Surprise:
            surprise += freq
            surprise_list.append(word)
        if word in Good:
            good += freq
            good_list.append(word)
        if word in Happy:
            happy += freq
            happy_list.append(word)

    emotion_info = {
        'length': len(wordlist),
        'positive': positive,
        'negative': negative,
        'anger': anger,
        'disgust': disgust,
        'fear': fear,
        'good': good,
        'sadness': sad,
        'surprise': surprise,
        'happy': happy,

    }

    indexs = ['length', 'positive', 'negative', 'anger', 'disgust', 'fear', 'sadness', 'surprise', 'good', 'happy']
    # return pd.Series(emotion_info, index=indexs), anger_list, disgust_list, fear_list, sad_list, surprise_list, good_list, happy_list
    #('length', 16) ('positive', 5) ('negative', 0) ('anger', 0) ('disgust', 0) ('fear', 0) ('sadness', 0) ('surprise', 0) ('good', 4) ('happy', 1)
    return pd.Series(emotion_info, index=indexs)


# 测试 (res, anger_list, disgust_list, fear_list, sad_list, surprise_list, good_list, happy_list)
text = """
晚安，人生最累的莫过于站在幸福里找幸福，生在福中不知福。懂得知足，才能常常感到心满意足
"""
# res, anger, disgust, fear, sad, surprise, good, happy = emotion_caculate(text)
res = emotion_caculate(text) #输出 length 16 positive 5 negtive 0 anger 0 disgust 0...... happy 1
print(res)



# -------------------------------------获取数据集---------------------------------
# weibo_path=r"../source/2019-12-08info.json"
#
# def weiboread(filepath,start,end):
#     '''
#     :param filepath: json的路径
#     :param start: 帖子开始的索引
#     :param end: 帖子结束的索引
#     :return: 列表，元素为一篇帖子下所有评论的字符串
#     '''
#     f = open(filepath, encoding='utf-8')
#     comment_list=json.load(f)
#     out=[]
#     for i in range(start,end):
#         out.append(''.join(comment_list['weibo'][i]['评论']))
#     #返回列表，每个元素是帖子下所有评论的拼接
#     return out
#
#
# comment_list=weiboread(weibo_path,0,3)
# #list转为dataframe
# c={
#     "review":comment_list
# }
# weibo_df=pd.DataFrame(c)
# emotion_df = weibo_df['review'].apply(emotion_caculate)
#
# #---------------------------------------情感计算---------------------------------
# output_df = pd.concat([weibo_df, emotion_df], axis=1)
#
# # 储存结果
# outPath=r"../source/weibo_qx.csv"
# output_df.to_csv(outPath, encoding='utf-8', index=False)


