import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests

def get_all_skaters_page(season='2019'):
	url = "https://www.hockey-reference.com/leagues/NHL_{}_skaters.html".format(season)
	r = requests.get(url)
	return BeautifulSoup(r.content, "html.parser")

def get_advanced_skaters_page(season='2019'):
	url = "https://www.hockey-reference.com/leagues/NHL_{}_skaters-advanced.html".format(season)
	r = requests.get(url)
	return BeautifulSoup(r.content, "html.parser")

def get_all_goalies_page(season='2019'):
	url = "https://www.hockey-reference.com/leagues/NHL_{}_goalies.html".format(season)
	r = requests.get(url)
	return BeautifulSoup(r.content, "html.parser")

def get_gamelogs_page(season='2020'):
	url = "https://www.hockey-reference.com/leagues/NHL_{}_games.html".format(season)
	r = requests.get(url)
	html = r.text.replace('<!--', '').replace('-->', '')
	return BeautifulSoup(html, "lxml")

def get_table_by_id(page, table_id):
	return page.find_all('table', id=table_id)

def build_df(table):
	thead = table[0].find('thead')
	trs = thead.find_all('tr')[0]
	ths = trs.find_all('th')
	headings = []
	for th in ths:
		headings.append(th.text.strip('.'))
	if headings[2] == 'G':
		headings[2] = 'AWAY_G'
	if headings[4] == 'G':
		headings[4] = 'HOME_G'
	tbody = table[0].find('tbody')
	rows = tbody.find_all('tr')
	data = []
	for row in rows:
		if row.get('class') == ['partial_table'] or row.get('class') == ['thead']:
			continue
		cells = row.find_all(['th', 'td'])
		new_cells = []
		for cell in cells:
			if cell.text.strip() == 'St. Louis Blues':
				new_cells.append(cell.text.strip().replace('.', ''))
			else:
				new_cells.append(cell.text.replace('%', '').strip())
		data.append([cell for cell in new_cells])
	df = pd.DataFrame(data=data, columns=headings)
	return df

def get_table(page):
	table = page.find('table',{'class':'stats_table'})
	thead = table.find('thead')
	trs = thead.find_all('tr')[1]
	ths = trs.find_all('th')
	headings = []
	for th in ths:
		headings.append(th.text.strip(' . '))
	if headings[12] == 'EV':
		headings[12] = 'EVG'
	if headings[13] == 'PP':
		headings[13] = 'PPG'
	if headings[14] == 'SH':
		headings[14] = 'SHG'
	if headings[16] == 'EV':
		headings[16] = 'EVA'
	if headings[17] == 'PP':
		headings[17] = 'PPA'
	if headings[18] == 'SH':
		headings[18] = 'SHA'
	tbody = table.find('tbody')
	rows = tbody.find_all('tr')
	data = []
	for row in rows:
		if row.get('class') == ['partial_table'] or row.get('class') == ['thead']:
			continue
		cells = row.find_all(['th', 'td'])
		cells = [cell.text.replace('%', '').strip() for cell in cells]
		data.append([cell for cell in cells])

	df = pd.DataFrame(data=data, columns=headings).fillna(0)
	for heading in headings:
		if heading in ['Player', 'Tm', 'Pos']: #Strings
			continue
		elif heading in ['Rk', 'Age']: #Ints
			df[heading] = df[heading].replace('', 0).astype(int)
		elif heading in ['ATOI', 'TOI/60', 'TOI(EV)']:
			df[heading] = df[heading].replace('', '00:00')
			df[heading] = '00:' + df[heading]
			df[heading] = pd.to_timedelta(df[heading], unit='h')
		else:
			#print(heading)
			df[heading] = df[heading].replace('', 0).astype('float64')
	return df