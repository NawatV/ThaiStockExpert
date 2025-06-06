#PREREQUISITE: - Register on https://developer.settrade.com/open-api/
#              - Added your own 'app_id' & 'app_secret' below 

# ------------ SETTRADE_V2 ------------
import settrade_v2
from settrade_v2 import Investor
import csv
from datetime import datetime

# ========= Get & store stock's history data to the assigned csv -> Ready to visualize with indicators |
#           Unavai. to 'Start-End' for m(min)
#           Loop | try-except |  =================

# #-#-#-#-# Getting & Storing Part #-#-#-#-# 
# Initialize the Investor object with your credentials
investor = Investor(app_id="", app_secret="",
                    broker_id="SANDBOX", app_code="SANDBOX", is_auto_queue = False)
# Access the market data
market = investor.MarketData()

# --- Loop ---
isAgain = True
rnd = 1
stockNames = []
while isAgain == True :
    try:
        # Get candle stick | *** Latest data = 3 working days before | Unavai.'15m'
        print("Beware of error due to improper input!")
        print("Stock Name (Case-Insen):", end=" ")
        sym = input()
        print("Interval -1d(daily), 1w(weekly), 1M(monthly),")  # Internal's description
        print("1,3,5,10,30,60,120,240m (per..minute(s)): ", end="") # Unavai. to 'Start-End'
        itv = input()
        print("Candle Amount:", end=" ")
        lim = input()

        if itv not in ["1m","3m","5m","10m","30m","60m","120m","240m"]:
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
                interval=itv,   #1m, 3m, 5m, 10m, 30m, 60m, 120m, 240m, 1d, 1w, 1M
                limit=lim,      #Candle amount
                start= startD,  #Opt.- "YYYY-mm-ddTHH:MM"
                end= endD,      #Opt.- "YYYY-mm-ddTHH:MM"
                                    #If no -> get the candles in the latest period
                                    #If yes -> get the candles in that period
                normalized=True
                )
            elif isDate == "n":
                res = market.get_candlestick(symbol=sym, interval=itv, limit=lim, normalized=True)
            else:
                print("Invalid input!")
                break
        else:
            res = market.get_candlestick(symbol=sym, interval=itv, limit=lim, normalized=True)    
        print("SMA,EMA,Upper&Lower Band - NO.of Periods: ", end="")
        numPeriod = int(input())

        # Store in list
        li_lastSequence = res["lastSequence"]
        li_time = res["time"]
        li_open = res["open"]
        li_high = res["high"]
        li_low = res["low"]
        li_close = res["close"]

#>>>>>>> customize pos below & next file later

        li_sma = []
        li_ema = []
        li_up = []
        li_down = []
        #--- SMA = (Sum of (closing) prices over a period) / (No.of time periods)
        numP = 1
        prevEMA = None
        for i in range(len(li_close)):
            if numP >= numPeriod:
                sumP = 0
                for j in range(numP-numPeriod, numP, 1):
                    sumP += float(li_close[j])
                sma = sumP/numPeriod
                li_sma.append(sma) #Append SMA
                #--- Get prevEMA ---
                if prevEMA == None:
                    prevEMA = sma
            else:                
                li_sma.append("") #Append null using ""/None
            numP += 1
        #--- EMA = (Current (closing) price * Multiplier) + (Previous EMA * (1 - Multiplier))
        numP = 1
        for i in range(len(li_close)):
            if numP == numPeriod:
                ema = prevEMA
                li_ema.append(ema) #Append 1st EMA
            elif numP > numPeriod:
                #--- emaMultiplyer = 2 / (No.of time periods + 1)
                emaMultiplyer = 2/(numPeriod + 1) 
                ema = (float(li_close[i])*emaMultiplyer) + (prevEMA*(1-emaMultiplyer))
                prevEMA = ema #Update prevEMA 
                li_ema.append(ema) #Append EMA
            else:                
                li_ema.append("") #Append null using ""/None
            numP += 1
            
#>>>>>>>
            
        #--- Upper Band = SMA + k*std (k=2, )
        #--- Lower Band ---



        li_volume = res["volume"]
        li_value = res["value"]

        # Create .txt & print to it
        rndStr = str(rnd)
        #res_txtFile = f"C://Users//LENOVO//Desktop//thai_stock_expert//outputTxt//{sym}_{rndStr}.txt" #Must use
                # Opening the file in write mode ("w") will create the file if it doesn't exist,
                # or overwrite it if it does
        #with open(res_txtFile, "w") as file:
            #file.write(f"lastSequence: {li_lastSequence} \n") & the other li_xxx

        # Create .csv & print to it
        csvHeader = ['li_time','li_open','li_high','li_low','li_close','li_volume',
                     'AAPL.Adjusted','dn','li_sma','li_ema','up','direction']
                    ### PATH !!!
        res_csvFile = f"C://Users//LENOVO//Desktop//thai_stock_expert//output//{sym}_{rndStr}.csv"
        with open(res_csvFile, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(csvHeader) #X writerows

            for i in range(len(li_close)):                
                #--- dateTime ---
                timestamp = li_time[i]
                dt = datetime.fromtimestamp(timestamp) #Unix timestamp -> local time
                                                       #e.g. 2025-03-25 00:00:00 is OK
                dateTime = str(dt)
                
                #--- csvRow ---                        #float/str() = no diff.
                csvRow = [dateTime, li_open[i], li_high[i], li_low[i], li_close[i], li_volume[i],
                          0,0,li_sma[i],li_ema[i],0,0] 
                writer.writerow(csvRow) #x,x,.. ->0,0,..

        # Display the retrieved data
            #print("close: ", li_close)

        # Store the stock-name history
        stockNames.append(f"{sym}_{rndStr}")

        # Start again
        isAgain = False
        print("Get more? (y or n): ", end="")
        z = input()
        if z == "y":
            isAgain = True 
            rnd += 1
            print("--------------------------------")
    except:
        print("Something wrong, check the source code!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

# End of getting the data
print("Here are the stocks & rounds: ")
for i in stockNames:
    print("-> ", i)


# #-#-#-#-# Visualization Part #-#-#-#-#
isAgain = True
while isAgain == True :
    try:
        print("Type <stock>_<round> to be visualized: ", end="")
        out = input()
        
# >>>>>> Open that file -> Visualize call method & send param in

        print("Get more? (y or n): ", end="")
        again = input()
        if again == "y":
            isAgain = True
            print("--------------------------------")
        elif again == "n":
            isAgain = False
        else:
            isAgain = False
            print("Invalid input!")
    except:
        print("Something wrong, check the source code!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        
print("=======================================")


""" out (dictionary (API response))
[{
'lastSequence': x/[..],
'time': [..],
'open': [..],
'high': [..],
'low': [..],
'close': [..],
'volume': [..],
'value': [..]
}]
"""
