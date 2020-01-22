import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.font_manager import FontProperties
import fangraphs as fg
import baseballref as bref
import historical as hist
import bpro as bp
import extract as ext
import pymongo
import datetime
from sklearn import linear_model

CUR_SEASON = '2019'
FG_SEASON_RANGE = np.arange(1903, int(CUR_SEASON))
BP_SEASON_RANGE = np.arange(1921, int(CUR_SEASON))

def conn():
	return pymongo.MongoClient("mongodb+srv://admin:pdometer@mongo-uwij2.mongodb.net/test?retryWrites=true")

def get_war_rank_data():
	client = conn()
	db = client['MLB_TEAM_HISTORICAL']
	war_ranks = []
	bwar_ranks = []
	pwar_ranks = []
	seasons = []
	for season in FG_SEASON_RANGE:
		if season == 1904 or season == 1994:
			continue
		table = db['fg_dashboard_' + str(season)]
		champ = table.find({'FINISH' : 'CHAMPION'})
		year = champ[0]['Year']
		war_rank = champ[0]['WAR_RANK']
		bwar_rank = champ[0]['B_WAR_RANK']
		pwar_rank = champ[0]['P_WAR_RANK']
		war_ranks.append(war_rank)
		bwar_ranks.append(bwar_rank)
		pwar_ranks.append(pwar_rank)
		seasons.append(year)
	df = pd.DataFrame()
	df['WAR_RANK'] = war_ranks
	df['BWAR_RANK'] = bwar_ranks
	df['PWAR_RANK'] = pwar_ranks
	df['YEAR'] = seasons
	df['YEAR'] = pd.to_datetime(df['YEAR'], format='%Y')
	return df

def get_warp_rank_data():
	client = conn()
	db = client['MLB_TEAM_HISTORICAL']
	war_ranks = []
	bwar_ranks = []
	pwar_ranks = []
	seasons = []
	for season in BP_SEASON_RANGE:
		if season == 1904 or season == 1994:
			continue
		table = db['bp_team_warp_' + str(season)]
		champ = table.find({'FINISH' : 'CHAMPION'})
		year = champ[0]['YEAR']
		war_rank = champ[0]['WARP_RANK']
		bwar_rank = champ[0]['BWARP_RANK']
		pwar_rank = champ[0]['PWARP_RANK']
		war_ranks.append(war_rank)
		bwar_ranks.append(bwar_rank)
		pwar_ranks.append(pwar_rank)
		seasons.append(year)
	df = pd.DataFrame()
	df['WARP_RANK'] = war_ranks
	df['BWARP_RANK'] = bwar_ranks
	df['PWARP_RANK'] = pwar_ranks
	df['YEAR'] = seasons
	df['YEAR'] = pd.to_datetime(df['YEAR'], format='%Y')
	return df

def plot_fwar_histogram(df):
	gs = gridspec.GridSpec(4, 4)
	fig = plt.figure(figsize=(8, 8))
	ax = fig.add_subplot(gs[2:4, 1:3])
	ax2 = fig.add_subplot(gs[:2, :2])
	ax3 = fig.add_subplot(gs[:2, 2:])
	plt.title("A Look At Where WS Champions Rank in fWAR (FanGraphs)", fontsize=24)
	ax.set_title('Cumulative fWAR', fontsize=16)
	ax.set_xlabel('fWAR Rank', fontsize=12)
	ax.set_ylabel('Championships', fontsize=12)
	ax2.set_title('Position Player fWAR', fontsize=16)
	ax2.set_xlabel('fWAR Rank', fontsize=12)
	ax2.set_ylabel('Championships', fontsize=12)
	ax3.set_title('Pitcher fWAR', fontsize=16)
	ax3.set_xlabel('fWAR Rank', fontsize=12)
	ax3.set_ylabel('Championships', fontsize=12)
	ax.hist(df['WAR_RANK'].values, bins=np.arange(1, 30)-0.5)
	ax2.hist(df['BWAR_RANK'].values, bins=np.arange(1, 30)-0.5)
	ax3.hist(df['PWAR_RANK'].values, bins=np.arange(1, 30)-0.5)
	fig.tight_layout()
	plt.savefig('graphs/fwar_ranks_hist.png')

