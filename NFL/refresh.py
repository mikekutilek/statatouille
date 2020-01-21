import numpy as np
import pandas as pd
import airyards as ay
import fp
import sys, json, argparse
import pymongo #pymongo-3.7.2

def conn():
	return pymongo.MongoClient("mongodb+srv://admin:pdometer@mongo-uwij2.mongodb.net/test?retryWrites=true")

def refresh_table(table_name, df):
	data_json = df.to_json(orient='records')
	client = conn()
	db = client['WOPR']
	table = db[table_name]
	table.drop()
	table.insert(json.loads(data_json))

def insert_to_table(table_name, df):
	data_json = df.to_json(orient='records')
	client = conn()
	db = client['WOPR']
	table = db[table_name]
	table.insert(json.loads(data_json))

def load_air_yards():
	df = ay.get_ay_data()
	refresh_table('air_yards', df)

def load_pfr_rushing():
	page = ay.get_pfr_rushing()
	df = ay.get_table(page)
	refresh_table('pfr_rushing', df)

def load_pfr_fantasy():
	page = ay.get_pfr_fantasy()
	df = ay.get_table(page)
	refresh_table('pfr_fantasy', df)

def load_pfr_scoring():
	page = ay.get_pfr_scoring()
	df = ay.get_table(page)
	refresh_table('pfr_scoring', df)

def load_fp():
	qb_df = fp.get_fp('QB')
	rb_df = fp.get_fp('RB')
	wr_df = fp.get_fp('WR')
	te_df = fp.get_fp('TE')
	refresh_table('fp', qb_df)
	insert_to_table('fp', rb_df)
	insert_to_table('fp', wr_df)
	insert_to_table('fp', te_df)

def main():
	load_air_yards()
	load_pfr_rushing()
	load_pfr_fantasy()
	load_pfr_scoring()
	load_fp()

if __name__ == '__main__':
	main()