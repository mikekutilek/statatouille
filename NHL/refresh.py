import numpy as np
import pandas as pd
import hockeyref as hr
import fp
import natstattrick as nst
import fantasylabs as fl
import sys, json, argparse
from datetime import datetime
import pymongo #pymongo-3.7.2

def conn():
	return pymongo.MongoClient("mongodb+srv://admin:pdometer@mongo-uwij2.mongodb.net/test?retryWrites=true")

def refresh_table(db_name, table_name, df):
	data_json = df.to_json(orient='records')
	client = conn()
	db = client[db_name]
	table = db[table_name]
	table.drop()
	table.insert(json.loads(data_json))

def load_skater_basic():
	page = hr.get_all_skaters_page()
	df = hr.get_table(page)
	refresh_table('NHL_PLAYER', 'skater_basic', df)

def load_skater_advanced():
	page = hr.get_advanced_skaters_page()
	df = hr.get_table(page)
	refresh_table('NHL_PLAYER', 'skater_advanced', df)

def load_skater_fp():
	df = fp.get_all_skater_fps()
	refresh_table('NHL_PLAYER', 'skater_fp', df)

def load_goalie_basic():
	page = hr.get_all_goalies_page()
	df = hr.get_table(page)
	refresh_table('NHL_PLAYER', 'goalie_basic', df)

def load_goalie_fp():
	df = fp.get_all_goalie_fps()
	refresh_table('NHL_PLAYER', 'goalie_fp', df)

def load_teams():
	df = json.load(open("data/teams.json"))
	client = conn()
	db = client['NHL_TEAM']
	table = db['teams']
	table.drop()
	table.insert(df)

def load_hr_gamelogs():
	page = hr.get_gamelogs_page()
	table = hr.get_table_by_id(page, 'games')
	df = hr.build_df(table)
	df = df.iloc[::-1]
	today = datetime.today().strftime('%Y-%m-%d')
	df = df[df['Date'] < today]
	refresh_table('NHL_GAMES', 'hr_gamelogs', df)

def load_nst_gamelogs(season, situation):
	page = nst.get_gamelogs_page(season, situation)
	table = nst.get_table_by_id(page, 'teams')
	df = nst.build_df(table, ['Game', 'Team', '', 'TOI', 'Result', 'Date'], [])
	df = df.iloc[::-1]
	refresh_table('NHL_GAMES', 'nst_gamelogs_'+situation+'_'+season, df)

def load_fantasylabs_gamelogs(season):
	df = fl.get_season_gamelogs(season)
	refresh_table('NHL_GAMES', 'fantasylabs_'+season, df)

def main(args):
	if args.hist:
		load_teams()
		load_nst_gamelogs('20112012', 'all')
		load_nst_gamelogs('20112012', '5v5')
		load_nst_gamelogs('20122013', 'all')
		load_nst_gamelogs('20122013', '5v5')
		load_nst_gamelogs('20132014', 'all')
		load_nst_gamelogs('20132014', '5v5')
		load_nst_gamelogs('20142015', 'all')
		load_nst_gamelogs('20142015', '5v5')
		load_nst_gamelogs('20152016', 'all')
		load_nst_gamelogs('20152016', '5v5')
		load_nst_gamelogs('20162017', 'all')
		load_nst_gamelogs('20162017', '5v5')
		load_nst_gamelogs('20172018', 'all')
		load_nst_gamelogs('20172018', '5v5')
		load_nst_gamelogs('20182019', 'all')
		load_nst_gamelogs('20182019', '5v5')
	if args.daily:
		load_teams()
		load_skater_basic()
		load_skater_advanced()
		load_skater_fp()
		load_goalie_basic()
		load_goalie_fp()
		load_fantasylabs_gamelogs('20192020')
		load_nst_gamelogs('20192020', 'all')
		load_nst_gamelogs('20192020', '5v5')

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='SABR Daily Data Refresh')
	parser.add_argument('--daily', action='store_true', help="Choose whether to run the daily data refresh or not")
	parser.add_argument('--hist', action='store_true', help="Choose whether to run the historical data refresh or not")
	args = parser.parse_args()
	main(args)