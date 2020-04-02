import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import hockeyref as hr
from datetime import timedelta, date, datetime
import pymongo #pymongo-3.7.2

def conn():
	return pymongo.MongoClient("mongodb+srv://admin:pdometer@mongo-uwij2.mongodb.net/test?retryWrites=true")

def get_page(url):
	r = requests.get(url)
	html = r.text.replace('<!--', '').replace('-->', '')
	return BeautifulSoup(html, "lxml")

def get_table_by_id(page, table_id):
	return page.find_all('table', id=table_id)

def get_table_by_class(page, _class):
	return page.find_all('table',{'class':_class})

def daterange(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + timedelta(n)

def get_gamelogs(date='2012_02_15'):
	url = "https://www.fantasylabs.com/api/sportevents/4/{}".format(date)
	resp = requests.get(url)
	data = resp.json()
	final_data = []
	for d in data:
		fantasylabs_id = d['EventId']
		event_date = d['EventDate'].split('T')[0]
		away_team = d['VisitorTeam']
		home_team = d['HomeTeam']
		away_total = d['VisitorScore']
		home_total = d['HomeScore']
		game_total = away_total + home_total
		if away_total > home_total:
			away_result = 'W'
			home_result = 'L'
		elif home_total > away_total:
			away_result = 'L'
			home_result = 'W'
		else:
			away_result = ''
			home_result = ''
		spread = d['Spread']
		away_spread_odds = d['SpreadMoney1']
		home_spread_odds = d['SpreadMoney2']
		away_ml = d['MLVisitor']
		home_ml = d['MLHome']
		over_under = d['OU']
		over_odds = d['OuMoney1']
		under_odds = d['OuMoney2']
		final_data.append({'DATE': event_date, 
			'AWAY RESULT': away_result, 
			'HOME RESULT': home_result, 
			'AWAY TEAM': away_team, 
			'HOME TEAM': home_team, 
			'AWAY TOTAL': away_total, 
			'HOME TOTAL': home_total, 
			'GAME TOTAL': game_total, 
			'SPREAD': spread, 
			'AWAY SPREAD ODDS': away_spread_odds, 
			'HOME SPREAD ODDS': home_spread_odds, 
			'AWAY ML': away_ml, 
			'HOME ML': home_ml, 
			'OVER UNDER': over_under, 
			'OVER ODDS': over_odds, 
			'UNDER ODDS': under_odds})
	return final_data
	#df = pd.DataFrame(final_data)
	#return df


def get_streaks(team, date):
	year = date.split('-')[0]
	month = date.split('-')[1]
	if int(month) > 7:
		otheryear = int(year) + 1
		season = year + str(otheryear)
	else:
		otheryear = int(year) - 1
		season = str(otheryear) + year
	nst_gamelogs = []
	l_streak = 0
	w_streak = 0
	goal_count = 0
	client = conn()
	db = client['NHL_GAMES']
	table = db['nst_gamelogs_all_'+season]
	data = table.find({ "$and": [{'Date': {"$lt": date}, 'Team': team}]})
	#data = table.find({ "$and": [{'Date': {"$lt": date}, "$or": [{'Home': team}, {'Visitor': team}]}]})
	for d in data:
		nst_gamelogs.append(d)
	nst_df = pd.DataFrame(nst_gamelogs)
	for index, row in nst_df.iterrows():
		if row['Result'] == 'L':
			if w_streak > 0: #LOST ON A WIN STREAK
				break
			else:
				l_streak = l_streak + 1
				goal_count += int(row['GF'])
		else: #WON
			if l_streak > 0:
				break
			else:
				w_streak = w_streak + 1
				goal_count += int(row['GF'])
	#hr_df = hr_df[hr_df['Date'] < date]
	"""
	for index, row in hr_df.iterrows():
		if (row['Home'] == team):
			if (int(row['AWAY_G']) > int(row['HOME_G'])): #LOST
				if w_streak > 0: #LOST ON A WIN STREAK
					break
				else:
					l_streak = l_streak + 1
					goal_count += int(row['HOME_G'])
			else: #WON
				if l_streak > 0:
					break
				else:
					w_streak = w_streak + 1
					goal_count += int(row['HOME_G'])
		elif (row['Visitor'] == team):
			if (int(row['HOME_G']) > int(row['AWAY_G'])): #LOST
				if w_streak > 0: #LOST ON A WIN STREAK
					break
				else:
					l_streak = l_streak + 1
					goal_count += int(row['AWAY_G'])
			else: #WON
				if l_streak > 0:
					break
				else:
					w_streak = w_streak + 1
					goal_count += int(row['AWAY_G'])
	"""
	return l_streak, w_streak, goal_count

def get_fancystats(team, date, maxgames):
	year = date.split('-')[0]
	month = date.split('-')[1]
	if int(month) > 7:
		otheryear = int(year) + 1
		season = year + str(otheryear)
	else:
		otheryear = int(year) - 1
		season = str(otheryear) + year
	nst_gamelogs = []
	client = conn()
	db = client['NHL_GAMES']
	table = db['nst_gamelogs_5v5_'+season]
	this_games_data = table.find({ "$and": [{'Date': date, 'Team': team}]})
	result = this_games_data[0]['Result']
	season_avg_exp_gf_percentage = 0
	recent_games_exp_gf_percentage = 0
	past_games_data = table.find({ "$and": [{'Date': {"$lt": date}, 'Team': team}]})
	for d in past_games_data:
		nst_gamelogs.append(d)
	if len(nst_gamelogs) > 0:
		nst_df = pd.DataFrame(nst_gamelogs)
		#print(nst_df)
		nst_df_past_n = nst_df.loc[0:maxgames]
		season_avg_exp_gf_percentage = nst_df['xGF%'].mean()
		recent_games_exp_gf_percentage = nst_df_past_n['xGF%'].mean()
	
	#print(season_avg_exp_gf_percentage, recent_games_exp_gf_percentage)
	return result, season_avg_exp_gf_percentage, recent_games_exp_gf_percentage

def get_full_boxscore(date='2020-01-27'):
	url = "https://www.covers.com/sports/NHL/matchups?selectedDate={}".format(date)
	page = get_page(url)
	games = page.find_all('div', {'class':'cmg_matchup_list_gamebox'})
	final_data = []
	for game in games:
		box_url = game.find_all('a')[0]['href']
		box_page = get_page(box_url)
		tables = get_table_by_class(box_page, 'covers-CoversMatchupDetails-inGameTable')
		dfs = []
		for table in tables:
			thead = table.find('thead')
			ths = thead.find_all('th')
			headings = []
			for th in ths:
				if th.text.strip() == '':
					headings.append('Team')
				else:
					headings.append(th.text.strip())
			tbody = table.find('tbody')
			rows = tbody.find_all('tr')
			data = []
			for row in rows:
				cells = row.find_all(['th', 'td'])
				cells = [cell.text.replace('*', '').replace('#', '').replace('%', '').strip() for cell in cells]
				data.append([cell for cell in cells])
			df = pd.DataFrame(data=data, columns=headings)
			dfs.append(df)
		game_df = dfs[0].merge(dfs[1], on='Team', how='left')
		away_team = game_df['Team'][0]
		home_team = game_df['Team'][1]
		away_total = game_df['Total'][0]
		home_total = game_df['Total'][1]
		game_total = game_df['Total'].astype(float).sum()
		away_ml = game_df['ML'][0]
		home_ml = game_df['ML'][1]

		client = conn()
		db = client['NHL_TEAM']
		collection = db['teams']
		away_data = collection.find({'abbrs.covers': away_team})
		if (away_team == 'ARI' and date < '2014-10-01'):
			away_full_name = away_data[0]['full_name'][1]
		else:
			away_full_name = away_data[0]['full_name'][0]
		away_l_streak, away_w_streak, away_goal_count = get_streaks(away_full_name, date)
		home_data = collection.find({'abbrs.covers': home_team})
		if (home_team == 'ARI' and date < '2014-10-01'):
			home_full_name = home_data[0]['full_name'][1]
		else:
			home_full_name = home_data[0]['full_name'][0]
		home_l_streak, home_w_streak, home_goal_count = get_streaks(home_full_name, date)
		away_streak_int = 0
		home_streak_int = 0
		if home_l_streak > home_w_streak:
			home_streak_int = home_l_streak
			home_streak = 'L' + str(home_l_streak)
		elif home_w_streak > home_l_streak:
			home_streak_int = home_w_streak
			home_streak = 'W' + str(home_w_streak)
		else:
			home_streak_int = 0
			home_streak = '0'
		if away_l_streak > away_w_streak:
			away_streak_int = away_l_streak
			away_streak = 'L' + str(away_l_streak)
		elif away_w_streak > away_l_streak:
			away_streak_int = away_w_streak
			away_streak = 'W' + str(away_w_streak)
		else:
			away_streak_int = 0
			away_streak = '0'

		away_result, away_season_avg_exp_gf_percentage, away_recent_games_exp_gf_percentage = get_fancystats(away_full_name, date, away_streak_int)
		home_result, home_season_avg_exp_gf_percentage, home_recent_games_exp_gf_percentage = get_fancystats(home_full_name, date, home_streak_int)
		away_streak_gf_percentage_diff = away_recent_games_exp_gf_percentage - away_season_avg_exp_gf_percentage
		home_streak_gf_percentage_diff = home_recent_games_exp_gf_percentage - home_season_avg_exp_gf_percentage
		final_data.append({'DATE': date, 
			'AWAY RESULT': away_result, 
			'HOME RESULT': home_result, 
			'AWAY TEAM': away_team, 
			'HOME TEAM': home_team, 
			'AWAY TOTAL': away_total, 
			'HOME TOTAL': home_total, 
			'GAME TOTAL': game_total, 
			'AWAY ML': away_ml, 
			'HOME ML': home_ml, 
			'AWAY STREAK': away_streak, 
			'HOME STREAK': home_streak, 
			'AWAY RECENT GOALS': away_goal_count, 
			'HOME RECENT GOALS': home_goal_count, 
			'AWAY xGF% SEASON': away_season_avg_exp_gf_percentage, 
			'HOME xGF% SEASON': home_season_avg_exp_gf_percentage, 
			'AWAY xGF% STREAK': away_recent_games_exp_gf_percentage, 
			'HOME xGF% STREAK': home_recent_games_exp_gf_percentage, 
			'AWAY xGF% STREAK DIFF': away_streak_gf_percentage_diff, 
			'HOME xGF% STREAK DIFF': home_streak_gf_percentage_diff})
		#print(game_df)
	final_df = pd.DataFrame(final_data)
	return final_df

def get_season_gamelogs(season):
	first_year = season[0:4]
	second_year = season[4:8]
	start_date = datetime.strptime((first_year + '_10_01'), "%Y_%m_%d")
	end_date = datetime.strptime((second_year + '_07_01'), "%Y_%m_%d")
	final_data = []
	day_count = (end_date - start_date).days + 1
	for single_date in daterange(start_date, end_date):
		gamelogs = get_gamelogs(single_date.strftime("%Y_%m_%d"))
		for game in gamelogs:
			final_data.append(game)

	#today_data = get_gamelogs(date)
	#for d in today_data:
	#	final_data.append(d)

	final_df = pd.DataFrame(final_data)
	return final_df

#var1, var2 = get_fancystats('Los Angeles Kings', '2019-12-21', 2)
#print(type(var1))
#print(type(var2))
#print(get_fancystats('Florida Panthers', '2019-10-03', 1))

print(get_fancystats('Toronto Maple Leafs', '2020-02-05', 5))