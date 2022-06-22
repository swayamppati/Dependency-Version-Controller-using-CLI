from random import random
import click
import pandas as pd
import random

import base64
import json

from prettytable import PrettyTable
from github import Github
import requests

def convertUrl(repolink):
    first_part = "https://api.github.com/repos/"
    mid = repolink.split("github.com/")[1]
    last_part = "contents/package.json"

    if(mid[-1]!='/'):
        last_part = "/"+last_part

    api_url = f"{first_part}{mid}{last_part}"
    return api_url


def compare(v, vfetch):
    versions1 = [int(v) for v in v.split(".")]
    versions2 = [int(v) for v in vfetch.split(".")]
    for i in range(max(len(versions1),len(versions2))):
        v1 = versions1[i] if i < len(versions1) else 0
        v2 = versions2[i] if i < len(versions2) else 0
        if v1 > v2:
            return False
        elif v1 <v2:
            return True
    return True

def fork(user, repo):
    #Forking a Repo
    myfork = user.create_fork(repo)
    print(f'\n{myfork}')

def push(repo, path, message, data, branch, update=False):
    source = repo.get_branch("main")

    # Create new branch from main
    repo.create_git_ref(ref=f"refs/heads/{branch}", sha=source.commit.sha)

    # If file already exists, update it
    if update:
        contents = repo.get_contents(path, ref=branch)  # Retrieve old file to get its SHA and path
        repo.update_file(contents.path, message, json.dumps(data), contents.sha, branch=branch)  # Add, commit and push branch

    # If file doesn't exist, create it
    else:  
        repo.create_file(path, message, json.dumps(data), branch=branch)  # Add, commit and push branch

def updateVer(access_token, login, user, repolink, uname, d, v):
    mid = repolink.split("github.com/")[1]
    if(mid[-1]=='/'):
        mid = mid[:-1]
    # print(mid)
    ownername = mid.split('/')[0]
    reponame = mid.split('/')[1]
    try:
        repo = login.get_repo(mid)
    except:
        return "Private Repo"

    #Fork the Repo
    fork(user, repo)

    # print(reponame)
    #Push Changes to Github
    repoforked = login.get_repo(f"{uname}/{reponame}")
    file_path = "package.json"
    contents = repoforked.get_contents(file_path)
    data = json.loads(contents.decoded_content.decode())
    data["dependencies"][d] = v
    n = random.randint(1,10000)
    push(repoforked, file_path, f"Update {d} version to {v}", data, f"update-dependencies{n}", update=True)

    #Create a Pull Request for the Pushed Changes
    headers = {
    "Authorization" : f"token {access_token}",
    "Accept" : "application/vnd.github.sailor-v-preview+json"
    }
    data= {
        "owner" : f"{ownername}",
        "title" : "Updating Dependency Version from CLI",
        "body" : f"Version update for {d} to {v}",
        "head" : f"{uname}:update-dependencies{n}",
        "base" : "main"
    }
    url = f"https://api.github.com/repos/{ownername}/{reponame}/pulls"
    reply = requests.post(url,data=json.dumps(data), headers=headers)
    return json.loads(reply.content)["html_url"]

def Dep(name,repolink):
    #*** api url to grab public user repositories ***
    api_url = convertUrl(repolink)
    try:
        response = requests.get(api_url)
        data =  response.json()
        file_content = data['content']
        file_content_encoding = data.get('encoding')
        if file_content_encoding == 'base64':
            file_content = base64.b64decode(file_content).decode()

        return json.loads(file_content)["dependencies"]

    except:
        print(f"\n{name} is a Private Repository, Authectication Required!!!")
        access_token = input("Enter Access Token for the Repository: ")
        #login with access token
        try:
            login  = Github(access_token)
            #get the user
            user  = login.get_user()
            repo = user.get_repo(name)
            contents = repo.get_contents("package.json")

            return json.loads(contents.decoded_content.decode())["dependencies"]
        # for key,val in dic.items():
        #     print(f"{key}\t{val}")
        except:
            return -1

@click.command()
@click.option('--inputfile','-i',help="File Name having Repo Links", required=True, prompt="Please Enter File Name:\n")
@click.option('-update', is_flag=True)
@click.argument('ver')
def getDep(inputfile, update, ver):
    print()
    table = PrettyTable()
    access_token :any
    uname :any
    login :any
    user :any
    if(update):
        table.field_names = ["name", "repo", "version", "version_satisfied", "update_pr"]
        table.align["update_pr"] = "l"
        print(f"To create PRs you need to be Logged In to your Account!!!")
        # access_token ="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"
        access_token = input("Enter your Access Token: ")
        uname = input("Enter username: ")
        login  = Github(access_token)
        user  = login.get_user()
    else:
        table.field_names = ["name", "repo", "version", "version_satisfied"]
    
    table.align["name"] = "l"
    table.align["repo"] = "l"
    table.align["version"] = "l"
    table.align["version_satisfied"] = "l"

    df = pd.read_csv(inputfile)
    for name,repolink in zip(df['name'],df['repo']):
        #*** Fetching Dependency from package.json***
        dep = Dep(name,repolink)

        #If Private Repo not authenticated succesfully
        if(dep==-1):
            print("Authentication Unsuccessful!!!")
            table.add_row([name,"Authentication Unsuccessful!!!","xxxxx","xxxxx"])
            continue

        #Extracting the Dependency and its version needed
        d = ver.split('@')[0]
        v = ver.split('@')[1]
        vfetch = dep[d].split('^')[1]
        
        #Checking Compatibility
        compatible = compare(v,vfetch)

        #If update flag has been called
        if(update):
            if(compatible):
                table.add_row([name,repolink,vfetch,compatible,""])
            else:
                pr_url = updateVer(access_token, login, user, repolink, uname, d, v)
                table.add_row([name,repolink,vfetch,compatible,pr_url])
        else:
            table.add_row([name,repolink,vfetch,compatible])

    #Printing the final Table
    print()
    print(table.get_string(title="Version Compatibility"))
    print()