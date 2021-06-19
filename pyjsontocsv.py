import json
import csv
import pyapi 
import pandas as pd

def jsonToCSV(directory, fnameJSON):
    with open("{}/{}.json".format(directory,fnameJSON), 'r+') as curJSON:
        data = json.load(curJSON)
        with open("{}/{}.csv".format(directory,fnameJSON), 'w') as curCSV:
            alldata = []
            for k,v in data.items():
                v['date'] = k
                alldata.append(v)

            columns = v.keys()
            writer = csv.DictWriter(curCSV, fieldnames=columns)
            writer.writeheader()

            for data in alldata:
                writer.writerow(data)

def getCSV(ticker):
    api = pyapi.API().storeHistoricalInfo(ticker)
    jsonToCSV("Tickers",ticker)
    return pd.read_csv('Tickers/{}.csv'.format(ticker))

if __name__ == '__main__':
    jsonToCSV("Tickers","SKLZ")