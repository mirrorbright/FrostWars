import requests
import datetime
import json
import csv
import sys
import urllib
import gspread
import pymongo
from oauth2client.service_account import ServiceAccountCredentials

#This script will get current clan members from API, then insert them into our database

#init mongodb
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["frost"]
myClan = mydb["clan"]
clanTemp=mydb["clanTemp"]

#Gdrive API
"""
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
"""
#COC API
filename = 'apikey'
f = open(filename, 'r')
apikey = f.read().strip()

#Grab latest list of current clan members
url = 'https://api.clashofclans.com/v1/clans/%239RPU22RU/members'
url2 = 'https://api.clashofclans.com/v1/players/'
headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer '+apikey
    }
r = requests.get(url, headers=headers)
data = json.loads(r.text.encode('utf-8'))


# logic: 
# Get list of current members from COC API
# Save list to temp. 
# iterate through list. If not there, add and include added date
# if already exists, update donations and th info


clanTemp.insert_many(data["items"])
allTags = []

for row in data["items"]:

    r2 = requests.get(url2 + urllib.quote(row["tag"]), headers=headers)
    data2 = json.loads(r2.text.encode('utf-8'))

    clanMember = json.loads("{}")
    clanMember["tag"]=row["tag"]
    clanMember["name"]=row["name"]
    clanMember["donationsReceived"]=row["donationsReceived"]
    clanMember["donations"]=row["donations"]
    clanMember["townHallLevel"]=data2["townHallLevel"]
    clanMember["active"]=True

    #allTags.append(clanMember["tag"])

    retExisting = myClan.find_one_and_update(
            {"tag":clanMember["tag"]},
            {'$set':clanMember},
            {}
    )
    
    if retExisting is None:
        #insert instead of update
        clanMember["joinedDate"]=datetime.datetime.now().strftime("%Y-%m-%d")
        myClan.insert_one(clanMember)
        print("Insert "+clanMember["name"])
    else:
        print("Update "+clanMember["name"])


# Now use all tags from the API call (saved in a query), query clanMember collection, returning anything that is set to active not in the API call.
# Those that remain are no longer active. Set them to removed, and set removedDate.

allTags=["#29Y902UV8"]

listOfRemovedMembers = myClan.find({"active":True, "tag":{'$in':allTags}})

for inactive in listOfRemovedMembers:
    inactive["active"]=False
    inactive["inactiveDate"]=datetime.datetime.now().strftime("%Y-%m-%d")

    myClan.find_one_and_update(
            {"tag":inactive["tag"]},
            {'$set':inactive},
            {}
    )

    print("Removed "+inactive["name"])

clanTemp.drop()
