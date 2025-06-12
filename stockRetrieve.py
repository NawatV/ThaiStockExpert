# ----- SETTRADE_V2 -----
import settrade_v2
from settrade_v2 import Investor
import csv
from datetime import datetime
# ----- Operation ----- 
import numpy as np
import os

# ========= Get & store stock's history data to the assigned csv -> Ready to visualize with indicators |
#           Unavai. to 'Start-End' for m(min) Loop | +Up/Low Bands +RSI |
#           Call func. | Handle input errors (all nec.) | Data struc. changed | Done lower/upper
#           def getRSDfn_list() | show indicators w/ numP | ** Multi-numPs & bugs fixed
#           *** X(=tmp): try-except =================


# #-#-#-#-# Getting & Storing Part #-#-#-#-# 
# Functions
# --- SMA = (Sum of (closing) prices over a period) / (No.of time periods) ---
def getSMAlist_numP(numP, li_close):
    dayNum = 1
    li_sma_numP = []
    for i in range(len(li_close)):
        if dayNum >= numP:
            sumP = 0
            for j in range(dayNum-numP, dayNum, 1):
                sumP += float(li_close[j])
            sma = sumP/numP
            li_sma_numP.append(sma) #Append sma
        else:                
            li_sma_numP.append("") #Append null using ""/None
        dayNum += 1
    return li_sma_numP

#--- EMA = (Current (closing) price * Multiplier) + (Previous EMA * (1 - Multiplier)) ---
def getEMAlist_numP(numP, li_close, li_sma_numP):
    dayNum = 1
    prevEMA = None
    li_ema_numP = []
    for i in range(len(li_close)):
        if dayNum == numP:
            #--- To get 'ema = prevEMA' ---
            sumP = 0
            for j in range(dayNum-numP, dayNum, 1):
                sumP += float(li_close[j])
            sma = sumP/numP
            prevEMA = sma
            ema = prevEMA
            #------------------------------
            li_ema_numP.append(ema) #Append 1st ema 
        elif dayNum > numP:
            #--- emaMultiplyer = 2 / (No.of time periods + 1)
            emaMultiplyer = 2/(numP + 1) 
            ema = (float(li_close[i])*emaMultiplyer) + (prevEMA*(1-emaMultiplyer))
            prevEMA = ema #Update prevEMA 
            li_ema_numP.append(ema) #Append ema
        else:                
            li_ema_numP.append("") #Append null using ""/None
        dayNum += 1
    return li_ema_numP

# --- Upper Band = SMA + k*std (k=2) ---
def getUpperBandList_numP(numP, li_close, li_sma_numP):
    dayNum = 1
    li_up_numP = []
    for i in range(len(li_close)):
        if dayNum >= numP:
            sumP = 0
            stdS = []
            for j in range(dayNum-numP, dayNum, 1):
                stdS.append(float(li_close[j]))
            #--- Get Upper Band ---
            std = np.std(stdS, ddof=1) #Sample std deviation
            up = li_sma_numP[dayNum-1] + (2*std)
            li_up_numP.append(up) #Append up
        else:                
            li_up_numP.append("") #Append null using ""/None
        dayNum += 1
    return li_up_numP

# --- Lower Band = SMA - k*std (k=2) ---
def getLowerBandList_numP(numP, li_close, li_sma_numP):
    dayNum = 1
    li_down_numP = []
    for i in range(len(li_close)):
        if dayNum >= numP:
            sumP = 0
            stdS = []
            for j in range(dayNum-numP, dayNum, 1):
                stdS.append(float(li_close[j]))
            #--- Get Lower Band ---
            std = np.std(stdS, ddof=1) #Sample std deviation
            down = li_sma_numP[dayNum-1] - (2*std)
            li_down_numP.append(down) #Append down
        else:                
            li_down_numP.append("") #Append null using ""/None
        dayNum += 1        
    return li_down_numP

