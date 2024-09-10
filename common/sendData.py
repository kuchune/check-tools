import requests
import json
import os
import time

PROJECT = os.environ.get("PROJECT", "reviews-team-test/test_jenkins")
# BRANCH = os.environ.get("BRANCH", "main") #PULL_BASE_REF
NUMBER = os.environ.get("NUMBER", "6") #PULL_NUMBER
CHANGEURL = f"https://github.com/{PROJECT}/pull/{NUMBER}"
# AUTHOR = os.environ.get("AUTHOR", "kuchune") #github.actor
REVISION = os.environ.get("REVISION", "c8daa46ae1c65d28bfcea09301cecca3092aa8cd") #github.sha
RUNID = os.environ.get("RUNID", "10629754757") #github.run_id
JOBSTATUS = os.environ.get("JOBSTATUS", "success") #job.status
TESTTYPE = os.environ.get("TESTTYPE", "staticCheck")
STATUS = os.environ.get("STATUS", "否")
RESULT = os.environ.get("RESULT", "1")
# ARCHIVEID = os.environ.get("ARCHIVEID", "1881147956")

# def writeJsonFile(resultInfo, jsonFile):
#     with open(jsonFile, 'w+') as fp:
#       fp.write(json.dumps(resultInfo, indent=4, ensure_ascii=False))

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

def send_webhook_request(push_info):
    headers = {
        "Content-Type": "application/json"
    }
    
    url = "https://cooperation.uniontech.com/api/workflow/hooks/NjZjZWU4ZTkwYjEwOTIwMDc0MmU3ZDIz"
    print(json.dumps(push_info))
    try:
        response = requests.post(url, data=json.dumps(push_info), headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending webhook request: {e}")
        return None
    
@retry(tries=3, delay=1)
def get_pr_info():
    url = f"https://api.github.com/repos/{PROJECT}/pulls/{NUMBER}"
    response = requests.get(url).json()
    global pr_type
    global pr_base_branch
    global commit_author
    pr_type = response['state'].title()
    pr_base_branch = response['base']['ref']
    commit_author = response['user']['login']


get_pr_info()
commitInfo = {
    "platform": "Github",
    "type": pr_type,
    "branch": pr_base_branch,
    "project": PROJECT,
    "authorEmail": "test@test.com",
    "changeUrl": CHANGEURL,
    "author": commit_author,
    "number": NUMBER,
    "revision": REVISION
}
testResults = {
    "status": STATUS,
    "result": RESULT,
    # "log": "https://github.com/"+PROJECT+"/actions/runs/"+RUNID+"/artifacts/"+ARCHIVEID"
    "log": "https://github.com/"+PROJECT+"/actions/runs/"+RUNID
}
push_info = {
    "commitInfo": json.dumps(commitInfo),
    "jobUrl": "https://github.com/"+PROJECT+"/actions/runs/"+RUNID,
    "jobStatus": JOBSTATUS,
    "testType": TESTTYPE,
    "testVersion": "2500",
    "testResults": json.dumps(testResults)
}
send_webhook_request(push_info)