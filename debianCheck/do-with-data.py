import sys
import json
import os

# 在增加和修改内容中筛选敏感词
# checkType: 1, 在增加和修改内容筛选敏感词
def filter_keys_in_modify(content, keyLst):
    strJson = {}
    for fileName, patchContent in content.items():
        for lineContent in patchContent['b']:
            for keyStr in keyLst:
                if keyStr in lineContent:
                    if keyStr not in list(strJson.keys()):
                        strJson[keyStr] = {}
                    if fileName not in list(strJson[keyStr].keys()):
                        strJson[keyStr][fileName] = []
                    strJson[keyStr][fileName].append(lineContent)
    return strJson


# 在增加，删除和修改内容中筛选敏感词
# checkType: 2, 在修改,删除和增加内容筛选敏感词
def filter_keys_in_all(content, keyLst):
    strJson = {}
    for fileName, patchContent in content.items():
            for keyStr in keyLst:
                for actionType, actionTypePatchConten in patchContent.items():
                    for lineContent in actionTypePatchConten:
                        if keyStr in lineContent:
                            if keyStr not in list(strJson.keys()):
                                strJson[keyStr] = {}
                            if fileName not in list(strJson[keyStr].keys()):
                                strJson[keyStr][fileName] = {}
                            if actionType not in list(strJson[keyStr][fileName].keys()):
                                strJson[keyStr][fileName][actionType] = []
                            strJson[keyStr][fileName][actionType].append(lineContent)
    return strJson


def filter_keywords(content_dict, keyLst, checkType):
    originInfo = {}
    resultInfo = {}
    if content_dict:
        for fileTemp in content_dict:
            originInfo[fileTemp['filename']] = {
                "a": [],
                "b": []
            }
            filePatch = fileTemp['patch']
            fileContent = filePatch.splitlines()
            for line in fileContent:
                if line.startswith("-"):
                    originInfo[fileTemp['filename']]["a"].append(line.lstrip("-"))
                elif line.startswith("+"):
                    originInfo[fileTemp['filename']]["b"].append(line.lstrip("+"))

        if checkType == 'modify':
            resultInfo = filter_keys_in_modify(originInfo, keyLst)
        elif checkType == 'all':
            resultInfo = filter_keys_in_all(originInfo, keyLst)
        else:
            print("异常类型")
            exit(1)
    else:
        print("原始解析数据为空")
           
    if resultInfo:
      print(f"[FAIL]: 敏感词检查不通过{list(resultInfo.keys())}")
      writeJson(resultInfo, 'result.json')
      exit(1)
    else:
      print(f"[PASS]: 敏感词{checkKeys}检查通过")


# 读取json文件
def readJson(filepath):
    data = {}
    if os.path.isfile(filepath):
        with open(filepath, 'r') as file:
            data = json.load(file)
    return data


def writeJson(originInfo, logFile):
    with open(logFile, "w+") as fout:
        if isinstance(originInfo, dict):
            fout.write(json.dumps(originInfo, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    checkType = sys.argv[1]
    global checkKeys 
    checkKeys = sys.argv[2]
    jsonSource = sys.argv[3] # json文件路径
    
    key_list = checkKeys.split(',') #关键字以','号分隔
    content_dict = readJson(jsonSource)

    filter_keywords(content_dict, key_list, checkType)
