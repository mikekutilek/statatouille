import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import sys, json, re, time, io

CUR_SEASON = '2019'

def get_search_page(hfGT='R', hfSea=CUR_SEASON, player_type='pitcher', batter_stands='', position='', hfInn='', min_results='', group_by='name', sort_col=''):
	url = '''
	https://baseballsavant.mlb.com/statcast_search?
	hfPT=&
	hfAB=&
	hfBBT=&
	hfPR=&
	hfZ=&
	stadium=&
	hfBBL=&
	hfNewZones=&
	hfGT={}%7C&
	hfC=&
	hfSea={}%7C&
	hfSit=&
	player_type={}&
	hfOuts=&
	opponent=&
	pitcher_throws=&
	batter_stands={}&
	hfSA=&
	game_date_gt=&
	game_date_lt=&
	hfInfield=&
	team=&
	position={}&
	hfOutfield=&
	hfRO=&
	home_road=&
	hfFlag=&
	hfPull=&
	metric_1=&
	hfInn={}&
	min_pitches=0&
	min_results={}&
	group_by={}&
	sort_col={}&
	player_event_sort=h_launch_speed&
	sort_order=desc&
	min_pas=0#results
	'''.replace('\t', '').replace('\n', '').strip().format(hfGT, hfSea, player_type, batter_stands, position, hfInn, min_results, group_by, sort_col)
	r = requests.get(url)
	return BeautifulSoup(r.content, "html.parser")

def get_search_result_table(page):
	table = page.find('table',{'id':'search_results'})
	thead = table.find('thead')
	ths = thead.find_all('th')
	headings = []
	for th in ths:
		headings.append(th.text.strip())
	headings = headings[:-3]
	headings.append("Player ID")
	tbody = table.find('tbody')
	rows = tbody.find_all('tr')
	data = []
	for row in rows[::2]:
		player_id = row.attrs['id'][12:18]
		cells = row.find_all('td')
		row_data = []
		for cell in cells:
			row_data.append(cell.text.strip())
		row_data.append(player_id)
		data.append(row_data)
	df = pd.DataFrame(data=data, columns=headings)
	return df

def get_player_page(firstName='', lastName='', playerId='', category='career', szn_split='r', statType='', league='mlb', season=CUR_SEASON):
	url = '''
	https://baseballsavant.mlb.com/savant-player/
	{}-{}-{}?
	stats={}-{}-{}-{}&
	season={}
	'''.replace('\t', '').replace('\n', '').strip().format(firstName, lastName, playerId, category, szn_split, statType, league, season)
	r = requests.get(url)
	html = r.text.replace('<!--', '').replace('-->', '')
	return BeautifulSoup(html, 'lxml')

def get_pitcher_page(firstName='', lastName='', playerId=''):
	return get_player_page(firstName, lastName, playerId, statType='pitching')

def get_batter_page(firstName='', lastName='', playerId=''):
	return get_player_page(firstName, lastName, playerId, statType='hitting')

def get_table_from_css(page, css):
	return page.select_one(css)

def build_df(table):
	ths = table.find_all('th')
	headings = []
	for th in ths:
		headings.append(th.text.strip())
	tbody = table.find('tbody')
	rows = tbody.find_all('tr')
	data = []
	for row in rows:
		cells = row.find_all('td')
		data.append([cell.text.strip() for cell in cells])
	df = pd.DataFrame(data=data, columns=headings)
	return df

#UNUSED - SAVE for FUTURE DEV
def get_leaderboard_page():
	r = requests.get("https://baseballsavant.mlb.com/expected_statistics?csv=true").content
	return r

def get_zones_page(playerId='', playerType='', season=CUR_SEASON, hand=''):
	url = '''
	https://baseballsavant.mlb.com/player-services/zones?
	playerIds={}&
	playerType={}&
	season={}&
	hand={}
	'''.replace('\t', '').replace('\n', '').strip().format(playerId, playerType, season, hand)
	r = requests.get(url)
	html = r.text.replace('<!--', '').replace('-->', '')
	return BeautifulSoup(html, 'lxml')

def get_pitch_type_breakdown_page():
	url = '''
	https://baseballsavant.mlb.com/player-services/statcast-pitches-breakdown?
	playerId=605397&
	position=1&
	hand=&
	pitchBreakdown=pitches&
	timeFrame=game&
	season=&
	pitchType=&
	updatePitches=false
	'''.replace('\t', '').replace('\n', '').strip()
	r = requests.get(url)
	return BeautifulSoup(r.content, "html.parser")

def get_leaderboard_table(page):
	df = pd.read_csv(io.StringIO(page.decode('utf-8')))
	return df

def get_zone_data(page):
	arr = eval('[' + page.text[1:-1] + ']')
	return pd.DataFrame(arr)

#print(get_zone_data(get_zones_page(playerId='605397', playerType='pitching', hand='L')))