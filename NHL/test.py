import numpy as np
import pandas as pd
import hockeyref as hr
import sys, json, argparse
import pymongo #pymongo-3.7.2

def conn():
	return pymongo.MongoClient("mongodb+srv://admin:pdometer@mongo-uwij2.mongodb.net/test?retryWrites=true")

def main():
	client = conn()
	db = client['Corsica']
	table = db.skater_advanced
	for stat in table.find():
		print(stat['oiSV%'], stat['oiSH%'], type(stat['oiSV%']))

if __name__ == '__main__':
	main()