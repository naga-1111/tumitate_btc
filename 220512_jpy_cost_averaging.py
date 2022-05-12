from ast import While
from dataclasses import replace
import ccxt
from numpy import average
import pandas as pd
import requests
import traceback
import datetime
import json
import time
import csv

class bitflyer_order:
    def __init__(self):
        self.url = ""#discord url
        self.jpy =    #一回の注文で何円分の現物を買うか
        self.symbol = "BTC/JPY"#"ETH/JPY"
        self.exchange = ccxt.bitflyer({
            "apiKey": "",
            "secret": "",
        })
        self.sleep_time = 10
        self.path = "/home/ec2-user/jpy_cost"
        return
        
    def chat(self, text):
        while True:
            try:                        
                webhook_url  = self.url
                main_content = {'content': f'{text}'}
                headers      = {'Content-Type': 'application/json'}
                response     = requests.post(webhook_url, json.dumps(main_content), headers=headers)
                return response
            except Exception as e:
                traceback.print_exc()
                time.sleep(10)

    def market_order(self,quantity):
        while True:
            try:
                self.exchange.create_order(
                    symbol = f'{self.symbol}',
                    side = "buy",
                    amount = f'{quantity}',
                    type = "MARKET",#"MARKET","LIMIT"
                    params = { "product_code" : f'{self.symbol.upper().replace("/","_")}' }
                )
                return
            except Exception as e:
                traceback.print_exc()
                self.chat(f"order error : {e}")
                self.chat(f"retry in {self.sleep_time} sec")
                time.sleep(self.sleep_time)
                self.sleep_time *= 2
                
    def quantity(self):
        while True:
            try:
                pri = ccxt.bitflyer().fetch_ticker('BTC/JPY', params = { "product_code" : self.symbol.replace("/","_") })["last"]
                coin = self.jpy/float(pri)
                if "BTC" in self.symbol:
                    rcoin = round(coin,5)
                else:
                    rcoin = round(coin,4)
                buy_data = ["BTCJPY",pri,rcoin]
                with open (f"{self.path}/buy_data.csv", "a", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(buy_data)
                    
                df = pd.read_csv(f"{self.path}/buy_data.csv", header=None, names=['symbol', 'price', "amount"])
                df["price"] = df["price"].apply(float)
                df["amount"] = df["amount"].apply(float)
                df["cost"] = df["price"]*df["amount"]
                
                sum_cost = df["cost"].sum()
                sum_amount = df["amount"].sum()
                average_price = sum_cost*1.001/sum_amount
                self.chat(f"===\n平均取得価格 : {round(average_price,1)} 円\n現在価格 : {round(float(pri),1)} 円\n積立PNL : {round((float(pri)/average_price-1)*100,3)} %\n総購入量 : {round(sum_amount,4)} BTC\n===")
                
                return rcoin
            except Exception as e:
                traceback.print_exc()
                self.chat(f"get balance error : {e}")
                self.chat(f"retry in {self.sleep_time} sec")
                time.sleep(self.sleep_time)
                self.sleep_time *= 2

if __name__ == '__main__':
    bo = bitflyer_order()
    quantity = bo.quantity()
    bo.market_order(quantity)
