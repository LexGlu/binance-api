import datetime
import time
import json
import aiohttp
import asyncio
import pandas as pd
import os
from utils import log_message
from database import table_exists, create_table, insert_data

workdir = os.path.dirname(__file__)

def save_to_db(df, table_name):
    # create table if it doesn't exist
    if not table_exists(table_name):
        create_table(table_name)
    
    # insert data into database
    insert_data(df, table_name)

def save_to_csv(df, file_name):
    # append data to csv file if it exists (header=False to not write header again)
    if os.path.exists(f'{workdir}/data/{file_name}.csv'):
        df.to_csv(f'{workdir}/data/{file_name}.csv', mode='a', header=False, index=False)
        log_message(f'Appended {len(df)} rows to {file_name}.csv')
    else:
        df.to_csv(f'{workdir}/data/{file_name}.csv', index=False)
        log_message(f'Created {file_name}.csv with {len(df)} rows')


async def get_data(base_url, symbol, interval, limit, start_time=None):
    # get data from binance api
    async with aiohttp.ClientSession() as session:
        # create url for api call
        url = f'{base_url}symbol={symbol}&interval={interval}&limit={limit}'
        # if start_time is not None, add it to the url as a parameter
        if start_time:
            url += f'&startTime={start_time}'
        
        async with session.get(url) as response:
            data = await response.text()
            data = json.loads(data)
            
            # check if data is empty and return if it is
            if not data:
                log_message(f'No data returned for {symbol} {interval} and start_time {start_time}. Check if new data is available since last run. Skipping...')
                return
            
            # remove last column (unused field from api call, says to ignore it)
            data = [row[:-1] for row in data]
            
            # create dataframe from data
            df = pd.DataFrame(data) 
            df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            data_name = f'{symbol}_{interval}'
            
            # save data to database
            save_to_db(df, data_name)
            
            # save data to csv file
            save_to_csv(df, data_name)


if __name__ == '__main__':
    
    # set up variables for data collection 
    base_url = 'https://api.binance.com/api/v3/klines?'
    limit = '1000' # max limit for api call is 1000
    intervals = ('1d', '4h', '1h', )
    symbols = ('BTCUSDT', 'ETHUSDT', 'BNBUSDT', )
    
    # read start time from file or set to None if file is empty (first run)
    with open(f'{workdir}/data/start_time.txt', 'r') as f:
        # read start_time from file
        start_time = f.read()
        
        # if file is empty, set start_time to None
        if not start_time:
            start_time = None
    
    for symbol in symbols:
        for interval in intervals:
            print(f'Collecting {symbol} {interval} data...')
            asyncio.run(get_data(base_url, symbol, interval, limit, start_time))
            
    # write current time as timestamp in milliseconds to file for next run to use as start_time (in order to get only new data)
    with open(f'{workdir}/data/start_time.txt', 'w') as f:
        timestamp = int(time.time() * 1000)
        f.write(str(timestamp))
    
    print('Finished collecting data. Check logs.txt for details.')
    