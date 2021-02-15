import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import hockeyref as hr
import pymongo #pymongo-3.7.2

def conn():
	return pymongo.MongoClient("mongodb+srv://admin:pdometer@mongo-uwij2.mongodb.net/test?retryWrites=true")

def get_dog_percentage(year):
	otheryear = int(year) - 1
	season = str(otheryear) + year
	fl_gamelogs = []
	client = conn()
	db = client['NHL_GAMES']
	table = db['fantasylabs_'+season]
	past_games_data = table.find({})
	for d in past_games_data:
		fl_gamelogs.append(d)
	if len(fl_gamelogs) > 0:
		fl_df = pd.DataFrame(fl_gamelogs)
		df = fl_df[fl_df['AWAY ML'].str.startswith('+') & fl_df['AWAY RESULT'].str.startswith('W')]
		away_dogs = fl_df[fl_df['AWAY ML'].str.startswith('+')]
		away_wins = df.shape[0]
		away_dog_games = away_dogs.shape[0]
		print(int(away_wins) / int(away_dog_games))
	
	#print(season_avg_exp_gf_percentage, recent_games_exp_gf_percentage)
	return fl_df

def combine_nst_data(season):
	winners = []
	losers = []
	client = conn()
	db = client['NHL_GAMES']
	table = db['nst_gamelogs_all_'+season]
	win_data = table.find({'Result': 'W'})
	loss_data = table.find({'Result': 'L'})
	for d in win_data:
		winners.append(d)
	for d in loss_data:
		losers.append(d)
	w_df = pd.DataFrame(winners)
	l_df = pd.DataFrame(losers)
	print(l_df[l_df['Date'] == '2021-02-13'])
	df = w_df.merge(l_df, on=['Game'], suffixes=('_winner', '_loser'))
	print(df[["Game", "Team_winner", "Team_loser", "Date_winner", "Date_loser"]])

combine_nst_data('20202021')
#get_dog_percentage('2018')