import requests
import json
import csv
import sys
import urllib

filename = 'apikey'
f = open(filename, 'r')
apikey = f.read().strip()

url = 'https://api.clashofclans.com/v1/clans/%239RPU22RU/members'
url2 = 'https://api.clashofclans.com/v1/players/'
headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer '+apikey
    }
r = requests.get(url, headers=headers)
data = json.loads(r.text.encode('utf-8'))
outputFile = open("clan.csv", 'wb') #load csv file
output = csv.writer(outputFile) #create a csv.write
#outputFile.write(r.text.encode('utf-8'))
#output.writerow(data[0].keys())  # header row
output.writerow(["Tag","Name","Town Hall Level","Donations"])
for row in data["items"]:
    r2 = requests.get(url2 + urllib.quote(row["tag"]), headers=headers)
    data2 = json.loads(r2.text.encode('utf-8'))
    output.writerow([row["tag"],row["name"],data2["townHallLevel"],row["donations"]])
    #output.writerow(row["name"])
    #attacks = len(row["attacks"])
    #output.writerow(attacks)
