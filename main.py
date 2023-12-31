from func import hist_data, StockTradingEnvironment, calculate_rsi, calculate_macd
import pandas as pd
import os

# Global Variable
interval = 'FIFTEEN_MINUTE'
start_date = '2023-01-01'
end_date = '2023-12-29'
is_intraday = False
initial_balance = 10000
stop_loss_percent = 0.02
overall_pl = 0

df = pd.read_csv('symbolToken.csv')
for i in range(len(df)):
    stock_data = hist_data(df.iloc[i,0],interval,start_date,end_date)
    stock_data['is_close'] = (stock_data['timestamp'].dt.hour == 15) & (stock_data['timestamp'].dt.minute == 15)
    stock_data['RSI'] = calculate_rsi(stock_data)
    stock_data['MACD'], stock_data['Signal_Line'] = calculate_macd(stock_data)
    stock_data['is_buy'] = (stock_data['RSI'] < 30) & (stock_data['MACD'] > stock_data['Signal_Line']) & stock_data['RSI'].diff().fillna(0).astype(int) > 0
    stock_data['is_sell'] = (stock_data['RSI'] > 70) & (stock_data['MACD'] < stock_data['Signal_Line']) & stock_data['RSI'].diff().fillna(0).astype(int) < 0
    env = StockTradingEnvironment(stock_data,df['name'].iloc[i],is_intraday,initial_balance ,stop_loss_percent)
    done = False
    while not done:
        env.apply_stop_loss()
        if stock_data['is_buy'].iloc[env.current_step] and not stock_data['is_close'].iloc[env.current_step]\
                and env.shares_held == 0:
            env.take_action(0)
        if stock_data['is_sell'].iloc[env.current_step] and env.shares_held != 0:
            env.take_action(1)
        if stock_data['is_close'].iloc[env.current_step] and env.shares_held != 0 and is_intraday:
            env.take_action(2)
        if env.current_step >= len(stock_data) - 1:
            done = True
            if env.shares_held != 0:
                env.take_action(2
                                )
            print(df['name'].iloc[i] + ' completed ' + str(env.balance - env.initial_balance))
            overall_pl += round((env.balance - env.initial_balance),2)

        env.current_step += 1
    env.reset()
    if os.path.exists('output.csv'):
        env.trade_book.to_csv('output.csv', mode='a', header=False, index=False)
    else:
        env.trade_book.to_csv('output.csv', mode='w', index=False)
print('Overall P/L = '+str(overall_pl))


