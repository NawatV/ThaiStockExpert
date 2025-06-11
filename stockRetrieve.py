# ----- SETTRADE_V2 -----
import settrade_v2
from settrade_v2 import Investor
import csv
from datetime import datetime
# ----- Operation ----- 
import numpy as np
import os

# ========= Get & store stock's history data to the assigned csv -> Ready to visualize with indicators |
#           Unavai. to 'Start-End' for m(min) Loop | X(tmp): try-except | +Up/Low Bands +RSI |
#           Call func. | Handle input errors (all nec.) | Data struc. changed | Done lower/upper
#           def getRSDfn_list() | | +li_numPeriod =================

# #-#-#-#-# Getting & Storing Part #-#-#-#-# 
# Functions
# --- Upper Band = SMA + k*std (k=2) ---
def getUpperBandValue(sma, stdS):
    std = np.std(stdS, ddof=1) #Sample std deviation
    up = sma + 2*std
    return up
# --- Lower Band = SMA - k*std (k=2) ---
def getLowerBandValue(sma, stdS):
    std = np.std(stdS, ddof=1) #Sample std deviation
    down = sma - (2*std)
    return down  

# --- RSI =100−(100/(1+RS)) ---
def getRsi(li_close, numP, numPeriod): #if 14-day RSI -> li,15,14
    gains = 0
    losses = 0
    for j in range(numP-numPeriod, numP, 1): #if 14-day RSI -> 1,15,1 (=ele no.2, ele no.16, +1)
        if j < numP: #Still does when the last ele isn't found!
            diff = float(li_close[j] - li_close[j-1])
            if diff >= 0:
                gains += diff
            else:
                losses += abs(diff)
    avgGain = gains / numPeriod     #X: avg_gain = gain.rolling(window= numPeriod).mean()
    avgLoss = losses / numPeriod
    #--- Case avgLoss = 0 ---
    if avgLoss == 0:
        return ""
    else:
        rs = avgGain / avgLoss
        rsi = 100 - (100 / (1 + rs))
    return rsi

def getRSDfn_list(): ##### PATH !!!
    RSDfn_path = "C://Users//LENOVO//Desktop//thai_stock_expert//output//"
    RSDfn_list = [
        fileName for fileName in os.listdir(RSDfn_path)
            if os.path.isfile(os.path.join(RSDfn_path, fileName))
                # Filter out 'RSDfn_path' of 'RSDfn_path//fileName' -> @'fileName'
            # if @'fileName' exists (== True) in 'a list of all files in 'RSDfn_path'
            # then fileName = @'fileName' -> RSDfn_list.append(fileName)
            # and keep doing until all the files in 'RSDfn_path' are met 
                 ]
    return RSDfn_list

