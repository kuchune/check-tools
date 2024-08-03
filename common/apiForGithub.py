
import os
import requests
import time

# 环境变量中获取参数
REPO = os.environ.get("REPO", "reviews-team-test/test_jenkins")
PULL_NUMBER = os.environ.get("PULL_NUMBER", "6")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
reviewers = os.environ.get("reviewers", "ckux")
reviewer_teams = os.environ.get("reviewer_teams", "ckux-team")
comment_path = os.environ.get("comment_path", "./comment.txt")

def retry(tries=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(tries):
                try:
                    return func(*args, **kwargs)
                except:
                    print(f"第{i+1}次尝试失败...")
                    time.sleep(delay)
            print("重试失败...")
            return None
        return wrapper
    return decorator


def getRequest(url):
    response = requests.get(url)
    if response.status_code == 200:
      return response.json()
    else:
      print(response.status_code)
      print(f"获取{url}失败, 错误信息：", response.text)


def getHeaders(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Accept": "application/vnd.github+json" 
    }
    return headers


@retry(tries=3, delay=1)
def getReviewers():
    url = f'https://api.github.com/repos/{REPO}/pulls/{PULL_NUMBER}/requested_reviewers'
    reviewJson = getRequest(url)
    reviewerLst = [obj['login'] for obj in reviewJson['users']]
    reviewerTeamLst = [obj['name'] for obj in reviewJson['teams']]
    return reviewerLst, reviewerTeamLst


@retry(tries=3, delay=1)
def removeReviewers(reviewerLst, teamReviewerLst):
    url = f'https://api.github.com/repos/{REPO}/pulls/{PULL_NUMBER}/requested_reviewers'
    data = {
        "reviewers": reviewerLst,
        "team_reviewers": teamReviewerLst
    }
    response = requests.delete(url, json=data, headers=getHeaders(GITHUB_TOKEN))
    re = "成功"
    if response.status_code != 200:
        print(f"错误码: {response.status_code}")
        print(f"错误信息: {response.text}")
        # print(f"请求删除reviewers: {reviewerLst}和{teamReviewerLst}失败, 错误信息：{response.text}")
        response.raise_for_status()
        re = "失败"
    return re

@retry(tries=3, delay=1)
def addReviewers(reviewers):
    # data['team_reviewers'] =  team_reviewers.split(',')
    url = f'https://api.github.com/repos/{REPO}/pulls/{PULL_NUMBER}/requested_reviewers'
    data = {
      'reviewers': reviewers.split(',')
    }
    msg = f"添加reviewers: {reviewers}"
    response = requests.post(url, json=data, headers=getHeaders(GITHUB_TOKEN))
    if response.status_code != 201:
        msg += "失败"
        print(f"错误信息: {response.status_code},{response.text}")
        response.raise_for_status()
    else:
        msg += "成功"
    print(msg)
    
def checkExistReviewers(reviewers, team_reviewers):
    existReviewers = []
    existReviewerTeams = []
    reviewerLst, reviewerTeamLst = getReviewers()
    for reviewerName in reviewers.split(','):
        for userLogin in reviewerLst:
            if userLogin == reviewerName:
                existReviewers.append(reviewerName)
                
    for reviewerTeamName in team_reviewers.split(','):
        for teamName in reviewerTeamLst:
            if teamName == reviewerTeamName:
                existReviewerTeams.append(reviewerTeamName)
                    
    return existReviewers, existReviewerTeams

def checkReviewerActionStatus(checkType, reviewersMsg, memberLst, teamList):
    memberLst2, teamList2 = checkExistReviewers(reviewers, reviewer_teams)
    checkResult = "成功"
    if checkType == '添加':
        if reviewers not in memberLst2:
            checkResult = "失败"
    if checkType == '删除':
        for member in memberLst:       
            if member in memberLst2:
                checkResult = "失败"
        for teamMem in teamList:
            if teamMem not in teamList2:
                checkResult = "失败"
    print("检查"+checkType+reviewersMsg+checkResult)

def checkRiewer():
    memberLst, teamList = checkExistReviewers(reviewers, reviewer_teams)
    checkType = "添加"
    checkResult = "成功"
    reviewersMsg = ""
    if os.path.isfile(comment_path):
        reviewersMsg = reviewers
        if not memberLst:
            checkResult = addReviewers(reviewers)
    else:
        reviewersMsg = f"{reviewers}和{reviewer_teams}"
        checkType = '删除'
        if memberLst or teamList:
            checkResult = removeReviewers(memberLst, teamList)
    print(checkType+reviewersMsg+str(checkResult))
    
addReviewers(reviewers)

            