import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import pymongo

def conn():
	return pymongo.MongoClient("mongodb+srv://admin:pdometer@mongo-uwij2.mongodb.net/test?retryWrites=true")

def get_team_stats_page(cat, season):
	if cat == 'batting':
		stats_list = 'TEAM%2CLG%2CYEAR%2CG%2CPA%2CAB%2CR%2CH%2CHR%2CTB%2CBB%2CIBB%2CSO%2CBBR%2CSOR%2CHBP%2CSF%2CSH%2CRBI%2CSB%2CCS%2CSB_PERCENT%2CAVG%2COBP%2CSLG%2COPS%2CISO%2CDRC_RAA%2CDRC_PLUS%2CDRC_WARP'
	else:
		stats_list = 'YEAR%2CTEAM%2CLVL%2CIP%2CPA%2CHR%2CERA%2CFIP%2CTRAA_PERCENT%2CEPAA_PERCENT%2CCFIP%2CDRA%2CDRA_MINUS%2CDRA_RELIEF%2CDRA_START%2CDRA_PWARP'
	url = '''https://legacy.baseballprospectus.com/sortable/index.php?
	mystatslist={}&
	category=team_{}&
	tablename=dyna_team_{}&
	stage=data&
	year={}&
	group_TEAM=*&
	group_LVL=MLB&
	group_LG=*&
	minimum=0&
	sort1column=DRC_WARP&
	sort1order=DESC&
	sort2column=TEAM&
	sort2order=ASC&
	sort3column=TEAM&
	sort3order=ASC&
	page_limit=All&
	glossary_terms=*'''.replace('\t', '').replace('\n', '').strip().format(stats_list, cat, cat, season)
	r = requests.get(url)
	html = r.text.replace('<!--', '').replace('-->', '')
	return BeautifulSoup(html, "lxml")

def get_table_by_id(page, table_id):
	return page.find('table', id=table_id)

def build_df(table, strings, ints):
	rows = table.find_all('tr')
	headings = []
	thead = rows[0]
	ths = thead.find_all('td')
	for th in ths:
		headings.append(th.text.strip())
	data = []
	for row in rows[1:]:
		cells = row.find_all(['th', 'td'])
		cells = [cell.text.replace(',', '').replace('%', '').strip() for cell in cells]
		data.append([cell for cell in cells])
	df = pd.DataFrame(data=data, columns=headings)
	for heading in headings:
		if heading in strings: #Strings
			continue
		elif heading in ints: #Ints
			#print(type(df[heading][0]))
			df[heading] = [df[heading][i].replace('.', '') for i in range(len(df[heading]))]
			df[heading] = df[heading].astype(int)
		else:
			df[heading] = df[heading].replace('', 0).astype('float64')
	return df

def abbr_to_master(df):
	client = conn()
	db = client['SABR']
	table = db['teams']
	abbr_df = pd.DataFrame()
	abbr_df['Team'] = df['TEAM']
	#print(abbr_df)
	team_abbrs = []
	for index, row in abbr_df.iterrows():
		bp_abbr = row['Team'].title().strip().upper()
		#print(bp_abbr)
		if bp_abbr == 'AVG':
			continue
		abbr = table.find( { 'abbrs.bp' : bp_abbr } )
		#for doc in abbr:
		#	print(doc)
		team_abbr = abbr[0]['master_abbr']
		#print(team_abbr)
		team_abbrs.append(team_abbr)
	for i in range(len(team_abbrs)):
		df.loc[i, 'Master Team'] = team_abbrs[i]
	return df