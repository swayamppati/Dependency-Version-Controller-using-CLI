import click
import pandas as pd

import requests
from prettytable import PrettyTable

@click.command()
def getPubRepos():   

    table = PrettyTable()
    table.field_names = ["Repository Name", "Created Date"]

    # github_username  = "dyte-in"   #specify your User name

    github_username  = input("Enter your username: ")   #specify your User name

    #api url to grab public user repositories
    api_url = f"https://api.github.com/users/{github_username}/repos"

    #send get request
    response = requests.get(api_url)

    #get the json data
    data =  response.json()

    for repository in data:
        table.add_row([repository["name"], repository["created_at"]])

    print(table)