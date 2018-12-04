import requests
import json
import csv
import sys
import gspread
import pymongo
from oauth2client.service_account import ServiceAccountCredentials

#init mongodb
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
wardb = myclient["warDB"]
currentWar = wardb["wars"]

scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

filename = 'apikey'
f = open(filename, 'r')
apikey = f.read().strip()

url = 'https://api.clashofclans.com/v1/clans/%239RPU22RU/currentwar'
headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer '+apikey
    }
r = requests.get(url, headers=headers)
data = json.loads(r.text.encode('utf-8'))
outputFile = open("war.csv", 'wb') #load csv file
output = csv.writer(outputFile) #create a csv.write
#outputFile.write(r.text.encode('utf-8'))
#output.writerow(data[0].keys())  # header row

retExisting = currentWar.find_one_and_update(
        {"endTime":data["endTime"]},
        {'$set':data},
        {}
)

if retExisting is None:
    #insert instead of update
    currentWar.insert_one(data)
    print("Insert war endtime "+data["endTime"])
else:
    print("Update war endtime "+data["endTime"])


sheet = client.open("Frost Wars")

try:
    warWorksheet = sheet.worksheet(data["startTime"][:8].encode('utf-8'))
except:
    warWorksheet = sheet.add_worksheet(data["startTime"][:8].encode('utf-8'),1,1)

warWorksheet = sheet.worksheet(data["startTime"][:8].encode('utf-8'))
warWorksheet.clear()

#Opponent Name
output.writerow([data["opponent"]["tag"].encode('utf-8'),data["opponent"]["name"].encode('utf-8'),data["startTime"].encode('utf-8')])
output.writerow("")

warWorksheet.append_row([data["opponent"]["tag"].encode('utf-8'),data["opponent"]["name"].encode('utf-8'),data["startTime"].encode('utf-8')])
warWorksheet.append_row(["","",""])


#output.writerow(data["opponent"]["tag"])
#Date
#output.writerow(data["startTime"])

for row in data["clan"]["members"]:
    if 'attacks' not in row:
        att=0
    else:
        att = len(row["attacks"])
    output.writerow([row["tag"].encode('utf-8'),row["name"].encode('utf-8'),att])
    warWorksheet.append_row([row["tag"].encode('utf-8'),row["name"].encode('utf-8'),att])
    #output.writerow(row["name"])
    #attacks = len(row["attacks"])
    #output.writerow(attacks)
