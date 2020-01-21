import numpy as np
import pandas as pd
import airyards as ay
import wopr
import sys, json, argparse

def get_fp(position):
	#Wrangle all data from pfr and airyards.com
	f_page = ay.get_pfr_fantasy()
	f_df = ay.get_table(f_page)
	f_df = f_df.replace('', 0)
	s_page = ay.get_pfr_scoring()
	s_df = ay.get_table(s_page)
	s_df = s_df.replace('', 0)
	r_page = ay.get_pfr_rushing()
	r_df = ay.get_table(r_page)
	r_df = r_df.replace('', 0)
	f_df.rename(columns={'FantPos':'Pos'}, inplace=True)

	wo_df = wopr.get_wo()
	wopr_df = wopr.get_totals()
	wopr_g_df = wopr.get_averages()
	wo_df.rename(columns={'FantPos':'Pos'}, inplace=True)
	wopr_df.rename(columns={'full_name':'Player', 'position':'Pos'}, inplace=True)
	wopr_g_df.rename(columns={'full_name':'Player', 'position':'Pos'}, inplace=True)

	#Combine data to get full fp dataset
	df2 = pd.merge(f_df,r_df[['Fmb', 'Player']],on='Player', how='left')
	df3 = pd.merge(df2,s_df[['AllTD', 'Player']],on='Player', how='left').fillna(0)
	#print(df3)

	#Calculate fantasy points
	passyds = df3['PassYds'].astype('float64')
	passtds = df3['PassTD'].astype('float64')
	ints = df3['Int'].astype('float64')
	rushyds = df3['RushYds'].astype('float64')
	receptions = df3['Rec'].astype('float64')
	recyds = df3['RecYds'].astype('float64')
	tds = df3['AllTD'].astype('float64')
	twoptmd = df3['2PM'].astype('float64')
	twoptcp = df3['2PP'].astype('float64')
	fumbles = df3['Fmb_y'].astype('float64')

	if position == 'QB':
		games = df3['GS'].astype('float64')
	else:
		games = df3['G'].astype('float64')

	fp = (passyds / 30.0) + (passtds * 4.0) - (ints * 2.0) + (rushyds / 10.0) + (receptions * 0.5) + (recyds / 10.0) + (tds * 6.0) + (twoptmd * 2.0) + (twoptcp * 2.0) - (fumbles * 2.0)

	#Combine data to get full opportunity dataset
	df4 = pd.merge(f_df,wo_df[['WO', 'WO/G', 'Player', 'Pos']],on=['Player', 'Pos'], how='left').fillna(0)
	df5 = pd.merge(df4,wopr_g_df[['wopr', 'Player', 'Pos']],on=['Player', 'Pos'], how='left').fillna(0)
	df5.rename(columns={'wopr':'WOPR/G'}, inplace=True)
	df6 = pd.merge(df5,wopr_df[['wopr', 'Player', 'Pos']],on=['Player', 'Pos'], how='left').fillna(0)

	#Combine opportunity with fantasy points and return dataset filtered on position
	df = pd.DataFrame()
	df['Player'] = df6['Player']
	df['Pos'] = df6['Pos']
	df['FP'] = fp.round(2)
	df['WO'] = df6['WO']
	df['FPG'] = (fp / games).round(2)
	df['WOG'] = df6['WO/G']
	df['WOPRG'] = df6['WOPR/G']
	df['WOPR'] = df6['wopr']

	#flex handling
	if position == 'FLEX':
		final_df = df[(df['Pos'] == 'WR') | (df['Pos'] == 'RB') | (df['Pos'] == 'TE')]
	else:
		final_df = df[(df['Pos'] == position)]

	return final_df

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("pos", help="position of player (qb, rb, wr, te, flex)")
	parser.add_argument("sort_col", help="column you want to sort by")
	args = parser.parse_args()

	if (args.sort_col == 'WO'):
		sort = 'WO'
	if (args.sort_col == 'WOG'):
		sort = 'WO/G'
	if (args.sort_col == 'FP'):
		sort = 'FP'
	if (args.sort_col == 'FPG'):
		sort = 'FP/G'
	if (args.sort_col == 'WOPR'):
		sort = 'WOPR'
	if (args.sort_col == 'WOPRG'):
		sort = 'WOPR/G'

	data = get_fp(args.pos.upper())
	print(data.sort_values(by=[sort], ascending=False).to_json(orient='records'))
	sys.stdout.flush()

if __name__ == '__main__':
	main()