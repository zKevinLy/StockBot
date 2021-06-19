# LSTM (long short term memory) to predict closing stock price using past 60 day stock price
import math
import numpy as np 
import pandas as pd 
import pyapi
import pyjsontocsv
import pytime
from sklearn.preprocessing import MinMaxScaler
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, LSTM

import matplotlib.pyplot as plt 



def predictNext(ticker):
    plt.style.use('fivethirtyeight')
    nDays = 100
    def getCSV(ticker):
        api = pyapi.API().storeHistoricalInfo(ticker)
        pyjsontocsv.jsonToCSV("Tickers",ticker)
        return pd.read_csv('Tickers/{}.csv'.format(ticker))

    df = getCSV(ticker)

    # #visualizing price history
    # plt.figure(figsize=(16,8))
    # plt.title("Close Price History: {}".format(ticker))
    # plt.plot(df['close'])
    # plt.xlabel('Date', fontsize=18)
    # plt.ylabel('Price ($)', fontsize=18)
    # plt.show()

    #filter close column
    data = df.filter(['close'])
    dataset = data.values
    #getting training data
    training_data_len = math.ceil(len(dataset) * 0.8)
    #scale data
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(dataset)
    #create training data set given nDays prediction
    train_data = scaled_data[0:training_data_len,:]
    x_train, y_train = [], []
    for i in range(nDays, len(train_data)):
        x_train.append(train_data[i-nDays:i,0])
        y_train.append(train_data[i,0])
    #reshape data
    x_train,y_train = np.array(x_train), np.array(y_train) 
    x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))

    
    def simulation():
        #build lstm
        model = Sequential()
        model.add(LSTM(50, return_sequences=True,input_shape=(x_train.shape[1],1)))
        model.add(LSTM(50, return_sequences=False))
        model.add(Dense(25))
        model.add(Dense(1))
        #compile and train model
        model.compile(optimizer='adam', loss = 'mean_squared_error')
        model.fit(x_train,y_train,batch_size=1,epochs=1)
        #create test dataset
        test_data = scaled_data[training_data_len - nDays:,:]
        x_test = [test_data[i-nDays:i,0] for i in range(nDays, len(test_data))]
        y_test = dataset[training_data_len:,:]
        #reshape data
        x_test = np.array(x_test)
        x_test = np.reshape(x_test, (x_test.shape[0],x_test.shape[1],1))
        #get predicted price
        predictions = model.predict(x_test)
        predictions = scaler.inverse_transform(predictions)
        #get root mse
        rmse = np.sqrt( np.mean( predictions-y_test )**2 )

        train = data[:training_data_len]
        valid = data[training_data_len:]
        valid['Predictions'] = predictions

    #     #visualize
    #     plt.figure(figsize=(16,8))
    #     plt.title("Model for {}".format(ticker))
    #     plt.xlabel('Date', fontsize=18)
    #     plt.ylabel('Price ($)', fontsize=18)
    #     plt.plot(train['close'][-10:])
    #     plt.plot(valid[['close','Predictions']])
    #     plt.legend(['Train', 'Val', 'Predictions'], loc='lower right')
    #     plt.show()

        #create new df
        new_df = getCSV(ticker)
        new_df_close = new_df.filter(['close'])
        #get last 60 days closing
        last_ndays = new_df_close[-nDays:].values
        last_ndays_scaled = scaler.transform(last_ndays)
        X_test = np.array([last_ndays_scaled])
        X_test = np.reshape(X_test, (X_test.shape[0],X_test.shape[1],1))
        pred_price = model.predict(X_test)
        pred_price = scaler.inverse_transform(pred_price)
        last_day = new_df.filter(['date']).values[len(new_df_close.values)-1][-1]
        return pred_price, last_day
    

    #results
    pd.options.mode.chained_assignment = None
    prices = np.array([simulation() for i in range(5)],dtype=object)
    last_day = prices[0,1]
    prices = prices[:,0]
    avg = np.average(prices)
    nextDay = pytime.Time().timeMath(last_day, days=1)
    return avg
    

if __name__ == '__name__':
    # x = predictNext("SKLZ")
    # print(x)
    print("hi")