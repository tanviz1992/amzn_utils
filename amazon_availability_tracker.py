import requests
from bs4 import BeautifulSoup
import html
import argparse
import os
from requests.exceptions import HTTPError
from twilio.rest import Client
from itertools import cycle
from lxml import html
client = Client("AS###", "secret code")

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
country_code_db={}

def SendText(asin, product_name, status, price):
    body = str(asin) + " : " + product_name + " " + status + " Price : " + str(price) + "\n"
    print(body)
    message = client.messages.create(to="+15512858554",
                           from_="+16822573668",
                           body=body)
    print(message.sid)

def checkAvailibility(asin, url):
    import random
    print("Sending to URL " + url)
    response = None
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print('Success! Checking for Site for details')
        elif response.status_code == 404:
            print('Amazon Webpage does not exist for ' + url)
            return
    except HTTPError as http_err:
        print('Amazon Webpage does not exist for ' + url)
        print(f'HTTP error occurred: {http_err}')
        return
    except Exception as err:
        print('Amazon Webpage does not exist for ' + url)
        print(f'Other error occurred: {err}')
        return
    else:
        print('Success!')

    soup = BeautifulSoup(response.content, features="lxml")
    if(len(soup.select("#productTitle"))==0):
        print("Increase time interval. Throttle limit crossed ?")
        return

    title = soup.select("#productTitle")[0].get_text().strip()
    availability_status = soup.select("#availability")[0].get_text().strip()
    price = soup.select("#priceblock_saleprice")[0].get_text()

    if "unavailable" not in availability_status.lower():
        SendText(asin, title, availability_status, price)

def PrintHelp():
    print ("Usage: python amazon_availability_tracker.py --asin ASIN_AMZN --country-db /path/db/file/country_list.csv")

def loadCountryDB(country_db_path):
    global country_code_db
    file_handle = open(country_db_path, "r")

    lines = file_handle.readlines()[1:]

    for line in lines:
        split_line = line.split(",")
        country_full = split_line[0].lower().rstrip()
        country_code = split_line[1].lower().rstrip()
        country_code_db[country_full] = country_code

def getCountryCode(country):
    global country_code_db
    if country in country_code_db:
        return country_code_db[country]
    return ""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--country', dest='country', required=False, help='<Optional> Country Page where you want to check')
    parser.add_argument('--asin', dest='asin', required=False, help='<Required> Amazon Assigned ASIN')
    parser.add_argument('--country-db', dest='country_db', required=False, help='<Optional> Required if using the --country feature')

    parser.add_argument("--print-help", dest='print_help', action='store_true')

    parsed_args = parser.parse_args();

    if parsed_args.print_help:
        PrintHelp()
        exit()

    country = parsed_args.country
    asin = parsed_args.asin
    country_db_path = parsed_args.country_db
    if asin == "":
        print("Please provide a valid ASIN")
        PrintHelp()

    if country != "" and country != None:
        if country != "USA" and country != "United States" and country != "United States of America" and country_code_db == "":
            print("Country provided other than USA, but no path to country_db specified.")
            PrintHelp()


    if country_db_path != "" and country_db_path != None:
        if (not os.path.isfile(country_db_path)):
            print("File Path to Country DB does not exist. Please provide a valid file path")
            PrintHelp()
        loadCountryDB(country_db_path)

    country_code ="com"
    if country != "" and country != None:
        if country != "USA" and country != "United States" and country != "United States of America":
            country_code="com"
        else:
            country_code = getCountryCode(country.lower())

        if (country_code == ""):
            print("Could not determine country code for " +  country)
            print("Valid Countries are " + country_code_db)
            PrintHelp()

    construct_url="https://www.amazon." + country_code + "/dp/" + asin
    checkAvailibility(asin, construct_url)
