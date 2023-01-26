from flask import Flask,request
from binance.client import Client
from binance.enums import *
import requests
import config,math
import os
import json

app = Flask(__name__)

def line(msg,token):
    try:
        url = 'https://notify-api.line.me/api/notify'
        headers = {'content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + token}
        r = requests.post(url, headers=headers, data={'message': msg})
    except:
        print('Cannot access line noti')

def round_decimals_down(number:float, decimals:int=2):
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math.floor(number)

    factor = 10 ** decimals
    return math.floor(number * factor) / factor

def get_cash(client):
    item = client.futures_account()
    balance = float(item['totalMarginBalance']) #all balance
    cash = float(item['totalCrossWalletBalance']) - float(item['totalInitialMargin']) #cross wallet balance - all margin
    return balance, cash

def get_existing_amount(symbol, client):
    i = float(client.futures_position_information(symbol = symbol)[-1]['positionAmt'])
    return i

def trade_order(symbol, side, qty, client):
    try:
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            positionSide='BOTH',
            type='MARKET',
            quantity=qty
            )
        return {
            'status': "Success",
            'message' : format(order)
        }
    except Exception as e:
        return {
            'status': 'False',
            'message': format(e)
            }

@app.route('/')
def helloworld():
    return 'APP is running.'

@app.route('/checkport')
def checkport():
    try:
        client = Client(config.API_key, config.API_secret, tld='com')
        return format(client.futures_account_balance())
    except:
        return 'Cannot access API ACTUAL port'

@app.route('/checkport_test')
def checkport_test():
    try:
        client = Client(config.test_API_key, config.test_API_secret, tld='com')
        client.FUTURES_URL  = config.testnet_URL
        return format(client.futures_account_balance())
    except:
        return 'Cannot access API ACTUAL port'

@app.route('/future_trade', methods=['POST'])
def future_trade():
    # check Data Format
    try:
        data = json.loads(request.data)
        symbol = data["ticker"]
        strategy = data['strategy']
        side = strategy['SIDE'].upper()
        name = data['Name']
        position = strategy['POSITION']
        current_price = data['Price']
    except Exception as e:
        return {
            'status': 'Wrong format data',
            'message': format(e)
            }
    # check Pass phrase
    if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            "code": "error",
            "message": "Nice try Bitch"
        }

    # check TEST or which port trade
    if data['which_port'].upper() == "REAL":
        client = Client(config.API_key, config.API_secret, tld='com')
        token_line = config.line_token
    else:
        client = Client(config.test_API_key, config.test_API_secret, tld='com')
        client.FUTURES_URL  = config.testnet_URL      
        
    require_qty_raw = float(strategy['QTY'])
    leverage_setup = round(float(strategy['LEVERAGE']))
    client.futures_change_leverage(symbol = symbol, leverage = leverage_setup)
    
    # Round Decimal of symbol
    for i in client.futures_exchange_info()["symbols"]:
        if i['symbol'] == symbol:
            precision =  int(i['quantityPrecision'])
            break
    require_qty = round_decimals_down(require_qty_raw, precision)
    if side == "SELL":
        require_qty = -require_qty
    # make order
    action_amount = require_qty
    if action_amount > 0:
        order = trade_order(symbol, "BUY", abs(action_amount), client)
    elif action_amount < 0:
        order = trade_order(symbol, "SELL", abs(action_amount), client)
    else:
        order = trade_order(symbol, side, abs(action_amount), client)
    
    line(f'❗{side}❗ @ราคา{current_price} เหรียญ{symbol} จำนวน ={abs(action_amount)}{symbol[:3]} ระบบ 📊{name} สถานะ {position}',token_line)
    return(order)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))