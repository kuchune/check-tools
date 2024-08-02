
import os
import requests

# 环境变量中获取参数
REPO = os.environ.get("REPO_NAME", "reviews-team-test/test_jenkins")
PULL_NUMBER = os.environ.get("PULL_NUMBER", "3")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
reviewers = os.environ.get("reviewers")
reviewer_teams = os.environ.get("reviewer_teams")

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

def listReviewers():
    url = f'https://api.github.com/repos/{REPO}/pulls/{PULL_NUMBER}/requested_reviewers'
    reviewJson = getRequest(url)
    reviewerLst = [obj['login'] for obj in reviewJson['users']]
    reviewerTeamLst = [obj['name'] for obj in reviewJson['teams']]
    return reviewerLst, reviewerTeamLst

def removeReviewers(reviewerLst, teamReviewerLst):
    re = 'FAIL'
    url = f'https://api.github.com/repos/{REPO}/pulls/{PULL_NUMBER}/requested_reviewers'
    data = {
        "reviewers": reviewerLst,
        "team_reviewers": teamReviewerLst
    }
    response = requests.delete(url, json=data, headers=getHeaders(GITHUB_TOKEN))
    if response.status_code == 200:
      re = 'PASS'
    else:
      print(response.status_code)
      print(f"获取{url}失败, 错误信息：", response.text)
    return re

def checkExistReviewers(reviewers, team_reviewers):
    existReviewers = []
    existReviewerTeams = []
    reviewerLst, reviewerTeamLst = listReviewers()
    for reviewerName in reviewers.split(','):
        for userLogin in reviewerLst:
            if userLogin == reviewerName:
                existReviewers.append(reviewerName)
                
    for reviewerTeamName in team_reviewers.split(','):
        for teamName in reviewerTeamLst:
            if teamName == reviewerTeamName:
                existReviewerTeams.append()
                    
    return existReviewers, existReviewerTeams

def checkAndRemoveReviewers(reviewers, team_reviewers):
    memberLst, teamList = checkExistReviewers(reviewers, team_reviewers)
    re = removeReviewers(memberLst, teamList)
    print(f"删除reviewers:{reviewers}和{team_reviewers}:", re)
    return re

checkAndRemoveReviewers(reviewers, reviewer_teams)