def getStockData():
    # Initialize an Investor object with your credentials
    investor = Investor(app_id="", app_secret="",
                        broker_id="SANDBOX", app_code="SANDBOX", is_auto_queue = False)
    # Access the market data
    market = investor.MarketData()


    # --- Loop ---
    isAgain = True
    rnd = 1
    stockNames = []
    while isAgain == True :
        #try:
        # Get candle stick | *** Latest data = 3 working days before | Unavai.'15m'
        print("Beware of error due to improper input!")
        print("Stock Name (Case-Insen):", end=" ")
        sym = input()
        sym = sym.lower()
        
        print("Interval -1d(daily), 1w(weekly), 1M(monthly),")  # Internal's description
        print("1,3,5,10,30,60,120,240m (per..minute(s)): ", end="") # Unavai. to 'Start-End'
        itv = input()
        if itv in ["1d","1w","1M"]:
            #--- Get lim after 'if itv' ---
            print("Candle Amount (<=1000):", end=" ")
            lim = input()
            try:
                if int(lim) > 1000 or int(lim) < 1:
                    print("Input out of 1-1000! Start again.")
                    continue #Go back to while #X: break
            except:
                print("Invalid input! Start again.")
                continue
            #------------------------------
            print("Start-End Date? (y or n): ", end="")
            isDate = input()
            if isDate == "y":
                #--- Start-End Date ---
                print("Start Date (DD/MM/YYYY): ", end="")
                sd = input()
                try:
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
                except:
                    print("Invalid input! Start again.")
                    continue #Go back to while #X: break
                #----------------------
                res = market.get_candlestick(
                symbol=sym,
                interval=itv,   #1m, 3m, 5m, 10m, 15m, 30m, 60m, 120m, 240m, 1d, 1w, 1M
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
                print("Invalid input! Start again.")
                continue
        elif itv in ["1m","3m","5m","10m","30m","60m","120m","240m"]:
            #--- Get lim after 'if itv' ---
            print("Candle Amount (<=1000):", end=" ")
            lim = input()
            try:
                if int(lim) > 1000 or int(lim) < 1:
                    print("Input out of 1-1000! Start again.")
                    continue
            except:
                print("Invalid input! Start again.")
                continue
            #------------------------------
            res = market.get_candlestick(symbol=sym, interval=itv, limit=lim, normalized=True)    
        else:
            print("Invalid input! Start again.")
            continue  

        # Store in list
        li_lastSequence = res["lastSequence"]
        li_time = res["time"]
        li_open = res["open"]
        li_high = res["high"]
        li_low = res["low"]
        li_close = res["close"]
        li_numPeriod = [] #<<<<<<<<<<<<<<<<<<<<<<<<<<<
        li_up = []
        li_down = []
        li_sma = []
        li_ema = []
        li_rsi = []

        # Creates indicators
        while True:
            try:
                print("SMA,EMA,Upper&Lower Band - NO.of Periods: ", end="")
                numPeriod = int(input())
                #--- Only 1 value in 'li_numPeriod' ---
                li_numPeriod.append(numPeriod) #<<<<<<<<<<<<<<<<<<<<<<<<<<<
                for i in range(len(li_close)-1):
                    li_numPeriod.append("")
                #--------------------------------------
                break
            except:
                print("Invalid input! Try again.")
                
        #--- SMA = (Sum of (closing) prices over a period) / (No.of time periods) ---
        numP = 1
        prevEMA = None
        for i in range(len(li_close)):
            if numP >= numPeriod:
                sumP = 0
                stdS = []
                for j in range(numP-numPeriod, numP, 1):
                    sumP += float(li_close[j])
                    stdS.append(float(li_close[j]))
                sma = sumP/numPeriod
                li_sma.append(sma) #Append SMA
                #--- Get prevEMA ---
                if prevEMA == None:
                    prevEMA = sma
        #--- Get Upper Band ---
                up = getUpperBandValue(sma, stdS)
                li_up.append(up)
        #--- Get Lower Band ---
                down = getLowerBandValue(sma, stdS)
                li_down.append(down)
        #--- Get RSI ---
                if numP > numPeriod: #if 14-day RSI, starts at ele 15
                    rsi = getRsi(li_close, numP, numPeriod)
                    li_rsi.append(rsi)
                else:
                    li_rsi.append("")
                    
    #>>>>>>>>>>>>>>>>>
                
            else:                
                li_sma.append("") #Append null using ""/None
                li_up.append("")
                li_down.append("")
                li_rsi.append("")

    #>>>>>>>>>>>>>>>>>
                
            numP += 1
            
        #--- EMA = (Current (closing) price * Multiplier) + (Previous EMA * (1 - Multiplier)) ---
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

    #>>>>>> +Others ?
            
        li_volume = res["volume"]
        li_value = res["value"]

        # Create .txt & print to it
        rndStr = str(rnd)
        #res_txtFile = f"C://Users//LENOVO//Desktop//thai_stock_expert//output//{rndStr}_{sym}.txt" #Must use
                # Opening the file in write mode ("w") will create the file if it doesn't exist,
                # or overwrite it if it does
        #with open(res_txtFile, "w") as file:
            #file.write(f"lastSequence: {li_lastSequence} \n") & the other li_xxx

        # Create .csv & print to it     ##### PATH !!!
        csvHeader = ['li_time','li_open','li_high','li_low','li_close','li_volume', 'li_numPeriod',
                     'li_up', 'li_down','li_sma','li_ema','li_rsi']
        res_csvFile = f"C://Users//LENOVO//Desktop//thai_stock_expert//output//{rndStr}_{sym}.csv"
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
                csvRow = [dateTime, li_open[i], li_high[i], li_low[i], li_close[i], li_volume[i], li_numPeriod[i],
                          li_up[i], li_down[i], li_sma[i], li_ema[i], li_rsi[i]] 
                writer.writerow(csvRow) #x,x,.. ->0,0,..
            
        # Display the retrieved data
            #print("close: ", li_close)

        # Store the stock-name history
        stockNames.append(f"{rndStr}_{sym}")

        # Start again
        while True:
            print("Get more? (y or n): ", end="")
            again = input()
            if again == "y":
                isAgain = True 
                rnd += 1
                print("------------------------------------")
                break # Continue to get more
            elif again == "n":
                isAgain = False
                break
            else:
                print("Invalid input! Try again.")
            
        #except:
        #    print("Something wrong, check the source code!")
        #    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    # End of getting the data
    print("================================")
    print("Here are the stocks & rounds: ")
    for i in stockNames:
        print("----> ", i)
    print("================================")
            
# ================= END OF PROGRAM =================
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
