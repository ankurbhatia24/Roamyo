from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from datetime import timedelta, date
import requests
from amadeus import Client, ResponseError
import json

# time_durations less thans
twelve_hours = timedelta(hours = 12)

app = Flask(__name__)
api = Api(app)

# todos = {}

amadeus = Client(
    client_id='',
    client_secret=''
)


def totalCost(place,
              dateDeparture,
              dateReturn,
              noOfAdults = 1,
              noOfChild = 0):

              #Check the types of inputs
              # Date - <yyyy-mm-dd>
              # Place - string
              # noOfAdults - int
              # noOfChild - int

              # Tell manish bhai that date should be in this format and the date should be of proper time ahead from todays date.
              # It should be checked already by manish that the differnce in dates is atleast one day or more.
                print("In totalCost")
                print(place)

                # YOUR_ACCESS_KEY = 'GET YOUR ACCESS KEY FROM fixer.io' 
                # url = str.__add__('http://data.fixer.io/api/latest?access_key=', "") 
                # c = Currency_convertor(url) 
                # from_country = "USD"
                # to_country = "INR"

                #Calculate number of nights
                no_of_nights = date.fromisoformat(dateReturn) - date.fromisoformat(dateDeparture)
                no_of_nights = no_of_nights.days
                print(no_of_nights)
              

                with open('destinations_names_to_code.json') as f:
                    destination = json.load(f)
                
                destId = destination[place]
                products = top_20_products(destId)
                print('Got the 20 products')
                if(products["success"] == True):
                    per_person_average_price = 0
                    duration = format_duration("0 hour")
                    count = 0
                    for product in products["data"]:
                        du = format_duration(product["duration"])
                        if(du <= twelve_hours):
                            count = count + 1
                            per_person_average_price = product["price"] + per_person_average_price
                            duration = du  + duration 
                        print("Got i product")
                    try:
                        duration = duration/count
                    except:
                        #count if experinces below 12 hours is zero
                        #Here taking into considerations of all experience
                        
                        for product in products["data"]:
                            du = format_duration(product["duration"])
                            count = count + 1
                            per_person_average_price = product["price"] + per_person_average_price
                            duration = du  + duration
                        try:
                            duration = duration/count
                        except:
                            duration = 0
                    if(duration):
                        per_person_average_price = per_person_average_price/count
                    else: 
                        per_person_average_price = 0
                
                per_person_average_price = per_person_average_price*74.75 #USD to INR
                #starting hotel price
                # shp = StartingHotelPrice(place) #1 room, 1 night
                shp = 0
                no_of_rooms = int(noOfAdults/2.0)
                # shp = shp*(toINRvalue)
                #average flight price
                origin = 'DEL'
                final_destination = 'CMB'
                afp = cheepest_offer(origin, final_destination, dateDeparture, adults=1, oneWay=False)
                afp = float(afp[0]["price"]["total"]) # 0 is for cheepest offer
                afp = afp*85.44 #euro to inr
                # afp = AverageFlightPrice(place, dateDeparture, dateReturn)

                multiplicative_factor = 1
                totalPrice = 0
                totalPrice = (per_person_average_price*noOfAdults*no_of_nights*multiplicative_factor) + \
                             (shp*no_of_nights*no_of_rooms) + \
                             (afp*noOfAdults*2)
                # totalPrice = c.convert(from_country, to_country, totalPrice)
                return ({
                    "per_person_average_price" : per_person_average_price*74.5,
                    "totalPrice": totalPrice,
                    "no_of_rooms" : no_of_rooms,
                    "no_of_nights" : no_of_nights,
                    "noOfAdults" : noOfAdults,
                    "cheepest_Flight_Price" : afp
                })
                    
                


