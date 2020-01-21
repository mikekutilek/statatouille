import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import sys
import json
import argparse
import fangraphs as fg
import historical as hist
import savant as sa
import extract as ext

def get_rps_wOBA_vs(batter_stands):
	page = sa.get_search_page(batter_stands=batter_stands, position='RP', min_results='30', sort_col='woba')
	data = sa.get_search_result_table(page)
	new_data = pd.DataFrame()
	new_data['Player'] = data['Player']
	new_data['Player ID'] = data['Player ID']
	new_data['wOBA'] = data['wOBA'].astype('float64').apply(lambda x: '{0:.3f}'.format(x))
	return new_data.loc[new_data['wOBA'].astype('float64') < 0.250]

def get_sps_wOBA_vs(batter_stands):
	page = sa.get_search_page(batter_stands=batter_stands, position='SP', hfInn='1%7C', min_results='30', sort_col='woba')
	data = sa.get_search_result_table(page)
	new_data = pd.DataFrame()
	new_data['Player'] = data['Player']
	new_data['Player ID'] = data['Player ID']
	new_data['wOBA'] = data['wOBA'].astype('float64').apply(lambda x: '{0:.3f}'.format(x))
	return new_data.loc[new_data['wOBA'].astype('float64') > 0.350]

def get_all_candidates(batter_stands, position):
	#fg_df = fg.get_all_pitchers()
	#df = hist.teamname_to_abbr(fg_df)
	df = ext.load_table('SABR', 'fg_pitchers_active')
	#print(abbr_df)
	if position == 'RP':
		data = get_rps_wOBA_vs(batter_stands)
	else:
		data = get_sps_wOBA_vs(batter_stands)
	data['Team'] = ''
	data['Pos'] = position
	data['Hand'] = batter_stands
	for index, row in data.iterrows():
		playername = row['Player'].replace(' ', '').strip().lower()
		firstname = row['Player'].split(' ')[0]
		lastname = row['Player'].split(' ')[1:]
		urlname = row['Player'].replace(' ', '-').strip().lower()
		uri = urlname + '-' + row['Player ID']
		if not df.loc[df['fullname'] == playername].empty:
			if (len(df.loc[df['fullname'] == playername]) != 1):
				page = sa.get_pitcher_page(firstname, lastname, row['Player ID'])
				table = sa.get_table_from_css("#pitchingStandard > table")
				t = sa.build_df(table).iloc[[-2]]['Tm'].item()
				data.loc[index, 'Team'] = t
			else:
				t = df.loc[df['fullname'] == playername]['Master Team'].item()
				data.loc[index, 'Team'] = t
	return data

def get_team_candidates(team, batter_stands, position):
	df = get_all_candidates(batter_stands, position)
	if team == 'ANY':
		candidates = df
	else:
		candidates = df.loc[df['Team'] == team]
	return candidates

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("team", help="team of candidates you want to find")
	parser.add_argument("pos", help="position of the player")
	parser.add_argument("hand", help="handedness of the hitter")

	args = parser.parse_args()

	df = get_team_candidates(args.team, args.hand, args.pos)
	print(df.to_json(orient='records'))
	sys.stdout.flush()

if __name__ == '__main__':
	main()