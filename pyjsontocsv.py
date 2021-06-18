import json
import csv

def jsonToCSV(directory, fnameJSON, fnameCSV = None):
    if not fnameCSV:
        fnameCSV = fnameJSON
    with open("{}/{}.json".format(directory,fnameJSON), 'r') as curJSON:
        data = json.load(curJSON)
        with open("{}/{}.csv".format(directory,fnameCSV), 'w') as curCSV:
            writer = csv.writer(curCSV)
            alldata = []

            for k,v in data.items():
                data2 = dict()
                for a,b in v.items():
                    data2[a] = b
                data2['date']= k
                alldata.append(data2)

            for count, info in enumerate(alldata):
                if count == 0:
                    writer.writerow(info.keys())
                writer.writerow(info.values())
                
if __name__ == '__main__':
    jsonToCSV("Tickers","SKLZ","SKLZ")