def plot_warp_histogram(df):
	gs = gridspec.GridSpec(4, 4)
	fig = plt.figure(figsize=(8, 8))
	ax = fig.add_subplot(gs[2:4, 1:3])
	ax2 = fig.add_subplot(gs[:2, :2])
	ax3 = fig.add_subplot(gs[:2, 2:])
	plt.title("A Look At Where WS Champions Rank in WARP (Baseball Prospectus)", fontsize=24)
	ax.set_title('Cumulative WARP', fontsize=16)
	ax.set_xlabel('WARP Rank', fontsize=12)
	ax.set_ylabel('Championships', fontsize=12)
	ax2.set_title('Position Player BWARP', fontsize=16)
	ax2.set_xlabel('BWARP Rank', fontsize=12)
	ax2.set_ylabel('Championships', fontsize=12)
	ax3.set_title('Pitcher PWARP', fontsize=16)
	ax3.set_xlabel('PWARP Rank', fontsize=12)
	ax3.set_ylabel('Championships', fontsize=12)
	ax.hist(df['WARP_RANK'].values, bins=np.arange(1, 30)-0.5)
	ax2.hist(df['BWARP_RANK'].values, bins=np.arange(1, 30)-0.5)
	ax3.hist(df['PWARP_RANK'].values, bins=np.arange(1, 30)-0.5)
	fig.tight_layout()
	plt.savefig('graphs/warp_ranks_hist.png')

def plot_yoy(df):
	fig = plt.figure(figsize=(40, 15))
	ax = fig.add_subplot(221)
	ax.set_xlabel('MLB fWAR Rank')
	ax.set_ylabel('Championships')
	ax.grid(color='lightgray')
	war_ranks = df['WAR_RANK']
	bwar_ranks = df['BWAR_RANK']
	pwar_ranks = df['PWAR_RANK']
	ax.plot(df['YEAR'], war_ranks, 'bo')
	ax.plot(df['YEAR'], bwar_ranks, 'go')
	ax.plot(df['YEAR'], pwar_ranks, 'ro')
	plt.savefig('graphs/fwar_ranks_line.png')

def plot_drc_vs_dra(df):
	fig = plt.figure(figsize=(8, 8))
	ax = fig.add_subplot(1, 1, 1)
	ax.invert_yaxis()
	ax.set_title(CUR_SEASON + ' DRC+ vs. DRA-')
	ax.set_xlabel('DRC+')
	ax.set_ylabel('DRA-')
	ax.plot(df['DRC+'], df['DRA-'], 'wo')
	teams = df['Master Team']
	drc = list(df['DRC+'])
	dra = list(df['DRA-'])
	fp = FontProperties(fname="fonts/bbclub.otf")
	for i, team in enumerate(teams):
		team_entry = ext.load_table('MLB_TEAM', 'teams', { 'master_abbr' : team })
		font_letter = team_entry['font_letter'][0]
		ax.annotate(font_letter, [drc[i], dra[i]], clip_on=True, fontproperties=fp, fontsize=25)
	plt.savefig('graphs/drc_vs_dra.png')

def get_correlated_stats(df):
	#print(df.columns)
	for col in df.columns:
		if col in ['Team', 'Master Team', 'FINISH', 'Year', 'W-L%']:
			continue
		x = df[[col]]
		#x = final_df[['WAR']]
		y = df['W-L%']
		lm = linear_model.LinearRegression()
		model = lm.fit(x, y)
		print(col, lm.score(x, y))

def get_correlation_over_time(source, stat, season_range):
	corrs = []
	for season in season_range:
		if source == 'fg':
			df = ext.load_table('MLB_TEAM_HISTORICAL', 'fg_dashboard_'+str(season))
		else:
			df = ext.load_table('MLB_TEAM_HISTORICAL', 'bp_team_warp_'+str(season))
		x = df[[stat]]
		y = df['W-L%']
		lm = linear_model.LinearRegression()
		model = lm.fit(x, y)
		corrs.append(lm.score(x, y))
	out_df = pd.DataFrame()
	out_df['Year'] = season_range
	out_df[stat+'Correlation'] = corrs
	return out_df

def plot_correlation_over_time(source, stat, season_range):
	df = get_correlation_over_time(source, stat, season_range)
	fig = plt.figure(figsize=(8, 8))
	ax = fig.add_subplot(1, 1, 1)
	ax.set_title(stat + ' Correlation Over Time')
	ax.set_xlabel('Season')
	ax.set_ylabel('Correlation')
	ax.plot(df['Year'], df[stat+'Correlation'])
	plt.show()