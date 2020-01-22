import numpy as np
import pandas as pd
import fangraphs as fg
import bpro as bp
import baseballref as bref
import pymongo
import re, json

CUR_SEASON = '2019'
FG_START_YEAR = 1903
BP_START_YEAR = 1921
season_range = np.arange(2018, int(CUR_SEASON))

def conn():
	return pymongo.MongoClient("mongodb+srv://admin:pdometer@mongo-uwij2.mongodb.net/test?retryWrites=true")

def get_fg_team_stats(season, active_roster='0'):
	batter_page = fg.get_team_stats_page(season=season, active=active_roster)
	batter_table = fg.get_table_by_class(batter_page, 'rgMasterTable')
	batter_df = fg.build_df(batter_table, strings=['Team'])

	pitcher_page = fg.get_team_stats_page(ptype='pit', season=season, active=active_roster)
	pitcher_table = fg.get_table_by_class(pitcher_page, 'rgMasterTable')
	pitcher_df = fg.build_df(pitcher_table, strings=['Team'])

	pitcher_adv_page = fg.get_team_stats_page(ptype='pit', cat='1', season=season, active=active_roster)
	pitcher_adv_table = fg.get_table_by_class(pitcher_adv_page, 'rgMasterTable')
	pitcher_adv_df = fg.build_df(pitcher_adv_table, strings=['Team'])

	first_df = pd.merge(batter_df, pitcher_df[['#', 'Team', 'BABIP', 'LOB%', 'GB%', 'HR/FB', 'ERA', 'FIP', 'xFIP', 'WAR']], on='Team', how='left')
	df = pd.merge(first_df, pitcher_adv_df[['Team', 'K%', 'BB%', 'K-BB%', 'ERA-', 'FIP-', 'xFIP-', 'SIERA']], on='Team', how='left')

	df['WAR'] = df['WAR_x'] + df['WAR_y']
	df['Year'] = season
	df['Year'] = df['Year'].astype(int)
	df = df.sort_values(by=['WAR'], ascending=False).reset_index(drop=True)
	df['WAR_RANK'] = df.index + 1
	df = df.rename(columns={"WAR_x": "B_WAR", "WAR_y": "P_WAR", "#_x": "B_WAR_RANK", "#_y": "P_WAR_RANK", "BABIP_x": "bBABIP", "BABIP_y": "pBABIP", "BB%_x": "bBB%", "K%_x": "bK%", "BB%_y": "pBB%", "K%_y": "pK%"})
	df['B_WAR_RANK'] = df['B_WAR_RANK'].astype(int)
	df['P_WAR_RANK'] = df['P_WAR_RANK'].astype(int)
	df['FINISH'] = ''
	#df = df[['Team', 'Year', 'B_WAR', 'P_WAR', 'WAR', 'B_WAR_RANK', 'P_WAR_RANK', 'WAR_RANK', 'FINISH']]
	return df

def get_bp_team_stats(season):
	batter_page = bp.get_team_stats_page(cat='batting', season=season)
	batter_table = bp.get_table_by_id(batter_page, 'TTdata')
	batter_df = bp.build_df(batter_table, ['TEAM', 'LG', 'YEAR'], ['#'])
	batter_df = batter_df.sort_values(by=['BWARP'], ascending=False).reset_index(drop=True)
	batter_df['BWARP_RANK'] = batter_df.index + 1
	pitcher_page = bp.get_team_stats_page(cat='pitching', season=season)
	pitcher_table = bp.get_table_by_id(pitcher_page, 'TTdata')
	pitcher_df = bp.build_df(pitcher_table, ['TEAM', 'LVL', 'YEAR'], ['#'])
	pitcher_df = pitcher_df.sort_values(by=['PWARP'], ascending=False).reset_index(drop=True)
	pitcher_df['PWARP_RANK'] = pitcher_df.index + 1
	df = pd.merge(batter_df[['TEAM', 'PA', 'AB', 'R', 'H', 'HR', 'TB', 'BB', 'IBB', 'SO', 'BBr', 'SOr', 'HBP', 'SF', 'SH', 'RBI', 'SB', 'CS', 'SB%', 'AVG', 'OBP', 'SLG', 'OPS', 'ISO', 'DRAA', 'DRC+', 'BWARP', 'BWARP_RANK']], pitcher_df[['TEAM', 'PA', 'HR', 'ERA', 'FIP', 'TRAA', 'EPAA', 'cFIP', 'DRA-', 'DRA_RELIEF', 'DRA_START', 'PWARP', 'PWARP_RANK']], on='TEAM', how='left')
	df['WARP'] = df['BWARP'] + df['PWARP']
	df['DR'] = df['DRC+'] - df['DRA-']
	df['YEAR'] = season
	df['YEAR'] = df['YEAR'].astype(int)
	df = df.sort_values(by=['WARP'], ascending=False).reset_index(drop=True)
	df['WARP_RANK'] = df.index + 1
	
	
	df = df.rename(columns={"PA_x": "bPA", "PA_y": "pPA", "HR_x": "bHR", "HR_y": "pHR"})
	#df['BWARP_RANK'] = df['BWARP_RANK'].astype(int)
	#df['PWARP_RANK'] = df['PWARP_RANK'].astype(int)
	df['FINISH'] = ''
	df = df[['TEAM', 'YEAR', 'bPA', 'AB', 'R', 'H', 'bHR', 'TB', 'BB', 'IBB', 'SO', 'BBr', 'SOr', 'HBP', 'SF', 'SH', 'RBI', 'SB', 'CS', 'SB%', 'AVG', 'OBP', 'SLG', 'OPS', 'ISO', 'DRAA', 'DRC+', 'BWARP', 'pPA', 'pHR', 'ERA', 'FIP', 'TRAA', 'EPAA', 'cFIP', 'DRA-', 'DRA_RELIEF', 'DRA_START', 'PWARP', 'DR', 'WARP', 'BWARP_RANK', 'PWARP_RANK', 'WARP_RANK', 'FINISH']]
	return df

