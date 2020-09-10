from amadeus import Client, ResponseError
import pymongo
import requests
import json



client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0-wmcx9.mongodb.net/romayo_internal?retryWrites=true&w=majority")
db = client.roamyo_analysis
cols = db.list_collection_names()

#airports_collection = db.airports.find({})


amadeus = Client(
    client_id='',
    client_secret=''
)



def get_flight_offers(origin, destination, departureDate='2020-09-10', adults=1, oneWay=True):

    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode = origin,
            destinationLocationCode = destination,
            departureDate = departureDate,
             adults=1)
        return response.data

    except ResponseError as error:
        print(error)


#sample_offers = get_flight_offers('TRV', 'CMB')


def find_cheapest_offer(offers):
    min_price = 9999999999
    current_offer = None
    for offer in offers:
        if float(offer['price']['total']) < min_price:
            min_price = float(offer['price']['total'])
            current_offer = offer
        
    
    return min_price, current_offer




def collect_offers_for_country(country_name):
    indian_airports = []
    destination_airports = []
    for airports_list in airports_collection:
        if airports_list['countryName'] == 'India':
            indian_airports += airports_list['airports']

        if airports_list['countryName'] == country_name:
            destination_airports += airports_list['airports']
        
    
    for source in indian_airports:
        for destination in destination_airports:
            flight_offers = get_flight_offers(source['iataCode'].upper(), destination['iataCode'].upper())
            min_price, cheapest_offer = find_cheapest_offer(flight_offers)
            if min_price < 9999999998:
                db.amadeus_offers.insert({'_id':  source['iataCode'] + ' to ' + destination['iataCode'], 'source': source['iataCode'].upper(), 'destination': destination['iataCode'].upper(), 'price': cheapest_offer['price']['currency']+ str(min_price), 'offer': cheapest_offer})



#collect_offers_for_country('Australia')

# Australia   


airports_to_monitor = ['CMB', 'GRU', 'CPH', 'SVO', 'SIN', 'KUL', 'RAK']
dates_to_monitor = [ '2020-09-10' ]


flight_offers = get_flight_offers('DEL', 'SYD')

for e in flight_offers:
    #print(e)
    if 'PT14H' in e['itineraries'][0]['duration']:
        print(e)
    

print('here goes the cheapest offer')
print(find_cheapest_offer(flight_offers))





# source_airport = 'DEL'
# for destination_airport in airports_to_monitor:
#     for date in dates_to_monitor:
#         flight_offers = get_flight_offers(source_airport, destination_airport, date)
#         min_price, cheapest_offer = find_cheapest_offer(flight_offers)
    
#         if min_price < 9999999998:
#             #db.amadeus_price_analysis.insert({'_id': source_airport+' to '+destination_airport+' on '+date, 'source': source_airport, 'destination': destination_airport, 'price': cheapest_offer['price']['currency']+ str(min_price),'date': date , 'offer': cheapest_offer  })
#             pass
