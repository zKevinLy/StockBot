from pathlib import Path
import requests
import pytime
import json
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY1= os.getenv('API_KEY1')
API_KEY2= os.getenv('API_KEY2')
API_KEY3= os.getenv('API_KEY3')
API_KEY4= os.getenv('API_KEY4')
API_KEY5= os.getenv('API_KEY5')
 
class Exchanges:
  def __init__(self):
    self.supportedTickers = dict()
    self.keys = [API_KEY1, API_KEY2, API_KEY3, API_KEY4, API_KEY5]
    self.time = pytime.Time()
    self.today = self.time.getCurrentDate()
    self.lastUpdated()
    
  # updates all ticker symbols
  def updateTickers(self):
    try:
      directory = Path(__file__).absolute().parent
      for key in self.keys:
          url = "https://financialmodelingprep.com/api/v3/available-traded/list?apikey={key}".format(key = key)
          response = requests.get(url)
          data = response.json()
          if 'Error Message' in data and 'upgrade' in data['Error Message']:
            continue
          if 'Exchanges' not in os.listdir(directory):
            os.mkdir('Exchanges')
          with open('Exchanges/tradable.json', 'w') as cur:
            json.dump(data, cur)
    except:
      print("Error in updateTickers")
    
  def getSupportedTickers(self):
    try:
      directory = Path(__file__).absolute().parent
      if 'symbols.txt' not in os.listdir(directory / 'Exchanges'):
        with open('Exchanges/symbols.txt', 'w') as cur:
          pass
      with open('Exchanges/tradable.json', 'r') as r:
        with open('Exchanges/symbols.txt', 'w') as w:
          data = json.load(r)
          for p in data:
            w.write(p['symbol'] + '\n')
            if 'name' in p.keys():
              self.supportedTickers[p['symbol']] = p['name']
      return self.supportedTickers.keys()
    except:
      print("Error in getSupportedTickers")

  def getSupportedNames(self):
    return self.getSupportedTickers()

  def lastUpdated(self):
    try:
      directory = Path(__file__).absolute().parent
      if 'updated.txt' in os.listdir(directory / 'Exchanges'):
        with open('Exchanges/updated.txt', 'r') as r:
          date = r.readline().strip()
        if (abs(self.time.timeDiff(date, self.today).days)) > 31:
          with open('Exchanges/updated.txt', 'w') as cur:
            cur.write(self.today)
          self.updateTickers()
          print("Exchanges freshly updated {}".format(self.today))
        else:
          with open('Exchanges/updated.txt', 'r') as r:
            date = r.readline().strip()
          print("Exchanges recently updated {} day(s) ago".format(abs(self.time.timeDiff(date, self.today).days)))
          return
      else:
        with open('Exchanges/updated.txt', 'w') as cur:
          cur.write(self.today)
        self.updateTickers()
        return
    except:
      print("Error in lastUpdated")
      
if __name__ == '__main__':
  e = Exchanges()
  y = e.getSupportedTickers()
  x = e.getSupportedNames()
  a = e.updateTickers()
  b = e.lastUpdated()
  for i in [y,x,a,b]:
    print(i)