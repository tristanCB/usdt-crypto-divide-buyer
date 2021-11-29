import argparse
from binance import Client
import pprint
import math
import requests
import ast

pp = pprint.PrettyPrinter(indent=4)

class HotSwap():
    def __init__(self, amount, symbols=[]):
        api_key = "<my api key>"
        api_secret = "<my api secret>"
        self.client = Client(api_key=api_key, api_secret=api_secret)
        self.amount = amount
        self.symbols = symbols
    
    def get_kline_timeframe(self, symbol, timeframe='1m', limit=1):
        # Gets most recent price using bargraph data for close
        url = "https://api.binance.com/api/v3/klines"
        parameters = [
            ('symbol', symbol),
            ('interval', timeframe),
            ('limit',limit)
            ]
        data = requests.get(
            url,
            params=parameters,
            )
        assert data.status_code == 200    
        return float(ast.literal_eval(data.text)[0][4])

    # place a test market buy order, to place an actual order use the create_order function
    def execute_trade(self, symbol):
        # Executes trade on USDT pair
        pair = symbol.strip() + 'USDT'
        pair = pair.upper()
        info = self.client.get_symbol_info(pair)
        price_1m = self.get_kline_timeframe(pair)
        step_size = 0.0
        
        # Gets precision
        for f in info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                step_size = float(f['stepSize'])
        precision = int(round(-math.log(step_size, 10), 0))

        # Sets tarde amounts
        ammount = self.amount/len(self.symbols)
        amt_to_buy = ammount/price_1m
        nxt_amt_to_buy = round(amt_to_buy - (amt_to_buy % float(info['filters'][2]['minQty'])), precision)

        # Executes trades
        try:
            optin = self.client.create_order(
                symbol=pair,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=nxt_amt_to_buy)
            print(optin)
        except:
            print('Failed to buy')

    def execute_trades(self):
        for symbol in self.symbols:
            self.execute_trade(symbol)

def main():
    parser = argparse.ArgumentParser(description="Divite my money in between these cryptos.")
    # add arguments
    parser.add_argument('--amount', dest='Amount', required=True, type=float)
    parser.add_argument('--symbols', dest='Symbols', help='delimited list input', type=str)
    args = parser.parse_args()

    if args.Amount:
        Amount = args.Amount
    else:
        Amount = 100

    if args.Symbols:
        Symbols = [str(item) for item in args.Symbols.split(',')]
    else:
        Symbols = ['BTC', 'ETH']

    print(Amount)
    print(Symbols)
    
    args = parser.parse_args()
    hs = HotSwap(Amount, Symbols)
    hs.execute_trades()

# call main
if __name__ == '__main__':
    main()