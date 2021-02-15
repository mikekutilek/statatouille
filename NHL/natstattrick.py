import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import pymongo #pymongo-3.7.2
import functools

def conn():
	return pymongo.MongoClient("mongodb+srv://admin:pdometer@mongo-uwij2.mongodb.net/test?retryWrites=true")

def get_gamelogs_page(season, situation):
	url = '''
	http://www.naturalstattrick.com/games.php?
	fromseason={}&
	thruseason={}&
	stype=2&
	sit={}&
	loc=B&
	team=All&
	rate=n
	'''.replace('\t', '').replace('\n', '').strip().format(season, season, situation)
	r = requests.get(url)
	html = r.text.replace('<!--', '').replace('-->', '')
	return BeautifulSoup(html, "lxml")

def get_table_by_id(page, table_id):
	return page.find_all('table', id=table_id)

def get_table_by_class(page, _class):
	return page.find_all('table',{'class':_class})

def build_df(table, strings, ints):
	thead = table[0].find('thead')
	ths = thead.find_all('th')
	headings = []
	for th in ths:
		headings.append(th.text.strip())
	headings.append('Result')
	headings.append('Date')
	tbody = table[0].find('tbody')
	rows = tbody.find_all('tr')
	data = []
	for row in rows:
		cells = row.find_all(['th', 'td'])
		new_cells = []
		for cell in cells:
			if cell.text.strip() == '-':
				new_cells.append('0')
			else:
				new_cells.append(cell.text.strip())
		row_data = [cell for cell in new_cells]
		game = cells[0].text.strip()
		team = cells[1].text.strip()#.split(" ")[1:]
		date = game.split(" - ")[0]
		full_score = game.split(" - ")[1]
		away_score = full_score.split(', ')[0]
		home_score = full_score.split(', ')[1]
		away_team = away_score.split(" ")[:-1]
		away_goals = away_score.split(" ")[-1]
		home_team = home_score.split(" ")[:-1]
		home_goals = home_score.split(" ")[-1]
		away_team_string = away_team[0]
		for w in away_team[1:]:
			away_team_string += " "
			away_team_string += w
		print(team)
		print(away_team)
		print(away_team_string)
		"""
		if winning_team_string in team:
			result = 'W'
		else:
			result = 'L'
		"""
		if away_team_string in team:
			if away_goals > home_goals:
				result = 'W'
			else:
				result = 'L'
		else:
			if home_goals > away_goals:
				result = 'W'
			else:
				result = 'L'
		"""
		gf = int(cells[13].text.strip())
		ga = int(cells[14].text.strip())
		if gf > ga:
			result = 'W'
		else:
			result = 'L'
		"""
		row_data.append(result)
		row_data.append(date)
		data.append(row_data)
	#print(data)
	df = pd.DataFrame(data=data, columns=headings)
	for heading in headings:
		if heading in strings: #Strings
			continue
		elif heading in ints: #Ints
			df[heading] = df[heading].replace('', 0).astype(int)
		else:
			df[heading] = df[heading].replace('', 0).astype('float64')
	return df

"""
page = get_page('http://www.naturalstattrick.com/games.php')
table = get_table_by_id(page, 'teams')
df = build_df(table)
#df['Date'] = df['Game'].str.split(" ", expand=True)[0]
print(df)
"""