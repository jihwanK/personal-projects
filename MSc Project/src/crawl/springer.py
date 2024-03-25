# import pandas as pd
# import bs4 as BeautifulSoup
import requests

url = "http://api.springernature.com/meta/v2/json"
headers = {
    'Accept': 'application/json',
}
params = {
    # 'q': 'keyword:Machine Learning',  # search query
    'p': 10,  # number of results to return
    'api_key': '793eb0a9919da0a054f623d6fec08c4a',
    'year': 2021,
}

response = requests.get(url, headers=headers, params=params)

data = response.json()  # convert response to JSON format

print(data)
# print(data['records'].keys())

# for record in data['records']:
#     print(record['title'])