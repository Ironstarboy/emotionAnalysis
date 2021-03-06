import splitWeibo
import json

if __name__ == "__main__":
    filePath = '2019-12-09info.json'
    fp = open(filePath, 'r', encoding='utf-8')
    res = ''
    a = fp.readlines()
    for line in a:
        res += line
    jsonA = json.loads(res)
    print(jsonA)
    print(jsonA[0])