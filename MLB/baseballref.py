import numpy as np
import pandas as pd
from bs4 import BeautifulSoup, Comment
import requests
import re
import pymongo

federal_league_teams_1914 = {'CHI': 'Chi-Feds', 'BUF': 'Buffeds', 'BTT': 'Tip-Tops', 'KCP': 'Packers', 'PBS': 'Rebels', 'SLM': 'Terriers', 'NEW': 'Pepper', 'BAL': 'Terrapins', 'IND': 'Hoosiers'}
federal_league_teams_1915 = {'CHI': 'Whales', 'BUF': 'Blues', 'BTT': 'Tip-Tops', 'KCP': 'Packers', 'PBS': 'Rebels', 'SLM': 'Terriers', 'NEW': 'Pepper', 'BAL': 'Terrapins', 'IND': 'Hoosiers'}

def conn():
	return pymongo.MongoClient("mongodb+srv://admin:pdometer@mongo-uwij2.mongodb.net/test?retryWrites=true")

def get_page(url):
	r = requests.get(url)
	html = r.text.replace('<!--', '').replace('-->', '')
	return BeautifulSoup(html, "lxml")

def get_table_by_class(page, _class):
	return page.find_all('table',{'class':_class})

def get_table_by_id(page, table_id):
	return page.find_all('table', id=table_id)

def build_df(table, table_index, strings, ints):
	thead = table[table_index].find('thead')
	ths = thead.find_all('th')
	headings = []
	for th in ths:
		headings.append(th.text.replace('\u2265', 'gte').replace('\u003C', 'lt').strip())
	tbody = table[table_index].find('tbody')
	rows = tbody.find_all('tr')
	data = []
	for row in rows:
		if row.get('class') is not None:
			if 'partial_table' in row.get('class') or row.get('class') == ['thead']:
				continue
		cells = row.find_all(['th', 'td'])
		cells = [cell.text.replace('*', '').replace('#', '').replace('%', '').strip() for cell in cells]
		if cells[1] == 'LgAvg per 600 PA':
			continue
		data.append([cell for cell in cells])
	df = pd.DataFrame(data=data, columns=headings)
	for heading in headings:
		if heading in strings: #Strings
			continue
		elif heading in ints: #Ints
			df[heading] = df[heading].replace('', 0).astype(int)
		else:
			df[heading] = df[heading].replace('', 0).astype('float64')
	
	return df

def abbr_to_master(df, season):
	client = conn()
	db = client['SABR']
	table = db['teams']
	abbr_df = pd.DataFrame()
	abbr_df['Team'] = df['Tm']
	abbr_df['Lg'] = df['Lg']
	team_abbrs = []
	for index, row in abbr_df.iterrows():
		bref_abbr = row['Team'].title().strip().upper()[-3:]
		lg = row['Lg'].title().strip().upper()
		if bref_abbr == 'AVG':
			continue
		if lg == 'FL':
			if season == 1914:
				team_abbr = federal_league_teams_1914[bref_abbr]
			elif season == 1915:
				team_abbr = federal_league_teams_1915[bref_abbr]
		else:
			abbr = table.find( { 'abbrs.bref' : bref_abbr } )
			team_abbr = abbr[0]['master_abbr']
		team_abbrs.append(team_abbr)
	for i in range(len(team_abbrs)):
		df.loc[i, 'Master Team'] = team_abbrs[i]
	return df