import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import fangraphs as fg
import savant as sa

def get_pitchtypes():
	page = fg.get_player_stats_page(cat='4')
	df = fg.get_table(page).replace('', 0.0)
	return df

def get_pitchvalues():
	page = fg.get_player_stats_page(ptype='bat', cat='7')
	df = fg.get_table(page).replace('', 0.0)
	return df

def get_pitch_score(batter, pitcher):
	pt_data = get_pitchtypes()
	pv_data = get_pitchvalues()
	pitcher_data = pt_data.loc[pt_data['Name'] == pitcher]
	batter_data = pv_data.loc[pv_data['Name'] == batter]
	print(pitcher_data)
	print(batter_data)
	binx = batter_data.index[0]
	pinx = pitcher_data.index[0]

	wFB = batter_data['wFB/C'].astype('float64')
	wSL = batter_data['wSL/C'].astype('float64')
	wCT = batter_data['wCT/C'].astype('float64')
	wCB = batter_data['wCB/C'].astype('float64')
	wCH = batter_data['wCH/C'].astype('float64')
	wSF = batter_data['wSF/C'].astype('float64')

	fb_percent = pitcher_data['FB%'].astype('float64')
	sl_percent = pitcher_data['SL%'].astype('float64')
	ct_percent = pitcher_data['CT%'].astype('float64')
	cb_percent = pitcher_data['CB%'].astype('float64')
	ch_percent = pitcher_data['CH%'].astype('float64')
	sf_percent = pitcher_data['SF%'].astype('float64')

	score = (wFB[binx] * fb_percent[pinx]) + (wSL[binx] * sl_percent[pinx]) + (wCT[binx] * ct_percent[pinx]) + (wCB[binx] * cb_percent[pinx]) + (wCH[binx] * ch_percent[pinx]) + (wSF[binx] * sf_percent[pinx])

	return score

print(get_pitch_score('Rhys Hoskins', 'Noah Syndergaard'))