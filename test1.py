from datetime import datetime, timedelta, time
from trade import run_trade

# Global Variable
interval = 'FIFTEEN_MINUTE'
start_date = '2023-01-01'
end_date = '2023-12-29'
is_intraday = False
initial_balance = 10000
stop_loss_percent = 0.02

# Define start and end dates
start_date = datetime.strptime('2023-01-01', '%Y-%m-%d')
end_date = datetime.strptime('2023-12-29', '%Y-%m-%d')

# Define start and end times
start_time = time(9, 15)
end_time = time(15, 15)

# Initialize the current date and time
current_datetime = datetime.combine(start_date, start_time)

# Define additional dates to exclude
additional_exclude_dates = [
    datetime(2023, 1, 26), datetime(2023, 3, 7), datetime(2023, 3, 30),
    datetime(2023, 4, 4), datetime(2023, 4, 7), datetime(2023, 4, 14),
    datetime(2023, 5, 1), datetime(2023, 6, 29), datetime(2023, 8, 15),
    datetime(2023, 9, 19), datetime(2023, 10, 2), datetime(2023, 10, 24),
    datetime(2023, 11, 14), datetime(2023, 11, 27), datetime(2023, 12, 25)
]

# Convert the list of additional exclude dates to a set for faster lookup
exclude_dates = set(additional_exclude_dates)

# Define days to exclude (5 and 6 represent Saturday and Sunday)
exclude_days = {5, 6}

# Iterate over dates and times
while current_datetime.date() <= end_date.date():
    # Check if the current day is not a weekend day and the date is not in exclude_dates
    if current_datetime.weekday() not in exclude_days and current_datetime.replace(hour=0, minute=0, second=0,
                                                                                   microsecond=0) not in exclude_dates:
        prior_datetime = current_datetime - timedelta(days=10)
        print(prior_datetime.strftime('%Y-%m-%d %H:%M') + ' to ' + current_datetime.strftime('%Y-%m-%d %H:%M'))
        overall_pl = 0
        df = pd.read_csv('symbolToken.csv')
        for i in range(len(df)):
            stock_data = hist_data(df.iloc[i, 0], interval, start_date, end_date)
            stock_data['is_close'] = (stock_data['timestamp'].dt.hour == 15) & (stock_data['timestamp'].dt.minute == 15)
            stock_data['RSI'] = calculate_rsi(stock_data)
            stock_data['MACD'], stock_data['Signal_Line'] = calculate_macd(stock_data)
            stock_data['is_buy'] = (stock_data['RSI'] < 30) & (stock_data['MACD'] > stock_data['Signal_Line']) & \
                                   stock_data['RSI'].diff().fillna(0).astype(int) > 0
            stock_data['is_sell'] = (stock_data['RSI'] > 70) & (stock_data['MACD'] < stock_data['Signal_Line']) & \
                                    stock_data['RSI'].diff().fillna(0).astype(int) < 0
            env = StockTradingEnvironment(stock_data, df['name'].iloc[i], is_intraday, initial_balance,
                                          stop_loss_percent)
            done = False
            while not done:
                env.apply_stop_loss()
                if stock_data['is_buy'].iloc[env.current_step] and not stock_data['is_close'].iloc[env.current_step] \
                        and env.shares_held == 0:
                    env.take_action(0)
                if stock_data['is_sell'].iloc[env.current_step] and env.shares_held != 0:
                    env.take_action(1)
                if stock_data['is_close'].iloc[env.current_step] and env.shares_held != 0 and is_intraday:
                    env.take_action(2)
                if env.current_step >= len(stock_data) - 1:
                    done = True
                    if env.shares_held != 0:
                        env.take_action(2)
                    print(df['name'].iloc[i] + ' completed ' + str(env.balance - env.initial_balance))
                    overall_pl += round((env.balance - env.initial_balance), 2)

                env.current_step += 1
            #env.reset()
            if os.path.exists('output.csv'):
                env.trade_book.to_csv('output.csv', mode='a', header=False, index=False)
            else:
                env.trade_book.to_csv('output.csv', mode='w', index=False)
        print('Overall P/L = ' + str(overall_pl))

    # Increment by 15 minutes
    current_datetime += timedelta(minutes=15)

    # Reset time to the start time if it exceeds the end time
    if current_datetime.time() > end_time:
        current_datetime = current_datetime.replace(hour=start_time.hour, minute=start_time.minute)
        current_datetime += timedelta(days=1)


