import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests

def get_dk_live():
	url = '''https://sportsbook.draftkings.com/api/odds/v1/leagues/103/offers/gamelines.json'''
	resp = requests.get(url)
	data = resp.json()
	events = data["events"]
	#df = pd.DataFrame(columns=['Date', 'Game', 'Away Team', 'Away Spread', 'Away Spread Odds', 'Away ML', 'Home Spread', 'Home Spread Odds', 'Home ML', 'Total', 'Over Odds', 'Under Odds'])
	events_list = []
	for event_index, event in enumerate(events[:-1]):
		event_id = event['id']
		event_name = event['name']
		event_date = event['startDate']
		away_team = event['awayTeamName']
		home_team = event['homeTeamName']
		point_spreads = []
		alt_spreads = []
		moneylines = []
		totals = []
		alt_totals = []
		offers = event['offers']
		for offer in offers:
			if offer['label'] == 'Point Spread':
				alt_spreads.append(offer['outcomes'])
			if offer['label'] == 'Money Line':
				moneylines.append(offer['outcomes'][0]['oddsAmerican'])
				moneylines.append(offer['outcomes'][1]['oddsAmerican'])
			if offer['label'] == 'Total Points':
				alt_totals.append(offer['outcomes'])
		bestSpreadDiff = 1000
		bestSpreadIndex = 0
		for i, spread in enumerate(alt_spreads):
			away_odds = spread[0]['oddsDecimal']
			diff = abs(float(away_odds) - 1.91)
			if diff < bestSpreadDiff:
				bestSpreadDiff = diff
				bestSpreadIndex = i

		bestTotalDiff = 1000
		bestTotalIndex = 0
		for i, total in enumerate(alt_totals):
			away_odds = total[0]['oddsDecimal']
			diff = abs(float(away_odds) - 1.91)
			if diff < bestTotalDiff:
				bestTotalDiff = diff
				bestTotalIndex = i

		away_spread_info = alt_spreads[bestSpreadIndex][0]
		home_spread_info = alt_spreads[bestSpreadIndex][1]
		away_ml = moneylines[0]
		home_ml = moneylines[1]
		over_info = alt_totals[bestTotalIndex][0]
		under_info = alt_totals[bestTotalIndex][1]

		game_total = alt_totals[bestTotalIndex][0]['line']
		over_odds = over_info['oddsAmerican']
		under_odds = under_info['oddsAmerican']
		away_spread = away_spread_info['line']
		away_spread_odds = away_spread_info['oddsAmerican']
		home_spread = home_spread_info['line']
		home_spread_odds = home_spread_info['oddsAmerican']

		events_list.append({'DK_ID': event_id, 'DATE': event_date, 'GAME': event_name, 'AWAY TEAM': away_team, 'AWAY SPREAD': away_spread, 'AWAY SPREAD ODDS': away_spread_odds, 'AWAY ML': away_ml, 'HOME TEAM': home_team, 'HOME SPREAD': home_spread, 'HOME SPREAD ODDS': home_spread_odds, 'HOME ML': home_ml, 'TOTAL': game_total, 'OVER ODDS': over_odds, 'UNDER ODDS': under_odds})

		#print(away_team, away_spread, away_spread_odds, away_ml, game_total, over_odds)
		#print(home_team, home_spread, home_spread_odds, home_ml, game_total, under_odds)
	df = pd.DataFrame(events_list)
	return df

#get_dk_live()