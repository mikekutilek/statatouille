import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests

def get_team_stats_page(season='2020'):
	url = "https://www.basketball-reference.com/leagues/NBA_{}.html".format(season)
	r = requests.get(url)
	html = r.text.replace('<!--', '').replace('-->', '')
	return BeautifulSoup(html, "lxml")

def get_table_by_id(page, table_id):
	return page.find_all('table', id=table_id)

def build_df(table, table_index, strings, ints):
	thead = table[table_index].find('thead')
	trs = thead.find_all('tr')[1]
	ths = trs.find_all('th')
	headings = []
	for th in ths:
		headings.append(th.text.strip(' . ').replace('.', ''))
	if headings[21] == 'eFG%':
		headings[21] = 'def_eFG%'
	if headings[22] == 'TOV%':
		headings[22] = 'def_TOV%'
	if headings[24] == 'FT/FGA':
		headings[24] = 'def_FT/FGA'
	tbody = table[table_index].find('tbody')
	rows = tbody.find_all('tr')
	data = []
	for row in rows:
		if row.get('class') == ['partial_table'] or row.get('class') == ['thead']:
			continue
		cells = row.find_all(['th', 'td'])
		cells = [cell.text.replace('%', '').replace(',', '').strip() for cell in cells]
		data.append([cell for cell in cells])

	df = pd.DataFrame(data=data, columns=headings).fillna(0)
	for heading in headings:
		if heading in strings: #Strings
			continue
		elif heading in ints: #Ints
			df[heading] = df[heading].replace('', 0).astype(int)
		else:
			df[heading] = df[heading].replace('', 0).astype('float64')
	return df

"""
page = get_team_stats_page()
table = get_table_by_id(page, 'misc_stats')
df = build_df(table, 0, ['Team', 'Arena'], ['Rk', 'W', 'L', 'PW', 'PL'])
print(df)
"""