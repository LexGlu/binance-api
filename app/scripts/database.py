import psycopg2
import pandas as pd
import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scripts.utils as utils


def create_connection():
    connection = psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST'),
        port=os.environ.get('POSTGRES_PORT'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        database=os.environ.get('POSTGRES_DB')
    )
    return connection

def create_table(table_name):
    connection = create_connection()
    cursor = connection.cursor()
    query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
        open_time timestamp PRIMARY KEY,
        open_price float,
        high_price float,
        low_price float,
        close_price float,
        volume float,
        close_time timestamp,
        quote_asset_volume float,
        number_of_trades int,
        taker_buy_base_asset_volume float,
        taker_buy_quote_asset_volume float
        )
    """
    cursor.execute(query)
    connection.commit()
    connection.close()
    utils.log_message(f'Created {table_name} table')
    

def table_exists(table_name):
    connection = create_connection()
    cursor = connection.cursor()
    query = f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = '{table_name}'
        )
    """
    cursor.execute(query)
    exists = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return exists


def insert_data(df, table_name):
    connection = create_connection()
    cursor = connection.cursor()
    for row in df.itertuples():
        query = f"""
            INSERT INTO {table_name} VALUES (
                '{row.open_time}',
                {row.open},
                {row.high},
                {row.low},
                {row.close},
                {row.volume},
                '{row.close_time}',
                {row.quote_asset_volume},
                {row.number_of_trades},
                {row.taker_buy_base_asset_volume},
                {row.taker_buy_quote_asset_volume}
            )
            ON CONFLICT (open_time) DO NOTHING
        """
        cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    utils.log_message(f'Inserted {len(df)} rows into {table_name} table')
    
    
def get_table_names():
    connection = create_connection()
    cursor = connection.cursor()
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """
    cursor.execute(query)
    table_names = [row[0] for row in cursor.fetchall()] # returns list of tuples, need to get first element of each tuple (the table name)
    connection.close()
    return table_names
    
    
def get_data(table_name):
    connection = create_connection()
    cursor = connection.cursor()
    query = f"""
        SELECT * FROM {table_name}
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data)
    df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']
    df['open_time'] = pd.to_datetime(df['open_time']) 
    df['close_time'] = pd.to_datetime(df['close_time'])
    df = df.set_index('open_time') # needed for candlestick chart in plotly (otherwise it won't show the x-axis)
    df = df.sort_index()
    connection.close()
    return df
