import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import sys
import json

def get_page(pid):
	url = "https://www.fangraphs.com/statsd.aspx?playerid={}&position=P&gds=&gde=&type=6".format(pid)
	r = requests.get(url)
	return BeautifulSoup(r.content, "html.parser")

def get_table(page):
	table = page.find('table',{'class':'rgMasterTable'})
	ths = table.find_all('th')
	headings = []
	for th in ths:
		headings.append(th.text.strip())
	tbody = table.find('tbody')
	#rows = tbody.find_all('tr')
	rows = tbody.find_all('tr', {'class': ['rgRow', 'rgAltRow']})
	data = []
	for row in rows[1:]:
		cells = row.find_all('td')
		cells = [cell.text.replace('%', '').strip() for cell in cells]
		data.append([cell for cell in cells])

	df = pd.DataFrame(data=data, columns=headings)
	df = df.replace('', '0')
	return df

def get_fb(data):
	fb = data['FB%'].astype('float64')
	return fb

def get_bb(data):
	sl = data['SL%'].astype('float64')
	ct = data['CT%'].astype('float64')
	cb = data['CB%'].astype('float64')
	ch = data['CH%'].astype('float64')
	sf = data['SF%'].astype('float64')
	kn = data['KN%'].astype('float64')
	bb = sl + ct + cb + ch + sf + kn
	return bb

def get_fb_bb_split(data):
	df = pd.DataFrame(columns=['Date', 'Fastball %', 'Breaking Ball %'])
	df['Date'] = data['Date']
	df['Fastball %'] = json.loads(get_fb(data).to_json(orient='records'))
	df['Breaking Ball %'] = json.loads(get_bb(data).to_json(orient='records'))
	return df

def main(argv):
	page = get_page(int(argv[1]))
	df = get_table(page)
	df2 = get_fb_bb_split(df)
	#json = df.to_json(orient='records')[1:-1]
	print(df2.to_json(orient='records'))
	sys.stdout.flush()

if __name__ == "__main__":
	main(sys.argv)