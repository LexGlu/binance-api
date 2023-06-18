import datetime
import json
import os
import time

from pathlib import Path


# Description: Common functions for the project that are used in multiple files

# get directory where data and logs folders are located
parent_dir = Path(__file__).resolve().parent.parent


def log_message(message):
    with open(f'{parent_dir}/logs/logs.txt', 'a') as f:
        timestamp = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        f.write(f'{timestamp}: {message}\n')
        

def save_to_csv(df, file_name):
    # append data to csv file if it exists (header=False to not write header again)
    if os.path.exists(f'{parent_dir}/data/{file_name}.csv'):
        df.to_csv(f'{parent_dir}/data/{file_name}.csv', mode='a', header=False, index=False)
        log_message(f'Appended {len(df)} rows to {file_name}.csv')
    else:
        df.to_csv(f'{parent_dir}/data/{file_name}.csv', index=False)
        log_message(f'Created {file_name}.csv with {len(df)} rows')


def get_start_time_from_json(interval, symbol):
    with open(f'{parent_dir}/data/start_time.json', 'r') as file:

        # try to read data from file (if it exists) else create empty dictionary
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError:
            data = {}
        
        # check if there is data in the file
        if not data:
            return None
        
        start_time = data.get(symbol, {}).get(interval) # will return None if symbol or interval doesn't exist in data
        
        return start_time
        
        
def set_start_time_to_json(interval, symbol):
    # write current time as timestamp in milliseconds to file for next run to use as start_time (in order to get only new data)
    with open(f'{parent_dir}/data/start_time.json', 'r+') as file:
        
        # try to read data from file (if it exists) else create empty dictionary
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError:
            data = {}
    
        timestamp = int(time.time() * 1000)

        symbol_data = data.get(symbol, {})
        symbol_data[interval] = timestamp
        data[symbol] = symbol_data
        
        file.seek(0) # move cursor to beginning of file
        json.dump(data, file) # write data to file (overwrites existing data)
        