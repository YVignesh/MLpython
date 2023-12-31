import pandas as pd

# Define the trading environment
class StockTradingEnvironment:
    def __init__(self, data, initial_balance=10000, stop_loss_percent=0.02,name):
        self.data = data
        self.name = name
        self.current_step = 0
        self.initial_balance = initial_balance
        self.balance = self.initial_balance
        self.shares_held = 0
        self.buy_price = 0  # To record buy price
        self.sell_price = 0  # To record sell price
        self.profit_loss = 0  # To record profit/loss
        self.trade_time = None  # To record time of trade
        self.stop_loss_percent = stop_loss_percent
        self.trade_book = pd.DataFrame(columns=['timestamp', 'share', 'action', 'price', 'quantity', 'profit_loss'])

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
            self.buy_price = self.data['close'].iloc[self.current_step+1]
            self.shares_held = int(self.initial_balance/self.buy_price)
            self.balance -= (self.buy_price * self.shares_held)
            self.trade_time = self.data['timestamp'].iloc[self.current_step+1]
            self.trade_book.loc[len(self.trade_book.index)] = [self.trade_time, self.name, 'BUY', self.buy_price,self.shares_held,0]
        elif action == 1:  # Sell
            self.sell_price = self.data['close'].iloc[self.current_step+1]
            self.balance += self.sell_price * self.shares_held
            self.shares_held = 0
            self.profit_loss = self.shares_held * (self.sell_price - self.buy_price)
            self.trade_time = self.data['timestamp'].iloc[self.current_step+1]
            self.df.loc[len(df.index)] = [self.trade_time, self.name, 'SELL', self.sell_price, self.shares_held, self.profit_loss]
        # Move to the next time step
        self.current_step += 1

    def apply_stop_loss(self):
        current_price = self.data['close'].iloc[self.current_step]
        if self.shares_held > 0 and current_price < (1 - self.stop_loss_percent) * self.buy_price:
            # If the current price drops below the stop-loss threshold, sell
            self.take_action(1)  # Sell
    
    def close_trade_eod(self):
        if self.shares_held != 0 and (df['timestamp'].dt.hour == 15) & (df['timestamp'].dt.minute == 15)):
            self.sell_price = self.data['close'].iloc[self.current_step]
            self.balance += self.sell_price * self.shares_held
            self.shares_held = 0
            self.profit_loss = self.shares_held * (self.sell_price - self.buy_price)
            self.trade_time = self.data['timestamp'].iloc[self.current_step]
            self.df.loc[len(df.index)] = [self.trade_time, self.name, 'SELL', self.sell_price, self.shares_held,
                                      self.profit_loss]
        