import click
import pandas as pd

import requests
from prettytable import PrettyTable
from github import Github

@click.command()
def getAllRepos():   

    table = PrettyTable()
    table.field_names = ["Repository Name", "Private", "Public","Created Date","Language"]

    #github generated access token
    access_token =input("Enter Access Token: ")

    #login with access token
    login  = Github(access_token)

    #get the user
    user  = login.get_user()

    #get all repositories
    my_repos = user.get_repos()
    

    for repository in my_repos:
        name =  repository.name
        private,public = repository.private, not(repository.private)
        created_date = repository.created_at
        language = repository.language
        table.add_row([name, private, public, created_date, language])

    print(table)