"""
日期类
"""


import re

hanziS = u"[\u4e00-\u9fa5]+"
hanzi = re.compile(hanziS)


# 把 YYYY年MM月DD日变成YYYY-MM-DD-格式方便后续处理
def getDate(rdate):
    date = re.sub(pattern=hanzi, repl="-", string=rdate, count=3)
    return date


# 由数字生成对应日期
def generateDate(year, month, day):
    return str(fillAZero(year) + '-' + fillAZero(month) + '-' + fillAZero(day) + '-')


# 生成下一个日期地址
# 有一说一，这个是真的烦
def getNextDate(date):
    numbers = str(date).split('-')
    year = int(numbers[0])
    month = int(numbers[1])
    day = int(numbers[2])
    day += 1
    bigMonth = [1, 3, 5, 7, 8, 10, 12]
    smallMonth = [4, 6, 9, 11]
    if month in bigMonth:
        if day == 32:
            month += 1
            day = 1
    elif month in smallMonth:
        if (day == 31):
            month += 1
            day = 1
    elif month == 2:
        if year % 4 == 0 and year % 100 != 0:  # 闰年
            if day == 30:
                month += 1
                day = 1
        else:  # 其他年份
            if day == 29:
                month += 1
                day = 1
    else:
        print("ERROR!")
    if month == 13:
        year += 1
        month = 1
    return generateDate(year, month, day)


# 补‘0’
def fillAZero(num):
    if num < 10:
        return '0' + str(num)
    else:
        return str(num)


# 比较两个日期的大小，如果第一个的日期在第二个之后，则返回1；相等则返回0；否则返回-1
def dateCmp(date1, date2):
    numbers1 = int(str(date1).replace('-', ''))
    numbers2 = int(str(date2).replace('-', ''))
    if numbers1 > numbers2:
        return 1
    elif numbers1 == numbers2:
        return 0
    else:
        return -1