def get_ws_champs(start_year):
	page = bref.get_page('https://www.baseball-reference.com/postseason/')
	table = bref.get_table_by_id(page, 'postseason_series')
	df = pd.DataFrame(columns=['Year', 'Team'])
	years = []
	champs = []
	rows = table[0].find_all('tr')
	for row in rows:
		cells = row.find_all(['th', 'td'])
		cells = [cell.text.replace('*', '').strip().lower() for cell in cells]
		if "world series" in cells[0]:
			years.append(cells[0].split()[0])
			champs.append(cells[2][:cells[2].index("(")])
	df['Year'] = years
	df['Year'] = df['Year'].astype(int)
	df['Team'] = champs
	return df[df['Year'] >= start_year]

def get_ws_champ(season, start_year):
	df = teamname_to_abbr(get_ws_champs(start_year))
	return df[df['Year'] == season]

def teamname_to_abbr(df):
	"""
	This method takes a dataframe of teams and matches each team's name against a given Team Abbreviation Type stored in MongoDB
	"""
	client = conn()
	db = client['MLB_TEAM']
	table = db['teams']

	team_abbrs = []
	for index, row in df.iterrows():
		if 'Year' in df:
			current_season = row['Year']
		else:
			current_season = int(CUR_SEASON)

		full_name = row['Team'].title().strip()
		name_index = 0

		if 'senators' in full_name.lower():
			if current_season > 1901 and current_season <= 1960:
				team_abbr = 'MIN'
			else:
				team_abbr = 'TEX'
		elif full_name.lower() in ['chi-feds', 'buffeds', 'whales', 'terrapins', 'tip-tops', 'blues', 'green sox', 'blue sox', 'hoosiers', 'packers', 'pepper', 'rebels', 'terriers']:
			team_abbr = full_name
		elif 'colt' in full_name.lower():
			team_abbr = 'HOU'
		else:
			abbr = table.find({"$or":[{'team' : full_name}, {'full_name' : full_name}] })
			team_abbr = abbr[0]['master_abbr']
		team_abbrs.append(team_abbr)
	for i in range(len(team_abbrs)):
		df.loc[i, 'Master Team'] = team_abbrs[i]
	return df

def get_finished_df(season, source):
	"""Function that takes in a team stat dataset from Fangraphs or Baseball Prospectus and joins in some baseball reference data, namely W-L% and postseason finish"""
	if source == 'fg':
		war_df = get_fg_team_stats(str(season))
		pre_df = teamname_to_abbr(war_df)
		start_year = FG_START_YEAR
	elif source == 'bp':
		warp_df = get_bp_team_stats(str(season))
		pre_df = bp.abbr_to_master(warp_df)
		start_year = BP_START_YEAR
	#print(df)

	standings = bref.get_page('https://www.baseball-reference.com/leagues/MLB/{}-standings.shtml'.format(str(season)))
	standings_table = bref.get_table_by_id(standings, 'expanded_standings_overall')
	standings_df = bref.build_df(standings_table, 0, ['Tm', 'Lg', 'Strk', 'pythWL', 'vEast', 'vCent', 'vWest', 'Inter', 'Home', 'Road', 'ExInn', '1Run', 'vRHP', 'vLHP', 'last10', 'last20', 'last30', 'gte.500', 'lt.500'], [])
	bref_df = bref.abbr_to_master(standings_df, season)
	df = pre_df.merge(bref_df[['Master Team', 'W-L%']], on='Master Team', how='left')
	#print(df)
	if season < int(CUR_SEASON):
		if season != 1904 and season != 1994:
			champ = get_ws_champ(season, start_year)['Master Team'].values[0]
			#print(champ)
			champ_row = df['Master Team'] == champ
			idx = df.index[champ_row].tolist()[0]
			df.loc[idx, 'FINISH'] = 'CHAMPION'
	return df