import numpy as np
import pandas as pd
import basketballref as br
import json
import pymongo #pymongo-3.7.2
import os
import argparse

CUR_SEASON = "2020"

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

def load_team_misc():
	page = br.get_team_stats_page()
	table = br.get_table_by_id(page, 'misc_stats')
	df = br.build_df(table, 0, ['Team', 'Arena'], ['Rk', 'W', 'L', 'PW', 'PL'])
	refresh_table('NBA_TEAM', 'br_team_misc', df)

def main():
	load_team_misc()

if __name__ == '__main__':
	main()