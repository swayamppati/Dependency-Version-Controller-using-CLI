import click
import pandas as pd
import json

import requests
from prettytable import PrettyTable
from github import Github

def printPackage(repo):

    #For My Repo
    contents = repo.get_contents("package.json")

    # #For Package.json
    # contents = repo.get_contents("package.json")

    dic = json.loads(contents.decoded_content.decode())
    # print(_dic)

    # #From Dyte Repo
    # dic = dic["dependencies"]
    # dic["axios"] = "^0.23.0"
    ##From Vibhu Repo
    # dic = dic["dependencies"]
    # dic["react"] = "20.8.6"

    table = PrettyTable()
    table.field_names = ["Dependency","Version"]
    for key,val in dic.items():
        table.add_row([key, val])
    print(table)
    print()

def fork(user, repo):
    #Forking a Repo
    myfork = user.create_fork(repo)
    print(myfork)

# def pull_request():


def push(repo, path, message, data, branch, update=False):
    # author = InputGitAuthor(
    #     "SwayamPrakashPati",
    #     "swayamppati@gmail.com"
    # )
    source = repo.get_branch("main")
    repo.create_git_ref(ref=f"refs/heads/{branch}", sha=source.commit.sha)  # Create new branch from main
    if update:  # If file already exists, update it
        contents = repo.get_contents(path, ref=branch)  # Retrieve old file to get its SHA and path
        repo.update_file(contents.path, message, json.dumps(data), contents.sha, branch=branch)  # Add, commit and push branch
    else:  # If file doesn't exist, create it
        repo.create_file(path, message, json.dumps(data), branch=branch)  # Add, commit and push branch


@click.command()
@click.option('--input','-i',help="File Name having Repo Links", required=True, prompt="Please Enter File Name:\n")
@click.option('-update', is_flag=True)
@click.argument('ver')
def getPrivateDep(input, update, ver):

    table = PrettyTable()
    table.field_names = ["Dependency","Version"]

    # df = pd.read_csv(input)
    # print('\n')
    # print("File Version = " + ver)
    # for i in df['repo']:
    #     print(i)
    # print('\n')


    #Take input the repo and name
    #Fork the repo to your github


    #github generated access token
    access_token ="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"

    #login with access token
    login  = Github(access_token)

    # login = Github("swayamppati","Mygithub@4137")

    #get the user
    user  = login.get_user()

    repo = user.get_repo("Angular-Learning") #Use the repo name to which you want to send pull request
    _repo = login.get_repo("dyte-in/javascript-sample-app")
    _repovibhu = login.get_repo("Vibhukumar10/Google-Keep-Clone")

    #Fork the Repo
    fork(user,_repovibhu)

    #Push Changes to Github
    _repoforked = login.get_repo("swayamppati/Google-Keep-Clone")
    file_path = "package.json"
    contents = _repoforked.get_contents(file_path)
    data = json.loads(contents.decoded_content.decode())
    data["dependencies"]["react"] = "21.8.6"
    push(_repoforked, file_path, "Update react version.", data, "update-dependencies", update=True)


    #Create a Pull Request for the Pushed Changes
    headers = {
    "Authorization" : "token {}".format(access_token),
    "Accept" : "application/vnd.github.sailor-v-preview+json"
    }
    data= {
        "title" : "PullRequest-Using-GithubAPI",
        "body" : "I have amazing new Features",
        "head" : "update-dependencies",
        "base" : "main"
    }
    url = "https://api.github.com/repos/swayamppati/Google-Keep-Clone/pulls"
    reply = requests.post(url,data=json.dumps(data), headers=headers)
    print(reply)

    # printPackage(repo)
    # printPackage(_repo)
    # printPackage(_repovibhu)

    # #Pushing to my Repo
    # data={
    #     "one":1,
    #     "two":2,
    #     "three":3,
    #     "four":4
    # }
    # if(update):
    #     repo.update_file(contents.path, "more tests", json.dumps(data), contents.sha, branch="main")