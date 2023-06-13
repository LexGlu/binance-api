from flask import Flask, render_template, request
import plotly.graph_objects as go
from database import get_table_names, get_data

app = Flask(__name__, template_folder='templates')

# root page which redirects to charts page
@app.route('/', methods=['GET'])
def index():
    return charts()


@app.route('/charts', methods=['GET'])
def charts():
    
    # function to convert candlestick name to more readable format
    def kline_repr(kline):
        return f'{kline.split("_")[0].upper()} {kline.split("_")[1]}'
    
    # get list if available candlestick charts
    klines = get_table_names()
    
    # get candlestick name parameter from url
    kline = request.args.get('kline')
    
    if not kline or kline not in klines:
        kline = klines[0]
        
    # get candlestick data from database
    df = get_data(kline)
    kline_fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
    kline_fig.update_layout(title=f'{kline_repr(kline)} Candlestick Chart')
    
    # convert candlestick chart to JSON to pass to template
    kline_fig_JSON = kline_fig.to_json()
    
    # Create pie chart data for market caps using graph objects from plotly
    symbols = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'DOGE', 'TRX', 'MATIC', 'SOL', 'DOT']
    market_caps = [502.35, 209.33, 37.17, 26.83, 9.56, 8.57, 6.47, 5.99, 5.96, 5.49]

    pie_fig = go.Figure(data=[go.Pie(labels=symbols, values=market_caps)])
    pie_fig.update_layout(title='Market Caps of 10 Cryptocurrencies (in billions of USD)')
    pie_fig_JSON = pie_fig.to_json()
    
    def kline_repr(kline):
        return f'{kline.split("_")[0].upper()} {kline.split("_")[1]}'
    
    klines = [{'name': kline_repr(kline), 'arg': kline} for kline in klines]
    klines.sort(key=lambda x: x['name']) # sort by name
    
    return render_template('index.html', kline_fig=kline_fig_JSON, pie_fig=pie_fig_JSON, klines=klines)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)