def format_duration(duration):
    try:
        #type of '6 hours', '1 hour', '6 hours 30 minutes', '1 hour 30 minutes'
        hours = int(duration.split(' hour')[0])
        return(timedelta(hours = hours))        
    except:
        try:
            #type of '4 to 5 hours'
            hours_1 = int(duration.split(' hours')[0].split(' to ')[0])
            hours_2 = int(duration.split(' hours')[0].split(' to ')[1]) 
            return(timedelta(hours = hours_2))
        except:
            try:
                #type '3 days'
                days = int(duration.split(' day')[0])
                return(timedelta(days = days))
            except:
                try:
                    #type '2 to 3 days'
                    days_1 = int(duration.split(' days')[0].split(' to ')[0])
                    days_2 = int(duration.split(' days')[0].split(' to ')[1]) 
                    return(timedelta(days = days_2))  
                except:
                    try:
                        #type of '5 minutes'
                        minutes = int(duration.split(' minute')[0])
                        return(timedelta(minutes = minutes)) 
                    except:
                        try:
                            #type of '4 to 5 minutes'
                            minutes_1 = int(duration.split(' minutes')[0].split(' to ')[0])
                            minutes_2 = int(duration.split(' minutes')[0].split(' to ')[1])
                            return(timedelta(minutes = minutes_2))
                        except:
                            print("FUCKED")
                            print(duration)
                    
def check_duration_type(time_obj, dur_type):
    switcher = {'one_hour' : 1 if(time_obj <= one_hour) else 0,  #ternary,
                'four_hour' : 1 if(time_obj <= four_hour) else 0,
                'one_day' :1 if(time_obj <= one_day) else 0, 
                'three_days': 1 if(time_obj <= three_days) else 0,
                'three_day_plus':1 if(time_obj > three_days) else 0}
#     print(f"######### DURATION TYPE: {dur_type}#########      #####   dur_type: {switcher.get(dur_type)}    ####")    
    return(switcher.get(dur_type))
 


def cheepest_offer(origin, destination, departureDate, adults=1, oneWay=False):

    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode = origin,
            destinationLocationCode = destination,
            departureDate = departureDate,
             adults=1)
        return response.data

    except ResponseError as error:
        print(error)

#API from https://fixer.io/quickstart
class Currency_convertor: 
	# empty dict to store the conversion rates 
	rates = {} 
	def __init__(self, url): 
		data = requests.get(url).json() 

		# Extracting only the rates from the json data 
		self.rates = data["rates"] 

	# function to do a simple cross multiplication between 
	# the amount and the conversion rates 
	def convert(self, from_currency, to_currency, amount): 
		initial_amount = amount 
		if from_currency != 'EUR' : 
			amount = amount / self.rates[from_currency] 

		# limiting the precision to 2 decimal places 
		amount = round(amount * self.rates[to_currency], 2) 
# 		print('{} {} = {} {}'.format(initial_amount, from_currency, amount, to_currency))
		return amount


def top_20_products(destId 
                        ):

                print("In top 20 products")

                url = "https://viatorapi.sandbox.viator.com/service/search/products"

                payload = {"destId": destId,
                        "sortOrder": "REVIEW_AVG_RATING_D",
                        "topX": '1-20'}
                #payload = {"destId": destId}
                #payload = {"destId": destId
                #           "startDate": "2020-02-21",
                #           "endDate": "2020-03-21"}
                headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Accept-Language': 'en-US',
                'exp-api-key': '',  #Hide api key in production code
                'Content-Type': 'application/json'
                }
                response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
                products = response.json() 
                return products



class TotalTripCost(Resource):
    # def get(self, todo_id):
    #     return {todo_id: todos[todo_id]}

    def put(self):
        place = request.form['place']
        dateDeparture = request.form['dateDeparture']
        dateReturn = request.form['dateReturn']
        noOfAdults = int(request.form['noOfAdults'])
        noOfChild = int(request.form['noOfChild']) 
        # Check for the formats of date, etc. Are they received correct
        # Check if assert can be used here
        print("Okayyy Getting Ready")
        return jsonify(totalCost(place,
                                dateDeparture,
                                dateReturn,
                                noOfAdults,
                                noOfChild))

class HelloWorld(Resource):
    def get(self):
        return "Hello World!"

api.add_resource(TotalTripCost, '/TotalTripCost')
api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(debug=True, port=80)
