from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import pyotp
from Config import Config
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import os

api_key = Config["API_KEY"]
clientId = Config["CLIENT_ID"]
pwd = Config["PIN"]
smartApi = SmartConnect(api_key)
token = Config["TOKEN"]
totp = pyotp.TOTP(token).now()
correlation_id = "abc123"
data = smartApi.generateSession(clientId, pwd, totp)
authToken = data['data']['jwtToken']
refreshToken = data['data']['refreshToken']
feedToken = smartApi.getfeedToken()
res = smartApi.getProfile(refreshToken)
smartApi.generateToken(refreshToken)
def hist_data(symboltoken,interval,fromdate,todate):
    try:
        #fromdate = fromdate + " 09:00"
        #todate = todate + " 16:00"
        symboltoken = str(symboltoken)
        historicParam={
        "exchange": "NSE",
        "symboltoken": symboltoken,
        "interval": interval,  #FIFTEEN_MINUTE
        "fromdate": fromdate,
        "todate": todate
        }
        candle = smartApi.getCandleData(historicParam)
        candle = candle['data']
        candle = pd.DataFrame(candle, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        candle['timestamp'] = pd.to_datetime(candle['timestamp'])
    except Exception as e:
        print("Historic Api failed: {}".format(e.message))
    return candle

def identify_support_resistance(data, sensitivity=5):
    # Calculate rolling mean and rolling standard deviation
    data['rolling_mean'] = data['close'].rolling(window=20).mean()
    '''data['rolling_std'] = data['close'].rolling(window=20).std()

    # Identify potential support and resistance levels
    data['Support'] = data['rolling_mean'] - sensitivity * data['rolling_std']
    data['Resistance'] = data['rolling_mean'] + sensitivity * data['rolling_std']'''

    return data

# Plotting function
def plot_support_resistance(data,name):
    plt.figure(figsize=(10, 6))
    plt.plot(data['timestamp'], data['close'], label='Close Price', color='black')
    plt.plot(data['timestamp'], data['rolling_mean'], label='Rolling Mean', linestyle='--', color='blue')
    plt.plot(data['timestamp'], data['Support'], label='Support Level', linestyle='--', color='green')
    plt.plot(data['timestamp'], data['Resistance'], label='Resistance Level', linestyle='--', color='red')
    plt.xticks(rotation=25, ha='right')
    plt.title(name)
    plt.xlabel('Timestamp')
    plt.ylabel('Price')
    plt.legend()
    plt.tight_layout()
    name = 'img/'+name
    plt.savefig(name)

def plot_candlestick_support_resistance(data):
    apds = [
        mpf.make_addplot(data['rolling_mean'], color='blue', secondary_y=False),
        mpf.make_addplot(data['Support'], color='green', secondary_y=False),
        mpf.make_addplot(data['Resistance'], color='red', secondary_y=False)
    ]

    mpf.plot(data, type='candle', addplot=apds, volume=True, figscale=1.5, style='yahoo', title='Intraday Candlestick with Support and Resistance')


# Define the trading environment
class StockTradingEnvironment:
    def __init__(self, data, name,is_intraday=True, initial_balance=100000, stop_loss_percent=0.02):
        self.data = data
        self.name = name
        self.is_intraday = is_intraday
        self.current_step = 0
        self.initial_balance = initial_balance
        self.balance = self.initial_balance
        self.shares_held = 0
        self.buy_price = 0  # To record buy price
        self.sell_price = 0  # To record sell price
        self.profit_loss = 0  # To record profit/loss
        self.trade_time = None  # To record time of trade
        self.stop_loss_percent = stop_loss_percent
        self.trade_book = pd.DataFrame(columns=['timestamp', 'share', 'action', 'price', 'quantity', 'profit_loss', 'balance'])

    def reset(self):
        self.current_step = 0
        self.balance = self.initial_balance
        self.shares_held = 0
        self.buy_price = 0
        self.sell_price = 0
        self.profit_loss = 0
        self.trade_time = None
        self.name = None

    def take_action(self, action):
        if action == 0:  # Buy
            self.buy_price = self.data['close'].iloc[self.current_step + 1]
            self.shares_held = int(self.initial_balance / self.buy_price)
            self.balance -= round(((self.buy_price * self.shares_held) + self.charges(0)),2)
            self.trade_time = self.data['timestamp'].iloc[self.current_step + 1]
            self.trade_book.loc[len(self.trade_book.index)] = [self.trade_time, self.name, 'BUY', self.buy_price,
                                                               self.shares_held, 0,self.balance]
        elif action == 1:  # Sell
            self.sell_price = self.data['close'].iloc[self.current_step + 1]
            self.balance += round((self.sell_price * self.shares_held - self.charges(1)),2)
            self.shares_held = 0
            self.profit_loss = self.shares_held * (self.sell_price - self.buy_price)
            self.trade_time = self.data['timestamp'].iloc[self.current_step + 1]
            self.trade_book.loc[len(self.trade_book.index)] = [self.trade_time, self.name, 'SELL', self.sell_price, self.shares_held,
                                          self.profit_loss,self.balance]

        elif action == 2:  # Square off
            self.sell_price = self.data['close'].iloc[self.current_step]
            self.balance += round((self.sell_price * self.shares_held - self.charges(1)),2)
            self.shares_held = 0
            self.profit_loss = self.shares_held * (self.sell_price - self.buy_price)
            self.trade_time = self.data['timestamp'].iloc[self.current_step]
            self.trade_book.loc[len(self.trade_book.index)] = [self.trade_time, self.name, 'SELL', self.sell_price, self.shares_held,
                                          self.profit_loss,self.balance]
    def apply_stop_loss(self):
        current_price = self.data['close'].iloc[self.current_step]
        if self.shares_held > 0:
            if (self.buy_price - current_price)*self.shares_held > (self.stop_loss_percent*self.initial_balance):
                # If the current price drops below the stop-loss threshold, sell
                self.take_action(1)  # Sell


    def charges(self,action):
        if self.is_intraday:
            broker_charges = 0.03
            nse_charges = 0.00325
            stt_charges = 0.025
            stamp_duty = 0.003
        else:
            broker_charges = 20
            nse_charges = 0.00325
            stt_charges = 0.1
            stamp_duty = 0.015
        if action == 0 and self.is_intraday:
            brokerage = (self.buy_price * self.shares_held) * (broker_charges/100)
            if brokerage > 20:
                brokerage = 20
            other = (self.buy_price * self.shares_held) * ((nse_charges+stamp_duty)/100)
            charge = (brokerage + other)*1.18
        elif action == 1 and self.is_intraday:
            brokerage = (self.sell_price * self.shares_held) * (0.03/100)
            if brokerage > 20:
                brokerage = 20
            other = (self.sell_price * self.shares_held) * ((nse_charges+stt_charges)/100)
            charge = (brokerage + other)*1.18
        elif action == 0 and not self.is_intraday:
            brokerage = broker_charges
            other = (self.buy_price * self.shares_held) * ((nse_charges+stamp_duty+stt_charges)/100)
            charge = (brokerage + other)*1.18
        elif (action == 1 and not self.is_intraday):
            brokerage = broker_charges
            other = (self.sell_price * self.shares_held) * ((nse_charges+stt_charges)/100)
            charge = (brokerage + other)*1.18
        return round(charge,2)


# Function to calculate RSI
def calculate_rsi(data, window=14):
    close_delta = data['close'].diff()
    gain = close_delta.where(close_delta > 0, 0)
    loss = -close_delta.where(close_delta < 0, 0)

    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

# Function to calculate MACD
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data['close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['close'].ewm(span=long_window, adjust=False).mean()

    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()

    return macd, signal



