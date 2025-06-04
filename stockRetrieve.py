#PREREQUISITE: - Register on https://developer.settrade.com/open-api/
#              - Added your own 'app_id' & 'app_secret' below 

# ------------ SETTRADE_V2 ------------
import settrade_v2
from settrade_v2 import Investor

# Initialize the Investor object with your credentials
investor = Investor(app_id="", app_secret="",
                    broker_id="SANDBOX", app_code="SANDBOX", is_auto_queue = False)
# Access the market data
market = investor.MarketData()


# Get candle stick
out = market.get_candlestick(
symbol="AMATA",
interval="1m", #'1m','3m','5m','10m','15m','30m','60m','120m','240m','1d','1w','1M'
limit=31,
#start= "2025-01-01T00:00",  #Opt.- "YYYY-mm-ddTHH:MM"
#end= "2025-01-31T23:59",    #Opt.- "YYYY-mm-ddTHH:MM"
normalized=True
)

# Display the retrieved data
print(out)

""" out (dictionary (API response))
[{
'close': [58.75],
    'high': [66.75],
    'lastSequence': 105576,
    'low': [57.0],
    'open': [66.0],
    'time': [1677517200],
    'value': [0],
    'volume': [29500]
}]
"""

# ------------ OBSOLETE - SETTRADE ------------
"""
from settrade.openapi import Investor

# Initialize the Investor object with your credentials
investor = Investor(app_id="", app_secret="",
                    broker_id="SANDBOX", app_code="SANDBOX")

# Access the market data
market = investor.MarketData()

# Retrieve historical data for a specific symbol
historical_data = market.get_history(
    symbol="PTT",           # Replace with your desired stock symbol
    start="2023-01-01",     # Start date in YYYY-MM-DD format
    end="2023-12-31",       # End date in YYYY-MM-DD format
    interval="1d"           # Interval options: "1d", "1w", "1m"
)

# Display the retrieved data
print(historical_data)
"""
