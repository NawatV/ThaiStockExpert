#PREREQUISITE: - Register on https://developer.settrade.com/open-api/
#              - Added your own 'app_id' & 'app_secret' below 

# ------------ SETTRADE_V2 ------------
import settrade_v2
from settrade_v2 import Investor

# ========= Get & store stock's history data | Create .txt & print to it | Start-End Date |
#           Loop | try-except =================

# Initialize the Investor object with your credentials
investor = Investor(app_id="", app_secret="",
                    broker_id="SANDBOX", app_code="SANDBOX", is_auto_queue = False)
# Access the market data
market = investor.MarketData()

# --- Loop ---
isAgain = True
rnd = 1
while isAgain == True :
#    try:
    # Get candle stick | *** Latest data = 3 working days before ***
    print("Stock Name (Case-Insen):", end=" ")
    sym = input()
    print("Interval (1d(daily),1w,1m,3m,5m,10m,15m,30m,60m,120m,240m,1M):", end=" ")
    itv = input()
    print("Candle Amount:", end=" ")
    lim = input()
    print("Start-End Date? (y or n): ", end="")
    isDate = input()
    if isDate == "y":
        #--- Start-End Date ---
        print("Start Date (DD/MM/YYYY): ", end="")
        sd = input()
        sdS = sd.split("/")
        y = sdS[2]
        m = sdS[1]
        d = sdS[0]
        startD = f"{y}-{m}-{d}T00:00"
        print("End Date (DD/MM/YYYY): ", end="")
        ed = input()
        edS = ed.split("/")
        y = edS[2]
        m = edS[1]
        d = edS[0]
        endD = f"{y}-{m}-{d}T23:59"
        #----------------------
        res = market.get_candlestick(
        symbol=sym,
        interval=itv,   #1m, 3m, 5m, 10m, 15m, 30m, 60m, 120m, 240m, 1d, 1w, 1M
                            #1d=Daily data | 1w=Weekly data | 1m=Monthly data
        limit=lim,      #Candle amount
        start= startD,  #Opt.- "YYYY-mm-ddTHH:MM"
        end= endD,      #Opt.- "YYYY-mm-ddTHH:MM"
                            #If no -> get the candles in the latest period
                            #If yes -> get the candles in that period
        normalized=True
        )
    elif isDate == "n":
        res = market.get_candlestick(symbol=sym, interval=itv, limit=lim, normalized=True)

    # Store in list
    li_lastSequence = res["lastSequence"]
    li_time = res["time"]
    li_open = res["open"]
    li_high = res["high"]
    li_low = res["low"]
    li_close = res["close"]
    li_volume = res["volume"]
    li_value = res["value"]

    # Create .txt & print to it
    rndStr = str(rnd)
                    ### PATH !!!
    res_txtFile = f"C://Users//LENOVO//Desktop//thai_stock_expert//outputTxt//{sym}_{rndStr}.txt" #Must use
            # Opening the file in write mode ("w") will create the file if it doesn't exist,
            # or overwrite it if it does
    with open(res_txtFile, "w") as file:
        file.write(f"lastSequence: {li_lastSequence} \n")
        file.write(f"time: {li_time} \n")
        file.write(f"open: {li_open} \n")
        file.write(f"high: {li_high} \n")
        file.write(f"low: {li_low} \n")
        file.write(f"close: {li_close} \n")
        file.write(f"volume: {li_volume} \n")
        file.write(f"value: {li_value} \n")

    # Display the retrieved data
        #print("close: ", li_close)

    # Start again
    isAgain = False
    print("Get more? (y or n): ", end="")
    z = input()
    if z == "y":
        isAgain = True 
        rnd += 1
        print("--------------------------------")
#    except:
#        print("Something wrong, check the source code!")
#        print("--------------------------------")



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
