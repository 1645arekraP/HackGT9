from twilio.rest import Client
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import yfinance as yf
import plotly.graph_objs as go
from priv import *
from flask import send_from_directory
 
yf.pdr_override()
client = Client(account_sid, auth_token)
app = Flask(__name__)
 
 # Create a graph of stock data
def createGraph(stock1):
   df = yf.download(tickers=stock1,period='6h',interval='1m')
   fig=go.Figure()
   fig.add_trace(go.Candlestick(x=df.index,
               open=df['Open'],
               high=df['High'],
               low=df['Low'],
               close=df['Close'], name = 'market data'))
   fig.update_layout(
   title= str(stock1)+' Live Share Price:',
   yaxis_title='Stock Price (USD per Shares)')
   fig.write_image("fig.png")

# Method for uploading files to flask server on NGROK
@app.route('/uploads/<filename>', methods=['GET', 'POST'])
def uploaded_file(filename):
    return send_from_directory('/Users/parker/HackGT9-1/',
                               filename)

 
 # Twilio SMS message
@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
   body = request.values.get('Body', None)
   reply="CryptoPACK\n"
   """Respond to incoming messages with a friendly SMS."""
   resp = MessagingResponse()
   stockPick=body
   # Getting stock info
   stock = yf.Ticker(body)
   price = stock.info['regularMarketPrice']

   # Check to see if invalid input
   if price==None:
       reply="I am not sure what you meant. Use the correct stock symbol, and if you're trying to use a crypto coin make sure to include a dash followed by the currency ex. BTC-USD"
       msg=resp.message(reply)
   else:
        reply+=body+" Price: $"+str(price)
        msg=resp.message(reply)
        # Create a graph using plotly
        createGraph(stockPick)
        # Upload to flask server on NGROK
        uploaded_file('fig.png')
        msg.media('https://fa0e-38-101-220-237.ngrok.io/uploads/fig.png')
   return str(resp)
 
if __name__ == '__main__':
      app.run()
