import time
import pandas as pd
import requests
import json
import traceback
from binance.spot import Spot
import csv
#======================================
#pip install binance-connector
#======================================

class ftxapi:
    def __init__(self):
        self.usd = 100          #一回の注文で使うUSD量
        self.symbol = 'BTCBUSD' #注文銘柄
        self.client = Spot(key="", secret="")
        self.url = ""   #discord webhook url
        self.path = ""   #bot実行パス（ここにcsv保存される）
        return

    #discord通知関数
    def chat(self, text):
        webhook_url  = self.url
        main_content = {'content': f'{text}'}
        headers      = {'Content-Type': 'application/json'}
        while True:
            try:
                response = requests.post(webhook_url, json.dumps(main_content), headers=headers)
                return
            except Exception as e:
                traceback.print_exc()
                time.sleep(5)
                return

    #発注関数
    def market_order(self,params):
        time_wait = 10
        while True:
            try:
                self.client.new_order(**params)
                return
            except Exception as e:
                traceback.print_exc()
                self.chat(f"order error :{e}")
                time.sleep(time_wait)
                time_wait *= 2

    #発注、購入データ整理
    def price_quantity(self):
        time_wait = 10
        while True:
            try:
                #価格取得、購入枚数計算
                response = self.client.klines(symbol="BTCBUSD", interval="1m",limit="1")
                pri = float(response[0][4])
                coin = self.usd/float(pri)
                coin = round(coin,3)
                
                #購入データ保存、平均取得価格等計算、discord通知
                buy_data = [self.symbol,pri,coin]
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
                self.chat(f"===\n平均取得価格 : {round(average_price,1)} USD\n現在価格 : {round(float(pri),1)} USD\n積立PNL : {round((float(pri)/average_price-1)*100,3)} %\n総購入量 : {round(sum_amount,3)} BTC\n===")
                return coin
            except Exception as e:
                traceback.print_exc()
                self.chat(f"order error :{e}")
                time.sleep(time_wait)
                time_wait *= 2

    #メイン実行関数
    def main(self):
        coin = self.price_quantity()
        order_params = {
            'symbol': self.symbol,
            'side': 'BUY',
            'type': 'MARKET',
            'quantity': coin,
        }
        self.market_order(order_params)
        return
                
if __name__ == "__main__":
    ftxo = ftxapi()
    ftxo.main()