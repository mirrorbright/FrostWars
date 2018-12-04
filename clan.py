import requests
import json
import csv
import sys
import urllib
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)


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

sheet = client.open("Frost Wars")

clanSheet = sheet.worksheet("Clan Roster")

#Clear names
cell_list = clanSheet.range('A2:D51')

for cell in cell_list:
    cell.value = ''
#clanSheet.update_cells(cell_list)

#outputFile.write(r.text.encode('utf-8'))
#output.writerow(data[0].keys())  # header row
output.writerow(["Tag","Name","Town Hall Level","Donations"])
index=0
for row in data["items"]:
    r2 = requests.get(url2 + urllib.quote(row["tag"]), headers=headers)
    data2 = json.loads(r2.text.encode('utf-8'))
    output.writerow([row["tag"],row["name"].encode('utf-8'),data2["townHallLevel"],row["donations"]])

    
    cell_list[index].value=row["tag"]
    cell_list[index+1].value=row["name"]
    cell_list[index+2].value=data2["townHallLevel"]
    cell_list[index+3].value=row["donations"]

    index=index+4

clanSheet.update_cells(cell_list)
