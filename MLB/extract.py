import pandas as pd
import pymongo

def conn():
	return pymongo.MongoClient("mongodb+srv://admin:pdometer@mongo-uwij2.mongodb.net/test?retryWrites=true")

def load_table(db_name, table_name, query={}):
	client = conn()
	db = client[db_name]
	table = db[table_name]
	cursor = table.find(query)
	df = pd.DataFrame(list(cursor))
	if '_id' in df:
		del df['_id']
	return df