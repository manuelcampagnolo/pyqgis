from datetime import datetime as dt

# convert string day_hour:minute to day of month
dt.strptime(x+'_08_2018', '%d_%H:%M_%m_%Y').day
