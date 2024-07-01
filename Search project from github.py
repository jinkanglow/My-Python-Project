import requests
import json

def search_github(query, token):
    # GitHub API URL for searching code globally
    url = f'https://api.github.com/search/code?q={query}'

    # Headers including authorization token
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    #interacting with APIs and web services
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        results = response.json()
        for item in results.get('items', []):
            print(f"Repository: {item['repository']['full_name']}")
            print(f"URL: {item['html_url']}\n")
    else:
        print(f"Failed to fetch data: {response.status_code}")
        print(response.text)

# Usage
query = 'scheduling application project'  # Term you are searching for
token = 'replace with your GitHub Token'  # Replace with your GitHub token

search_github(query, token)