# --- RSI =100−(100/(1+RS)) ---
def getRSIlist_numP(numP, li_close): #if 14-day RSI -> numP=14, starts at day 15
    li_rsi_numP = []
    for i in range(len(li_close)):
        if i >= numP:
            gains = 0.0
            losses = 0.0
            for j in range(i-numP+1, i+1): #if 14-day RSI -> (1,15,1) -> j= 1,2,..14
                                           #-> ele no.2.. ele no.15
                try:
                    diff = float(li_close[j]) - float(li_close[j-1])
                    if diff >= 0: 
                        gains += diff
                    else:
                        losses -= diff
                except:
                    print("Something wrong about calculating the RSI")
                    continue
            avgGain = gains / numP     #X: avg_gain = gain.rolling(window= numPeriod).mean()
            avgLoss = losses / numP
            #--- Case avgLoss = 0 ---
            if avgLoss == 0:
                li_rsi_numP.append(100) #if no losses
            else:
                rs = avgGain / avgLoss
                rsi = 100 - (100 / (1 + rs))
                li_rsi_numP.append(rsi) #Append rsi
        else:
            li_rsi_numP.append("") #Append null using ""/None
    return li_rsi_numP

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
#-----------------------------


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
        li_numPeriod = []
        #--- up to each numPeriod ---
        li_up_all = []          
        li_down_all = []
        li_sma_all = []
        li_ema_all = []
        li_rsi_all = []

        # Creates indicators
        while True:
            try:
                print("SMA,EMA,Upper&Lower,RSI - NO.of Periods")
                print("1 or Multi (e.g., 20 or 17,25): ", end="")
                numPeriod_inputs = input()

                if "," in numPeriod_inputs:
                    #--- Multi values in 'li_numPeriod' ---
                    numPeriods_str =  numPeriod_inputs.split(",")
                    for numP in numPeriods_str:
                        numP = int(numP) 
                        li_numPeriod.append(numP)
                    #--- Fill the rest with "" ---
                    for i in range(len(li_close) - len(li_numPeriod)): ## required !!
                        li_numPeriod.append("")
                        
                    break
                else:
                    #--- Only 1 value in 'li_numPeriod' ---
                    numP = int(numPeriod_inputs)
                    li_numPeriod.append(numP)
                    #--- Fill the rest with "" ---
                    for i in range(len(li_close) - len(li_numPeriod)): ## required !!
                        li_numPeriod.append("")
                        
                    break
            except:
                print("Invalid input! Try again.")

        # Get all indicators for every <numP> in 'li_numPeriod' -in-> each indicator's 'li_<indicator>_all'
        # 'li_<ind.>_all' keeps 'li_<ind.>_numP'no.1, no.2,...
        # X [no need]: dict= {'numP': li_<ind.>_numP}
        for numP in li_numPeriod:
            if str(numP) != "": #"" != None
                                #Handle "" in 'li_numPeriod' here before calling the funcs. below
              # --- Get all indicators for each <numP> ---
                # === SMA ===
                ## getSMAlist_numP(numP) -added to-> 'li_sma_numP' --> 1 col 'li_sma_numP' in csv
                li_sma_numP = getSMAlist_numP(numP, li_close)
                li_sma_all.append(li_sma_numP)

                # === EMA ===
                ## getEMAlist_numP(numP) -added to-> 'li_ema_numP' --> 1 col 'li_ema_numP' in csv
                li_ema_numP = getEMAlist_numP(numP, li_close, li_sma_numP)
                li_ema_all.append(li_ema_numP)

                # === Upper & Lower Bands ===
                
                ## getUpperBandList_numP(numP) -added to-> 'li_up_numP' --> 1 col 'li_up_numP' in csv
                li_up_numP = getUpperBandList_numP(numP, li_close, li_sma_numP)
                li_up_all.append(li_up_numP)
                
                ## getLowerBandList_numP(numP) -added to-> 'li_down_numP' --> 1 col 'li_down_numP' in csv
                li_down_numP = getLowerBandList_numP(numP, li_close, li_sma_numP)
                li_down_all.append(li_down_numP)

                # === RSI ===
                ## getRSIlist_numP(numP) -added to-> 'li_rsi_numP' --> 1 col 'li_rsi_numP' in csv
                li_rsi_numP = getRSIlist_numP(numP, li_close)
                li_rsi_all.append(li_rsi_numP)


    # +Other Indicators <<<<<<<<<<<<<<<<<<<<<<<<<<<
            
        li_volume = res["volume"]
        li_value = res["value"]

      # Create .txt & print to it
        rndStr = str(rnd)
        #res_txtFile = f"C://Users//LENOVO//Desktop//thai_stock_expert//output//{rndStr}_{sym}.txt" #Must use
                # Opening the file in write mode ("w") will create the file if it doesn't exist,
                # or overwrite it if it does
        #with open(res_txtFile, "w") as file:
            #file.write(f"lastSequence: {li_lastSequence} \n") & the other li_xxx

      #===== Create .csv & print to it =====    ##### PATH !!!
        csvHeader = ['li_time','li_open','li_high','li_low','li_close','li_volume', 'li_numPeriod'] ## required !!
        #--- Create headers based on 'li_numPeriod' ---
        ## li_sma_numP
        for numPeriod in li_numPeriod: #[int,..,""]
            if str(numPeriod) != "":
                csvHeader.append(f'li_sma_{numPeriod}')
        ## li_ema_numP
        for numPeriod in li_numPeriod:
            if str(numPeriod) != "":
                csvHeader.append(f'li_ema_{numPeriod}')
        ## li_up_numP
        for numPeriod in li_numPeriod:
            if str(numPeriod) != "":
                csvHeader.append(f'li_up_{numPeriod}')
        ## li_down_numP
        for numPeriod in li_numPeriod:
            if str(numPeriod) != "":
                csvHeader.append(f'li_down_{numPeriod}')
        ## li_rsi_numP
        for numPeriod in li_numPeriod:
            if str(numPeriod) != "":
                csvHeader.append(f'li_rsi_{numPeriod}')

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
                
                #===== csvRow =====                        #float/str() = no diff.
                csvRow = [dateTime, li_open[i], li_high[i], li_low[i], li_close[i], li_volume[i], li_numPeriod[i]]
                #--- Add values based on 'li_numPeriod' ---
                ## li_sma_all
                for j in range(len(li_numPeriod)):
                    if str(li_numPeriod[j]) != "":
                        csvRow.append(li_sma_all[j][i])
                ## li_ema_all
                for j in range(len(li_numPeriod)):
                    if str(li_numPeriod[j]) != "":
                        csvRow.append(li_ema_all[j][i])
                ## li_up_all
                for j in range(len(li_numPeriod)):
                    if str(li_numPeriod[j]) != "":
                        csvRow.append(li_up_all[j][i])
                ## li_down_all
                for j in range(len(li_numPeriod)):
                    if str(li_numPeriod[j]) != "":
                        csvRow.append(li_down_all[j][i])
                ## li_rsi_all
                for j in range(len(li_numPeriod)):
                    if str(li_numPeriod[j]) != "":
                        csvRow.append(li_rsi_all[j][i])

                writer.writerow(csvRow)
            
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
