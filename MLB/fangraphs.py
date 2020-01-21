import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import sys
import datetime as dt
import argparse
import pymongo #pymongo-3.7.2

gamelog_categories = {'dashboard': 0, 'standard': 1, 'advanced': 2, 'batted-ball': 3, 'more-batted-ball': 4, 'win-probability': 5, 'pitch-type': 6, 'pitch-value': 7, 'plate-discipline': 8}
split_categories = {'handedness': 0, 'home-away': 1, 'monthly': 2, 'leverage': 3, 'situational': 4, 'through-count': 5, 'sp-rp': 6, 'shifts': 7, 'tto': 8}

CUR_SEASON = '2019'

def conn():
	return pymongo.MongoClient("mongodb+srv://admin:pdometer@mongo-uwij2.mongodb.net/test?retryWrites=true")

def get_player_stats_page(ptype='pit', cat='8', season=CUR_SEASON, active='0'):
	url = '''
	https://www.fangraphs.com/leaders.aspx?
	pos=all&
	stats={}&
	lg=all&
	qual=0&
	type={}&
	season={}&
	month=0&
	season1={}&
	ind=0&
	team=&
	rost={}&
	age=&
	filter=&
	players=&
	page=1_1500
	'''.replace('\t', '').replace('\n', '').strip().format(ptype, cat, season, season, active)
	r = requests.get(url)
	html = r.text.replace('<!--', '').replace('-->', '')
	return BeautifulSoup(html, "lxml")

#"https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=0&type=8&season=1990&month=0&season1=1990&ind=0&team=0,ts&rost=0&age=0&filter=&players=0"
def get_team_stats_page(ptype='bat', cat='8', season=CUR_SEASON, active='0'):
	url = '''
	https://www.fangraphs.com/leaders.aspx?
	pos=all&
	stats={}&
	lg=all&
	qual=0&
	type={}&
	season={}&
	month=0&
	season1={}&
	ind=0&
	team=0,ts&
	rost={}&
	age=0&
	filter=&
	players=0
	'''.replace('\t', '').replace('\n', '').strip().format(ptype, cat, season, season, active)
	r = requests.get(url)
	html = r.text.replace('<!--', '').replace('-->', '')
	return BeautifulSoup(html, "lxml")

def get_table_by_class(page, _class):
	return page.find('table',{'class':_class})

def build_df(table, offset=0, strings=[], ints=[]):
	ths = table.find_all('th')
	headings = []
	for th in ths:
		headings.append(th.text.strip())
	tbody = table.find('tbody')
	rows = tbody.find_all('tr')
	data = []
	for row in rows[offset:]:
		cells = row.find_all('td')
		cells = [cell.text.replace('%', '').strip() for cell in cells]
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

def get_all_pitchers():
	"""
	This method takes the full active pitcher list from fangraphs
	"""
	page = get_player_stats_page(active='1')
	table = get_table_by_class(page, 'rgMasterTable')
	df = build_df(table, strings=['Name', 'Team'], ints=['#'])
	df['fullname'] = ''
	for index, row in df.iterrows():
		df.loc[index, 'fullname'] = row['Name'].replace(' ', '').strip().lower()
	return df

#UNUSED - SAVE for FUTURE DEV
def get_category(cat):
	return gamelog_categories[cat]

def get_split(split):
	return split_categories[split]

def get_sabersim_page(pos, ptype):
	url = "https://www.fangraphs.com/dailyprojections.aspx?pos={}&stats={}&type=sabersim&team=0&lg=all&players=0&page=1_1000".format(pos, ptype)
	r = requests.get(url)
	html = r.text.replace('<!--', '').replace('-->', '')
	return BeautifulSoup(html, "lxml")

def get_gamelog_page(pid, cat='dashboard', start='2019-04-01', end=None):
	if end is None:
		end = str(dt.datetime.now()).split(' ')[0]
	t_num = get_category(cat)
	url = "https://www.fangraphs.com/statsd.aspx?playerid={}&position=P&type={}&gds={}&gde={}".format(pid, t_num, start, end)
	r = requests.get(url)
	html = r.text.replace('<!--', '').replace('-->', '')
	return BeautifulSoup(html, "lxml")

def get_splits_page(pid, season=CUR_SEASON):
	url = "https://www.fangraphs.com/statsplits.aspx?playerid={}&position=P&season={}".format(pid, season)
	r = requests.get(url)
	html = r.text.replace('<!--', '').replace('-->', '')
	return BeautifulSoup(html, "lxml")

def get_splits_leaderboard(season=CUR_SEASON):
	url = "https://www.fangraphs.com/leaderssplits.aspx?splitArr=43,5&strgroup=season&statgroup=1&startDate={}-3-1&endDate={}-11-1&filter=IP%7Cgt%7C20&position=P&statType=player&autoPt=true&players=&pg=0&pageItems=30&sort=19,-1".format(season, season)
	r = requests.get(url)
	html = r.text.replace('<!--', '').replace('-->', '')
	return BeautifulSoup(html, "lxml")

def get_split_data(page, split='handedness'):
	headings = []
	data = []

	table = page.find('table',{'class':'rgMasterTable'})
	thead = table.find('thead')
	tbody = table.find('tbody')
	heads = thead.find_all('tr')
	heads.extend(tbody.find_all('tr', {'class': 'rgHeadSpace'}))

	head = heads[get_split(split)]
	cells = head.find_all(['th', 'td'])
	for cell in cells:
		headings.append(cell.text)

	if split == 'handedness':
		rows = tbody.find_all('tr')
	else:
		rows = head.find_next_siblings('tr')

	for row in rows:
		if row.get('class') == ['rgHeadSpace']:
			break
		cells = row.find_all('td')
		data.append([cell.text for cell in cells])
	df = pd.DataFrame(data=data, columns=headings)
	return df

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("pid", help="playerid of the pitcher")
	parser.add_argument("type", help="type of data ['splits', 'gamelog']")
	parser.add_argument("-c", "--category", help="category of data you want to query\n" + str([key for key in gamelog_categories.keys()]))
	parser.add_argument("-s", "--start", help="start date (only for gamelog)")
	parser.add_argument("-e", "--end", help="end date (only for gamelog)")
	args = parser.parse_args()
	if args.type == 'splits':
		page = get_splits_page(args.pid)
		if args.category:
			df = get_split_data(page, split=args.category)
		else:
			df = get_split_data(page)
		print(df)
	elif args.type == 'gamelog':
		if args.category and args.start and args.end:
			page = get_gamelog_page(args.pid, cat=args.category, start=args.start, end=args.end)
		elif args.category and args.start:
			page = get_gamelog_page(args.pid, cat=args.category, start=args.start)
		elif args.category and args.end:
			page = get_gamelog_page(args.pid, cat=args.category, end=args.end)
		elif args.category:
			page = get_gamelog_page(args.pid, cat=args.category)
		elif args.start and args.end:
			page = get_gamelog_page(args.pid, start=args.start, end=args.end)
		elif args.start:
			page = get_gamelog_page(args.pid, start=args.start)
		elif args.end:
			page = get_gamelog_page(args.pid, end=args.end)
		else:
			page = get_gamelog_page(args.pid)
		df = get_table(page, offset=2)
		print(df)

if __name__ == '__main__':
	main()