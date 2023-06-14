import datetime
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
    

def get_start_time():
    with open(f'{parent_dir}/data/start_time.txt', 'r') as f:
        # read start_time from file
        start_time = f.read()
        
        # if file is empty, set start_time to None
        if not start_time:
            start_time = None
            
    return start_time


def set_start_time():
    # write current time as timestamp in milliseconds to file for next run to use as start_time (in order to get only new data)
    with open(f'{parent_dir}/data/start_time.txt', 'w') as f:
        timestamp = int(time.time() * 1000)
        f.write(str(timestamp))
        