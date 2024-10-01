from datetime import datetime, timedelta

current_day = datetime.now()

dates = []

for el in range(30):
    dates.append(current_day)
    current_day += timedelta(days=1)

for day in dates:
    print(f"{day.day}.{day.month}")