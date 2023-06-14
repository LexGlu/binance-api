import json
import aiohttp
import asyncio
import pandas as pd
import os
import database as db

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scripts.utils as utils

workdir = os.path.dirname(__file__)

def save_to_db(df, table_name):
    # create table if it doesn't exist
    if not db.table_exists(table_name):
        db.create_table(table_name)
    
    # insert data into database
    db.insert_data(df, table_name)

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
                utils.log_message(f'No data returned for {symbol} {interval} and start_time {start_time}. Check if new data is available since last run. Skipping...')
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
            utils.save_to_csv(df, data_name)


if __name__ == '__main__':
    
    # set up variables for data collection 
    base_url = 'https://api.binance.com/api/v3/klines?'
    limit = '1000' # max limit for api call is 1000
    intervals = ('1d', '4h', '1h', )
    symbols = ('BTCUSDT', 'ETHUSDT', 'BNBUSDT', )
    
    # read start time from file or set to None if file is empty (first run)
    start_time = utils.get_start_time()
    
    for symbol in symbols:
        for interval in intervals:
            print(f'Collecting {symbol} {interval} data...')
            asyncio.run(get_data(base_url, symbol, interval, limit, start_time))
            
    # write current time as timestamp in milliseconds to file for next run to use as start_time (in order to get only new data)
    utils.set_start_time()
    
    print('Finished collecting data. Check logs.txt for details.')
    