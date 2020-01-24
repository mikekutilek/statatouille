import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import json
#import urllib2

team_index = {"DET": "Pistons", "CHA": "Hornets", "SAS": "Spurs", "ORL": "Magic", "PHI": "76ers", "OKC": "Thunder", "IND": "Pacers", "HOU": "Rockets", "UTA": "Jazz", "MEM": "Grizzlies", "WAS": "Wizards", "MIN": "Timberwolves", "BOS": "Celtics", "GSW": "Warriors", "SAC": "Kings", "LAL": "Lakers", "BKN": "Nets", "CHI": "Bulls", "MIL": "Bucks", "IND": "Pacers", "NYK": "Knicks", "NOP": "Pelicans", "MIA": "Heat", "TOR": "Raptors", "DAL": "Mavericks", "POR": "Trail Blazers", "ATL": "Hawks", "LAC": "Clippers", "CLE": "Cavaliers", "DEN": "Nuggets", "PHO": "Suns"}


def get_page():
	url = '''https://projects.fivethirtyeight.com/2020-nba-predictions/games/'''
	r = requests.get(url)
	return BeautifulSoup(r.content, "html.parser")

def get_game_data(page, table):
	
	thead = table.find('thead')

	tbody = table.find('tbody')
	rows = tbody.find_all('tr')
	data = []
	for row in rows:
		cells = row.find_all(['th', 'td'])
		cells = [cell.text.replace('%', '').strip() for cell in cells]
		data.append(cell for cell in cells)
	df = pd.DataFrame(data=data)
	return df[1:3].loc[:, 2:4].rename(columns={2: "Team", 3: "Spread", 4: "538 Win%"})

def get_538_today():
	page = get_page()
	today = page.find_all('section', {'class':'day'})
	tables = today[0].find_all('table', {'class':'pre'})
	gamelines = []
	for table in tables:
		data = get_game_data(page, table)
		away_team = data.loc[1]['Team']
		home_team = data.loc[2]['Team']
		away_spread = data.loc[1]['Spread']
		home_spread = data.loc[2]['Spread']
		away_win = data.loc[1]['538 Win%']
		home_win = data.loc[2]['538 Win%']
		if away_spread == '':
			away_spread = home_spread[1:]
		if home_spread == '':
			home_spread = away_spread[1:]
		if away_spread == 'PK' or home_spread == 'PK':
			away_spread = '0'
			home_spread = '0'
		gamelines.append({'AWAY TEAM': away_team, 'AWAY SPREAD': float(away_spread), 'AWAY WIN%': float(away_win), 'HOME TEAM': home_team, 'HOME SPREAD': float(home_spread), 'HOME WIN%': float(home_win)})
	df = pd.DataFrame(gamelines)
	return df

#print(get_538_today())