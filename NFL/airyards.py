import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests

CUR_SEASON = "2019"

def get_ay_data():
	url = "http://airyards.com/{}/weeks".format(CUR_SEASON)
	r = requests.get(url)
	df = pd.DataFrame(r.json())
	return df

def get_pfr_rushing():
	url = "https://www.pro-football-reference.com/years/{}/rushing.htm".format(CUR_SEASON)
	r = requests.get(url)
	return BeautifulSoup(r.content, "html.parser")

def get_pfr_fantasy():
	url = "https://www.pro-football-reference.com/years/{}/fantasy.htm".format(CUR_SEASON)
	r = requests.get(url)
	return BeautifulSoup(r.content, "html.parser")

def get_pfr_scoring():
	url = "https://www.pro-football-reference.com/years/{}/scoring.htm".format(CUR_SEASON)
	r = requests.get(url)
	return BeautifulSoup(r.content, "html.parser")

def get_table(page):
	table = page.find('table',{'class':'stats_table'})
	thead = table.find('thead')
	trs = thead.find_all('tr')
	if len(trs) > 1:
		tr = trs[1]
	else:
		tr = trs[0]
	ths = tr.find_all('th')
	headings = []
	for th in ths:
		headings.append(th.text.strip())
	if headings[1] == '':
		headings[1] = 'Player'
	if headings[8] == 'Att':
		headings[8] = 'PassAtt'
	if headings[9] == 'Yds':
		headings[9] = 'PassYds'
	if headings[10] == 'TD':
		headings[10] = 'PassTD'
	if headings[12] == 'Att':
		headings[12] = 'RushAtt'
	if headings[13] == 'Yds':
		headings[13] = 'RushYds'
	if len(headings) > 14:
		if headings[15] == 'TD':
			headings[15] = 'RushTD'
		if headings[18] == 'Yds':
			headings[18] = 'RecYds'
		if headings[20] == 'TD':
			headings[20] = 'RecTD'
	tbody = table.find('tbody')
	rows = tbody.find_all('tr')
	data = []
	for row in rows:
		if row.get('class') == ['partial_table'] or row.get('class') == ['thead']:
			continue
		cells = row.find_all(['th', 'td'])
		cells = [cell.text.replace('%', '').strip() for cell in cells]
		data.append([cell for cell in cells])

	df = pd.DataFrame(data=data, columns=headings)
	return df

def main():
	page = get_pfr_rushing()
	print(get_table(page))

if __name__ == '__main__':
	main()