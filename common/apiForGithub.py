
import os
import requests
import time

# 环境变量中获取参数
REPO = os.environ.get("REPO", "reviews-team-test/test_jenkins")
PULL_NUMBER = os.environ.get("PULL_NUMBER", "3")
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
    if response.status_code == 200:
        print(response.status_code)
        print(f"删除reviewers: {reviewerLst}]和{teamReviewerLst}失败, 错误信息：", response.text)


@retry(tries=3, delay=1)
def addReviewers(reviewers):
    # data['team_reviewers'] =  team_reviewers.split(',')
    url = f'https://api.github.com/repos/{REPO}/pulls/{PULL_NUMBER}/requested_reviewers'
    data = {
      'reviewers': reviewers.split(',')
    }
    response = requests.post(url, json=data, headers=getHeaders(GITHUB_TOKEN))
    if response.status_code != 201:
        print(response.status_code)
        print(f"添加reviewers: [{reviewers}]失败，错误信息:", response.text)


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
                existReviewerTeams.append()
                    
    return existReviewers, existReviewerTeams


memberLst, teamList = checkExistReviewers(reviewers, reviewer_teams)
if os.path.isfile(comment_path):
    if not memberLst and not teamList:
        addReviewers(reviewers)
else:
    if memberLst or teamList:
        removeReviewers(memberLst, teamList)