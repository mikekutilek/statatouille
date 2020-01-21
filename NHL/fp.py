import numpy as np
import pandas as pd
import hockeyref as hr
import sys, json, argparse

def get_all_skater_fps():
	skater_page = hr.get_all_skaters_page()
	skaters = hr.get_table(skater_page)
	skaters = skaters.replace('', 0)
	players = skaters['Player'].astype('str')
	
	games = skaters['GP'].astype('float64')
	goals = skaters['G'].astype('float64')
	assists = skaters['A'].astype('float64')
	pts = skaters['PTS'].astype('float64')
	plus_minus = skaters['+/-'].astype('float64')
	ppg = skaters['PPG'].astype('float64')
	shg = skaters['SHG'].astype('float64')
	gwg = skaters['GW'].astype('float64')
	ppa = skaters['PPA'].astype('float64')
	sha = skaters['SHA'].astype('float64')
	shots = skaters['S'].astype('float64')
	blocks = skaters['BLK'].fillna(0).astype('float64')
	hits = skaters['HIT'].astype('float64')

	fps = (goals * 5) + (assists * 3) + (plus_minus * 1) + (ppg * 2) + (ppa * 2) + (gwg * 1) + (shg * 2) + (sha * 2) + (shots * 0.1) + (blocks * 0.025) + (hits * 0.025)
	fps_g = fps / games

	df = build_fp_table(players, fps, fps_g)

	return df

def get_all_goalie_fps():
	goalie_page = hr.get_all_goalies_page()
	goalies = hr.get_table(goalie_page)
	goalies = goalies.replace('', 0)
	players = goalies['Player'].astype('str')

	games = goalies['GP'].astype('float64')
	wins = goalies['W'].astype('float64')
	losses = goalies['L'].astype('float64')
	otl = goalies['T/O'].astype('float64')
	ga = goalies['GA'].astype('float64')
	saves = goalies['SV'].astype('float64')
	shutouts = goalies['SO'].astype('float64')

	fps = (wins * 5) - (losses * 2) - (ga * 1) + (saves * 0.2) + (shutouts * 3)
	fps_g = fps / games

	df = build_fp_table(players, fps, fps_g)

	return df

def get_skater_fps(pname):
	df = get_all_skater_fps()
	player = df[df['Player'] == pname]
	return player

def get_goalie_fps(pname):
	df = get_all_goalie_fps()
	player = df[df['Player'] == pname]
	return player

def build_fp_table(players, fps, fps_g):
	df = pd.DataFrame()
	df['Player'] = players
	df['FP'] = fps.apply(lambda x: '{0:.2f}'.format(x)).astype('float64')
	df['FPG'] = fps_g.apply(lambda x: '{0:.2f}'.format(x)).astype('float64')
	return df


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("ptype", help="type of player (skater or goalie)")
	parser.add_argument("sort_col", help="category you want to sort by")
	args = parser.parse_args()

	data = []

	if args.ptype == 'skater':
		data = get_all_skater_fps()
	elif args.ptype == 'goalie':
		data = get_all_goalie_fps()
	else:
		exit(1)

	if args.sort_col == 'FP':
		sort = 'FP'
	elif args.sort_col == 'FPG':
		sort = 'FP/G'

	data_json = data.sort_values(by=[sort], ascending=False).to_json(orient='records')
	print(data_json)
	
	sys.stdout.flush()

if __name__ == '__main__':
	main()