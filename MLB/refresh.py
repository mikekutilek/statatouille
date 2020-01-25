import numpy as np
import pandas as pd
import baseballref as bref
import savant as sa
import fangraphs as fg
import fp
import opener as op
import historical as hist
import extract as ext
import war_model as wm
import json
import pymongo #pymongo-3.7.2
import os
import argparse

CUR_SEASON = "2019"

def conn():
	return pymongo.MongoClient("mongodb+srv://admin:pdometer@mongo-uwij2.mongodb.net/test?retryWrites=true")

def refresh_table(db_name, table_name, df):
	data_json = df.to_json(orient='records')
	client = conn()
	db = client[db_name]
	table = db[table_name]
	if table.count() != 0:
		table.drop()
	table.insert(json.loads(data_json))

def insert_to_table(db_name, table_name, df):
	data_json = df.to_json(orient='records')
	client = conn()
	db = client[db_name]
	table = db[table_name]
	table.insert(json.loads(data_json))

def load_teams():
	df = json.load(open("data/teams.json"))
	client = conn()
	db = client['MLB_TEAM']
	table = db['teams']
	table.drop()
	table.insert(df)

def load_team_historical(source, season_range):
	for season in season_range:
		if source == 'fg':
			df = hist.get_finished_df(season, 'fg')
			refresh_table('MLB_TEAM_HISTORICAL', 'fg_dashboard_'+str(season), df)
		elif source == 'bp' and season >= 1921:
			df = hist.get_finished_df(season, 'bp')
			refresh_table('MLB_TEAM_HISTORICAL', 'bp_team_warp_'+str(season), df)

def load_active_pitchers():
	active_df = fg.get_all_pitchers()
	df = hist.teamname_to_abbr(active_df)
	refresh_table('MLB_PLAYER', 'fg_pitchers_active', df)

def load_bref_team_sp():
	url = "https://www.baseball-reference.com/leagues/MLB/{}-starter-pitching.shtml".format(CUR_SEASON)
	page = bref.get_page(url)
	df = bref.build_df(bref.get_table_by_class(page, 'stats_table'), 0, ['Tm'], ['']).sort_values(by=['GmScA'], ascending=False)
	refresh_table('MLB_TEAM', 'bref_team_sp', df)

def load_batter_fp():
	df = fp.get_all_batter_fps()
	refresh_table('MLB_PLAYER', 'fp_batter', df)

def load_pitcher_fp():
	df = fp.get_all_pitcher_fps()
	refresh_table('MLB_PLAYER', 'fp_pitcher', df)

def load_opener_candidates():
	rrp_df = op.get_all_candidates('R', 'RP')
	lrp_df = op.get_all_candidates('L', 'RP')
	rsp_df = op.get_all_candidates('R', 'SP')
	lsp_df = op.get_all_candidates('L', 'SP')
	refresh_table('MLB_PLAYER', 'opener_candidates', rrp_df)
	insert_to_table('MLB_PLAYER', 'opener_candidates', lrp_df)
	insert_to_table('MLB_PLAYER', 'opener_candidates', rsp_df)
	insert_to_table('MLB_PLAYER', 'opener_candidates', lsp_df)

def load_daily_graphs():
	df = ext.load_table('MLB_TEAM_HISTORICAL', 'bp_team_warp_'+CUR_SEASON)
	wm.plot_drc_vs_dra(df)

def main(args):
	if args.hist:
		if args.start_year and args.end_year:
			season_range = np.arange(int(args.start_year), int(args.end_year))
		elif args.start_year:
			season_range = np.arange(int(args.start_year), int(CUR_SEASON)+1)
		elif args.end_year:
			if args.bp:
				season_range = np.arange(1951, int(args.end_year))
			else:
				season_range = np.arange(1903, int(args.end_year))
		else:
			season_range = np.arange(1903, int(CUR_SEASON)+1)
		
		if args.bp:
			load_teams()
			load_team_historical('bp', season_range)
		elif args.fg:
			load_teams()
			load_team_historical('fg', season_range)
		else:
			print("### RUNNING HISTORICAL LOAD ###")
			load_teams()
			load_team_historical('fg', season_range)
			load_team_historical('bp', season_range)
			print("### HISTORICAL LOAD COMPLETES ###")
	if args.daily:
		print("### RUNNING DAILY LOAD ###")
		season_range = np.arange(int(CUR_SEASON), int(CUR_SEASON)+1)
		load_team_historical('bp', season_range)
		load_active_pitchers()
		load_bref_team_sp()
		load_batter_fp()
		load_pitcher_fp()
		load_opener_candidates()
		load_daily_graphs()
		print("### DAILY LOAD COMPLETES ###")

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='SABR Daily Data Refresh')
	parser.add_argument('--daily', action='store_true', help="Choose whether to run the daily data refresh or not")
	parser.add_argument('--hist', action='store_true', help="Choose whether to run the historical data refresh or not")
	parser.add_argument('--bp', action='store_true', help="Only run bp section of the historical refresh")
	parser.add_argument('--fg', action='store_true', help="Only run fg section of the historical refresh")
	parser.add_argument('--start_year', help="Specify a start year for historical refresh")
	parser.add_argument('--end_year', help="Specify an end year for historical refresh")
	args = parser.parse_args()
	main(args)
	#load_teams()