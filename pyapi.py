from pathlib import Path
from os import path
import requests
import os.path
import pytime
import math
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY1= os.getenv('API_KEY1')
API_KEY2= os.getenv('API_KEY2')
API_KEY3= os.getenv('API_KEY3')
API_KEY4= os.getenv('API_KEY4')
API_KEY5= os.getenv('API_KEY5')


class API:
    def __init__(self):
        self.keys = [API_KEY1, API_KEY2, API_KEY3, API_KEY4, API_KEY5]
        self.Time = pytime.Time()
        self.today = self.Time.getCurrentDate()
        
    # checks if file <fname> exists in a given directory <dname>
    def fileExists(self,dname,fname):
        try:
            directory = Path(__file__).absolute().parent / '{}'.format(dname)
            if directory/'{}'.format(fname) not in os.listdir(directory):
                return False
            return True
        except:
            print("Error in {}".format("fileExists"))

    # stores historical information of ticker
    def storeHistoricalInfo(self,ticker):
        try:
            historical = dict()
            for key in self.keys:
                url = "https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={key}".format(ticker = ticker, key = key)
                response = requests.get(url)
                data = response.json()
                if 'Error Message' in data.keys() and 'upgrade' in data['Error Message']:
                    continue

                url2 = "https://financialmodelingprep.com/api/v3/historical-chart/4hour/{ticker}?apikey={key}".format(ticker = ticker, key = key)
                response2 = requests.get(url2)
                data2 = response2.json()
                if 'Error Message' in data2 and 'upgrade' in data2['Error Message']:
                    continue

                for count,d in enumerate(data['historical']):
                    if count == 0:
                        prev = d
                    historical[d['date'] + ' 00:00:00'] = {
                                            "open": d['open'],
                                            "high": d['high'],
                                            "low": d['low'],
                                            "close":d['close'],
                                            "volume": d['volume'],
                                            "volumeChange": (float(prev['volume']) - float(d['volume']))/prev['volume'], 
                                            "change": d['change'],
                                            "changePercent": d['changePercent'],
                                            "vwap": d['vwap'],
                                            "date": d['date'] + ' 00:00:00'}
                    prev = d

                for count,d in enumerate(data2):
                    if count == 0:
                        prev = d
                    historical[d['date']] = {
                                            "open": d['open'],
                                            "high": d['high'],
                                            "low": d['low'],
                                            "close":d['close'],
                                            "volume": d['volume'],
                                            "volumeChange": (float(prev['volume']) - float(d['volume']))/prev['volume'],
                                            "change": float(prev['close']) - float(d['close']),
                                            "changePercent": (float(prev['close']) - float(d['close']))/prev['close'],
                                            "vwap": (float(d['close'])*float(d['volume']))/float(d['volume'])}
                    prev = d

                with open("Tickers/" + ticker + '.json', 'w') as cur:
                    print(json.dumps(historical, indent=4, sort_keys=True), file = cur)

                empty = False
                if not self.fileExists("Tickers","lastUpdated.json"):
                    with open("Tickers/lastUpdated.json",'w') as cur:
                        pass

                with open("Tickers/lastUpdated.json",'rb') as cur:
                    if len(cur.read()) == 0:
                        empty = True

                if empty:
                    with open("Tickers/lastUpdated.json",'r+') as cur:
                        ticks = dict()
                        ticks[ticker] = self.Time.getCurrentDate()
                        json.dump(ticks, cur)
                else:
                    with open("Tickers/lastUpdated.json",'r') as cur:
                        ticks = json.load(cur)
                        ticks[ticker] = self.Time.getCurrentDate()
                    os.remove("Tickers/lastUpdated.json")
                    with open("Tickers/lastUpdated.json",'w') as cur:
                        json.dump(ticks, cur)
                break
        except:
            print("Error in {}".format("storeHistoricalInfo"))

    # stores historical info of ticker
    def getHistoricalInfo(self,ticker):
        try:
            if not self.fileExists('Tickers', '{}.json'.format(ticker)):
                self.storeHistoricalInfo(ticker)
            
            with open("Tickers/" + ticker + '.json', 'r') as cur:
                return json.load(cur)
        except:
            print("Error in {}".format("getHistoricalInfo"))
    
    # returns historical price for use
    def getHistorical(self, ticker, ztype, day = pytime.Time().getCurrentDate()):
        try:
            dates = self.getHistoricalInfo(ticker)
            t = dict()
            for date in dates:
                t[date] = abs(self.Time.timeDiff(date, day))
                if date.split(" ")[0] == day.split(" ")[0]:
                    if ztype in dates[date].keys():
                        return (dates[date][ztype], date.split(" ")[0])
                    return 'Type Unavailable'
            closest = min(t, key=t.get)
            return (dates[closest][ztype], closest)
        except:
            print("Error in {}".format("getHistorical"))

    # gets real time price
    def getRealtime(self, ticker):
        try:
            for key in self.keys:
                url = "https://financialmodelingprep.com/api/v3/quote-short/{ticker}?apikey={key}".format(ticker = ticker, key = key)
                response = requests.get(url)
                data = response.json()            
                if 'Error Message' in data and 'upgrade' in data['Error Message']:
                    continue
                data[0]['date'] = self.Time.getCurrentDate()
                
                return data[0]
        except:
            print("Error in {}".format("getRealtime"))

    # gets company description
    def getProfile(self, ticker):
        try:
            for key in self.keys:
                url = "https://financialmodelingprep.com//api/v3/profile/{ticker}?apikey={key}".format(ticker = ticker, key = key)
                response = requests.get(url)
                data = response.json()
                if 'Error Message' in data and 'upgrade' in data['Error Message']:
                    continue
                return data[0]
        except:
            print("Error in {}".format("getProfile"))

    # gets top stocks of the day
    def mostGainer(self):
        try:
            for key in self.keys:
                url = "https://financialmodelingprep.com/api/v3/gainers?apikey={key}".format(key = key)
                response = requests.get(url)
                data = response.json()
                if 'Error Message' in data and 'upgrade' in data['Error Message']:
                    continue
                print(data[0])
                return data
        except:
            print("Error in {}".format("mostGainer"))

    # gets most active stocks of the day (volume to % change)
    def mostActive(self):
        try:
            for key in self.keys:
                url = "https://financialmodelingprep.com/api/v3/actives?apikey={key}".format(key = key)
                response = requests.get(url)
                data = response.json()
                if 'Error Message' in data and 'upgrade' in data['Error Message']:
                    continue
                return data
        except:
            print("Error in {}".format("mostActive"))

    # gets most downed stocks
    def mostLoser(self):
        try:
            for key in self.keys:
                url = "https://financialmodelingprep.com/api/v3/losers?apikey={key}".format(key = key)
                response = requests.get(url)
                data = response.json()
                if 'Error Message' in data and 'upgrade' in data['Error Message']:
                    continue
                return data
        except:
            print("Error in {}".format("mostLoser"))

    # gets sector info % change for the day 
    def getSector(self):
        try:
            for key in self.keys:
                url = "https://financialmodelingprep.com/api/v3/sectors-performance?apikey={key}".format(key = key)
                response = requests.get(url)
                data = response.json()
                if 'Error Message' in data and 'upgrade' in data['Error Message']:
                    continue
                return data
        except:
            print("Error in {}".format("getSector"))

    # gets market hours
    def getMarketHours(self):
        try:
            for key in self.keys:
                url = "https://financialmodelingprep.com/api/v3/market-hours?apikey={key}".format(key = key)
                response = requests.get(url)
                data = response.json()
                if 'Error Message' in data and 'upgrade' in data['Error Message']:
                    continue
                return data[0]
        except:
            print("Error in {}".format("getMarketHours"))

    # gets relevant news for a stock
    def getNews(self,tickers):
        try:
            for key in self.keys:
                url = "https://financialmodelingprep.com/api/v3/stock_news?tickers={ticker}&limit={limit}&apikey={key}".format(ticker = str(tickers), limit = 50,key = key)
                response = requests.get(url)
                data = response.json()
                if 'Error Message' in data and 'upgrade' in data['Error Message']:
                    continue
                return data
        except:
            print("Error in {}".format("getNews"))

    # gets stock rating by analysts
    def getRating(self, ticker):
        try:
            for key in self.keys:
                url = "https://financialmodelingprep.com/api/v3/rating/{ticker}?apikey={key}".format(ticker = ticker,key = key)
                response = requests.get(url)
                data = response.json()
                if 'Error Message' in data and 'upgrade' in data['Error Message']:
                    continue
                return data
        except:
            print("Error in {}".format("getRating"))

    # screens for stocks given parameters
    def getScreener(self, parameters):
        try:
            for key in self.keys:
                url = "https://financialmodelingprep.com/api/v3/stock-screener?apikey={key}".format(key = key)
                response = requests.get(url)
                data = response.json()

                for k,v in parameters.items():
                    if k == 'marketCapMoreThan':
                        data = [i for i in data if float(i['marketCap']) > float(v)]
                    elif k == 'marketCapLessThan':
                        data = [i for i in data if float(i['marketCap']) < float(v)]
                    elif k == 'betaMoreThan':
                        data = [i for i in data if float(i['beta']) > float(v)]
                    elif k == 'betaLessThan':
                        data = [i for i in data if float(i['beta']) < float(v)]
                    elif k == 'volumeMoreThan':
                        data = [i for i in data if float(i['volume']) > float(v)]
                    elif k == 'volumeLessThan':
                        data = [i for i in data if float(i['volume']) < float(v)]
                    elif k == 'dividendMoreThan':
                        data = [i for i in data if float(i['lastAnnualDividend']) > float(v)]
                    elif k == 'dividendLessThan':
                        data = [i for i in data if float(i['lastAnnualDividend']) < float(v)]
                    elif k == 'price':
                        data = [i for i in data if float(i['price']) < float(v)]
                    elif k == 'sector':
                        data = [i for i in data if i['sector'].lower() == v.lower()]

                if 'Error Message' in data and 'upgrade' in data['Error Message']:
                    continue
                return data
        except:
            print("Error in {}".format("getScreener"))

    #clears json files to save space
    def removeALL(self):
        try:
            directory = Path(__file__).absolute().parent / 'Tickers'

            for f in os.listdir(directory):
                os.remove(directory/f)
        except:
            print("Error in {}".format("removeALL"))
    



if __name__ == '__main__':
    api = API()
    print(api.pricePredict("SKLZ"))
    # testing = {
    #         "Historical":api.getHistorical('TSLA', 'close' , '2021-03-31 00:00:00'),
    #         "Realtime":api.getRealtime('TSLA'),
    #         "Profile":api.getProfile("TSLA"),
    #         "Gainer":api.mostGainer(),
    #         "Active":api.mostActive(),
    #         "Loser":api.mostLoser(),
    #         "Sector":api.getSector(),
    #         "MarketHours":api.getMarketHours(),
    #         "News":api.getNews("TSLA"),
    #         "Rating":api.getRating("TSLA"),
    #         "Screener":api.getScreener({"marketCapMoreThan":5000000}),
    #         "RemoveAll":api.removeALL()
    # }
    # for k,v in testing.items():
        # print("{} : {}".format(k,v)[:100])