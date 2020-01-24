import numpy as np
import pandas as pd
import basketballref as br
import dk
import fivethirtyeight as fte
import json
import pymongo #pymongo-3.7.2

CUR_SEASON = "2020"

def conn():
	return pymongo.MongoClient("mongodb+srv://admin:pdometer@mongo-uwij2.mongodb.net/test?retryWrites=true")

def moneyline_to_win_percentage(moneylines):
	win_percentage_data = []
	for moneyline in moneylines:
		if moneyline[0] == '-':
			num = int(moneyline)
			win_percentage = (num / (num - 100)) * 100
		else:
			num = int(moneyline[1:])
			win_percentage = (100 / (num + 100)) * 100
		win_percentage_data.append(win_percentage)
	return win_percentage_data

def get_dk_data():
	dk_gamelines = []
	client = conn()
	db = client['NBA_GAMES']
	table = db['dk_gamelines']
	data = table.find({})
	for d in data:
		dk_gamelines.append(d)
	df = pd.DataFrame(dk_gamelines)
	away_moneylines = df['AWAY ML']
	home_moneylines = df['HOME ML']
	df['DK AWAY WIN%'] = moneyline_to_win_percentage(away_moneylines)
	df['DK HOME WIN%'] = moneyline_to_win_percentage(home_moneylines)
	df['AWAY TEAM'] = df['AWAY TEAM'].str.split(" ", expand = True)[1]
	df['HOME TEAM'] = df['HOME TEAM'].str.split(" ", expand = True)[1]
	return df

def get_fte_data():
	fte_gamelines = []
	client = conn()
	db = client['NBA_GAMES']
	table = db['538_gamelines']
	data = table.find({})
	for d in data:
		fte_gamelines.append(d)
	df = pd.DataFrame(fte_gamelines)
	df = df.rename(columns={'AWAY SPREAD': '538 AWAY SPREAD', 'HOME SPREAD': '538 HOME SPREAD'})
	return df

def get_moneyline_value(sportsbook_data, model_data):
	df = sportsbook_data.merge(model_data, on=['AWAY TEAM', 'HOME TEAM'], how='left')
	df['AWAY LEVERAGE'] = df['AWAY WIN%'].astype('double') - df['DK AWAY WIN%'].astype('double')
	df['HOME LEVERAGE'] = df['HOME WIN%'].astype('double') - df['DK HOME WIN%'].astype('double')
	return df

dk_df = get_dk_data()
fte_df = get_fte_data()
df = get_moneyline_value(dk_df, fte_df)
print(df)