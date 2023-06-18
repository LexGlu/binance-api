import plotly.graph_objects as go
import requests
import scripts.database as db
import config

from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler


app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app)


# root page which redirects to charts page
@app.route('/', methods=['GET'])
def index():
    return redirect('/charts')


@app.route('/charts', methods=['GET'])
def charts():
    
    # function to convert candlestick name to more readable format
    def kline_repr(kline):
        return f'{kline.split("_")[0].upper()} {kline.split("_")[1]}'
    
    # get list if available candlestick charts
    klines = db.get_table_names()
    
    # get candlestick name parameter from url
    kline = request.args.get('kline')
    
    if not kline or kline not in klines:
        kline = klines[0]
        
    # get candlestick data from database
    df = db.get_data(kline)
    kline_fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
    kline_fig.update_layout(title=f'{kline_repr(kline)} Candlestick Chart')
    
    # convert candlestick chart to JSON to pass to template
    kline_fig_JSON = kline_fig.to_json()
    
    def kline_repr(kline):
        return f'{kline.split("_")[0].upper()} {kline.split("_")[1]}'
    
    klines = [{'name': kline_repr(kline), 'arg': kline} for kline in klines]
    klines.sort(key=lambda x: x['name']) # sort by name
    
    pie_chart_fig_JSON = get_market_cap_data()
    
    return render_template('index.html', kline_fig=kline_fig_JSON, klines=klines, pie_chart_fig=pie_chart_fig_JSON)


def get_market_cap_data():
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?start=1&limit=10&convert=USD' # API endpoint to retrieve top 10 cryptocurrencies (sorted by market cap desc)
        api_key = config.api_key # API key from CoinMarketCap
    
        headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            market_cap_data = {d['symbol']: round(d['circulating_supply'] * d['quote']['USD']['price'] / 1000000000, 2) for d in data['data']} # convert market cap to billions
            print(market_cap_data)
            
            pie_chart_fig = go.Figure(data=[go.Pie(labels=list(market_cap_data.keys()), values=list(market_cap_data.values()))])
            pie_chart_fig.update_layout(title='Market Cap of Top 10 Cryptocurrencies (Billion USD)')
            pie_chart_fig_JSON = pie_chart_fig.to_json()
            
            return pie_chart_fig_JSON
        

@socketio.on('connect', namespace='/chart') 
def connect():
    while True:
        time_to_sleep = 30 # update chart every 30 seconds (for demo purposes)
        pie_chart_fig_JSON = get_market_cap_data()
        socketio.emit('update_chart', {'chart_data': pie_chart_fig_JSON}, namespace='/chart')
        socketio.sleep(time_to_sleep)


if __name__ == '__main__':
    http_server = pywsgi.WSGIServer(('0.0.0.0', 5555), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
