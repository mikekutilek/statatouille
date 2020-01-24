import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests

url = "https://therundown-therundown-v1.p.rapidapi.com/sports/3/events/2019-06-10"

querystring = {"include":["all_periods","scores"],"offset":"0"}

headers = {
    'x-rapidapi-host': "therundown-therundown-v1.p.rapidapi.com",
    'x-rapidapi-key': "8e09acd151mshfb5dfdcb548476bp1acdebjsnf26f34825a8f"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)