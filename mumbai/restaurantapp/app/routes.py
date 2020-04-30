import sys
from importlib import reload
reload(sys)
#sys.setdefaultencoding("utf-8")


import csv

import pandas as pd
from flask import Flask, render_template,request,redirect,url_for
#from gevent.pywsgi import WSGIServer
from pymongo import MongoClient




from app import app

title = "TODO sample application with Flask and MongoDB"
heading = "FEEDBCK PAGE"

client1 = MongoClient("mongodb://127.0.0.1:27017/mumbairestaurants1")
db1 = client1['mumbairestaurants1']
client = MongoClient("mongodb://127.0.0.1:27017") #host uri
db = client.mymongodb    #Select the database
todos = db.todo

restaurant_review_collection = []
with open('app/feature_review_summary.csv', 'r', encoding="utf8") as csvFile:
	reader = csv.reader(csvFile)
	for row in reader:
		restaurant_review_collection.append(row)
csvFile.close()

col_names = restaurant_review_collection.pop(0)
rest_df = pd.DataFrame(restaurant_review_collection, columns=col_names, index=None)
rest_df["sentiment"].replace({"1": "POSITIVE REVIEWS", "-1": "NEGATIVE REVIEWS"}, inplace=True)



def get_restaurants(city_rest, locality):
	rest_in_city = []
	for rc in city_rest:
		if (rc['rest_locality'] == locality):
			rest_in_city.append(rc['rest_name'])
	return rest_in_city

@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/search', methods = ['POST', 'GET'])
def search():
	if request.method == 'POST':
		locality = request.form['c']
		# get restaurant and city info from database
		city_rest = db1.mumbairestaurants1.find({}, {"rest_name":1, "rest_locality":1, "_id":0})

		# get restaurnats by city
		if (locality == "Bandra"):
			rest_in_city = get_restaurants(city_rest, locality)
			return render_template('search.html', restaurants=rest_in_city, locality=locality)

		elif (locality == "Cumballa Hill"):
			rest_in_city = get_restaurants(city_rest, locality)
			return render_template('search.html', restaurants=rest_in_city, locality=locality)

		elif (locality == "Eksar"):
			rest_in_city = get_restaurants(city_rest, locality)
			return render_template('search.html', restaurants=rest_in_city, locality=locality)

		elif (locality == "Fort"):
			rest_in_city = get_restaurants(city_rest, locality)
			return render_template('search.html', restaurants=rest_in_city, locality=locality)

		else:
			pass

	return render_template('search.html', restaurants=None)

@app.route('/result', methods = ['POST', 'GET'])
def result():
	if request.method == 'POST':
		result = request.form
		rest = result['restaurant']
		restaurant = db1.mumbairestaurants1.find({}, {"rest_name":1, "_id":0})
		for r in restaurant:
			if (r['rest_name'].lower() == rest.lower()):
				# extract feature-review data from csv converted pandas df
				feature_review = dict() # store feature-review
				sentiment_review = dict()


				if (rest_df['restaurant name'].isin([rest.lower()]).any()):
					# get features
					features = rest_df.loc[rest_df['restaurant name'] == rest.lower(), 'feature'].tolist()
					# get reviews
					reviews = rest_df.loc[rest_df['restaurant name'] == rest.lower(), 'review'].tolist()
					# create a dictionary for feature-review
					sentiments = rest_df.loc[rest_df['restaurant name'] == rest.lower(), 'sentiment'].tolist()
					for i in range(len(features)):
						if features[i] in feature_review:
							feature_review[features[i]].append(reviews[i])

						else:
							feature_review[features[i]] = [reviews[i]]
					length = [len(x) for x in feature_review.values()]

					for i in range(len(sentiments)):
						if sentiments[i] in sentiment_review:
							sentiment_review[sentiments[i]].append(reviews[i])

						else:
							sentiment_review[sentiments[i]] = [reviews[i]]



					length1 = [len(y) for y in sentiment_review.values()]




				# parse restaurant and feature-review data to render template
				if (db1.mumbairestaurants1.find( {'rest_name' : r['rest_name'] } )):
					restaurant_info = db1.mumbairestaurants1.find( {'rest_name' : r['rest_name'] })
					return render_template("result.html", rest_info=restaurant_info[0], feature_review=feature_review, sentiment_review= sentiment_review, length=length, length1=length1)
		return render_template("noresult.html")


@app.route('/stats')
def stats():
	return render_template('stats.html')



def redirect_url():
    return request.args.get('next') or \
           request.referrer or \
           url_for('index')

@app.route('/index')


@app.route("/list")
def lists ():
	#Display the all Tasks
	todos_l = todos.find()
	a1="active"
	return render_template('index.html',a1=a1,todos=todos_l,t=title,h=heading)

@app.route("/")

@app.route("/action", methods=['POST'])
def action ():
	#Adding a Task
	name=request.values.get("name")
	desc=request.values.get("desc")
	date=request.values.get("date")
	pr=request.values.get("pr")
	todos.insert({ "name":name, "desc":desc, "date":date, "pr":pr, "done":"no"})
	return redirect("/list")
