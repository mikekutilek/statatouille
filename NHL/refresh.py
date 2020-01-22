import numpy as np
import pandas as pd
import hockeyref as hr
import fp
import sys, json, argparse
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

def main():
	load_skater_basic()
	load_skater_advanced()
	load_skater_fp()
	load_goalie_basic()
	load_goalie_fp()

if __name__ == '__main__':
	main()