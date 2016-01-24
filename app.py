from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
import io
import json
def yelpsearchapi_by_location(loc):
	DEFAULT_LOCATION = loc
	CREDENTIALS_PATH = 'static/credentials.json'
	RADIUS_FILTER_METERS = 1000
	NEAREST_SORT_OPTION = 1
	LIMIT = 5

	# read api keys credentials
	with io.open(CREDENTIALS_PATH) as cred:
		creds = json.load(cred)
		auth = Oauth1Authenticator(**creds)
		client = Client(auth)
    # enter parameters
    	params = { 'category_filter': 'bars',
    			   'radius_filter': RADIUS_FILTER_METERS,
    			   'sort': NEAREST_SORT_OPTION,
    			   'limit': LIMIT }

	if loc:
		response = client.search(loc, **params)
	else:
		response = client.search(DEFAULT_LOCATION, **params)

	return response

from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

@app.route("/")
def index():
	# return "hello, world"
	return render_template('index.html')

@app.route('/home')
def home():
	return ""

@app.route('/result', methods=['POST'])
def result():
	if request.method == 'POST':
		if 'bars' in request.form:
			selector = 'bars'
		elif 'food' in request.form:
			selector = 'food'
		else:
			selector = 'hospital'

		loc = selector + ' near ' + request.form['location']
		rat = request.form['minrating']
		res = yelpsearchapi_by_location(loc)

		if len(res.businesses) == 0:
			loc = 'bars'
			rat = request.form['minrating']
			res = yelpsearchapi_by_location(loc)

		def filter_min_rating():
			def f(yelpbusinessobject):
				return yelpbusinessobject.rating >= float(rat)
			return filter(f, res.businesses)

		business_filtered_by_min_rating = filter_min_rating()

		import numpy
		nbusiness_results = len(business_filtered_by_min_rating)
		min_index = min([5, nbusiness_results])

		random_index = numpy.random.randint(min_index)
		random_business_among_five = business_filtered_by_min_rating[random_index]
		name = random_business_among_five.name
		address = '\n'.join(random_business_among_five.location.display_address)
		phone = random_business_among_five.display_phone
		image = random_business_among_five.image_url
		rating = random_business_among_five.rating

		if res:
			return render_template('result.html', name=name,
				address=address, phone=phone, image=image, rating=rating)
		else:
			return "Go Home! Have a good nap."


if __name__ == "__main__":
	app.run()