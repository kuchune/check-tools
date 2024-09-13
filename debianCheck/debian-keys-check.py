
import json
import os

# check_type = os.environ.get("check_type", "all")
# check_keys = os.environ.get("check_keys", "export,unset")
repo_name = os.environ.get("repo_name", "reviews-team-test/dde-file-manager")
pull_number = os.environ.get("pull_number", "1")
api_token = os.environ.get("api_token")

# key_list = check_keys.split(',') #关键字以','号分隔
keyJson = {
  "modify": "getcap,setcap,lshw,dmidecode",
  "all": "export,unset"
}
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

# 写comment文件
def writeCommentFile(commentMsg):
  try:
    print(commentMsg)
    with open('comment.txt', "a+") as fout:
      fout.write(commentMsg+'\n')
  except Exception as e:
    print(f"[ERR]: writeCommentFile异常报错-{e}")
    
def filter_keywords(content_dict, keyJson):
    NoNeedSuffix = [".js", ".vue", ".ts", ".less", ".html", ".go", ".css", ".json", ".txt", ".doc", ".jpg", ".png", ".svg", ".py", '.yml', '.md', '.sha1', '.log']
    originInfo = {}
    resultInfo = {}
    isPass = True
    if content_dict:
        for fileTemp in content_dict:
            noNeed = False
            filename = fileTemp['filename']
            for endString in NoNeedSuffix:
                if filename.endswith(endString):
                    noNeed = True
                    break
            if noNeed:
                continue
            originInfo[fileTemp['filename']] = {
                "a": [],
                "b": []
            }
            if 'patch' in fileTemp.keys():
                filePatch = fileTemp['patch']
                fileContent = filePatch.splitlines()
                for line in fileContent:
                    if line.startswith("-"):
                        originInfo[fileTemp['filename']]["a"].append(line.lstrip("-"))
                    elif line.startswith("+"):
                        originInfo[fileTemp['filename']]["b"].append(line.lstrip("+"))
        
        reportDir = 'artifact'
        if os.path.exists(reportDir):
            os.rmdir(reportDir)
        os.makedirs(reportDir)
        for checkType in keyJson:
            keyLst = keyJson[checkType].split(',') #关键字以','号分隔
            # resultInfo = filter_keywords(pfInfo, key_list, check_type)
            if checkType == 'modify':
                resultInfo = filter_keys_in_modify(originInfo, keyLst)
            elif checkType == 'all':
                resultInfo = filter_keys_in_all(originInfo, keyLst)
            else:
                print("异常类型")
                # exit(1)
            if resultInfo:
                isPass = False
                resultInfoKeys = ', '.join(list(resultInfo.keys()))
                resultInfoMsg = json.dumps(resultInfo, indent=4)
                logMsg = f'''
- 检测到敏感词{resultInfoKeys}变动;
<details>
<summary>详情</summary>

```ruby
    {resultInfoMsg}
```
</details>
'''
                writeCommentFile(logMsg)
                writeJson(resultInfo, f'{reportDir}/result-{checkType}.json')
    else:
        print("原始解析数据为空")
    
    # if resultInfo:
    #     isPass = False
    # #   print(f"[FAIL]: 敏感词检查不通过{list(resultInfo.keys())}")
    #     writeJson(resultInfo, 'result.json')
    #   exit(1)
    # else:
    #   print(f"[PASS]: 敏感词{checkKeys}检查通过")
    return isPass


# 读取json文件
def readJson(filepath):
    data = {}
    if os.path.isfile(filepath):
        with open(filepath, 'r') as file:
            data = json.load(file)
    return data

# 写Json文件
def writeJson(originInfo, logFile):
    with open(logFile, "w+") as fout:
        if isinstance(originInfo, dict):
            fout.write(json.dumps(originInfo, indent=4, ensure_ascii=False))

# 获取pr中变更文件信息
def get_pulls_files():
    import requests
    url = f'https://api.github.com/repos/{repo_name}/pulls/{pull_number}/files'
    # print(f'apiurl is {url}')
    headers = {
        "Authorization": f"Bearer {api_token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
      return response.json()
    else:
      print(response.status_code)
      print(f"获取{url}失败, 错误信息：", response.text)

print(str(filter_keywords(get_pulls_files(), keyJson)))