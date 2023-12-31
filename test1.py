from datetime import datetime, timedelta, time

# Define start and end dates
start_date = datetime.strptime('2023-01-01', '%Y-%m-%d')
end_date = datetime.strptime('2023-12-31', '%Y-%m-%d')

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
        print(current_datetime.strftime('%Y-%m-%d %H:%M'))

    # Increment by 15 minutes
    current_datetime += timedelta(minutes=15)

    # Reset time to the start time if it exceeds the end time
    if current_datetime.time() > end_time:
        current_datetime = current_datetime.replace(hour=start_time.hour, minute=start_time.minute)
        current_datetime += timedelta(days=1)


