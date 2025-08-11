# ----- SETTRADE_V2 -----
import settrade_v2
from settrade_v2 import Investor
import csv
from datetime import datetime
# ----- Operation ----- 
import numpy as np
import os
import numbers
import pandas as pd
# ----- Related .py -----
import stockScraper as stScr

# ========= Get & store stock's history data to the assigned csv -> Ready to visualize with indicators |
#           Unavai. to 'Start-End' for m(min) Loop | +Up/Low Bands +RSI |
#           Call func. | Handle input errors (all nec.) | Data struc. changed | Done lower/upper
#           def getRSDfn_list() | Show indicators w/ numP
#           ** Multi-numPs & bugs fixed | +MACD,Signal,His | +Opti.del func.('rnd_fileNameWOtype')
#           | +Exit opt. | Check isUniPath before saving .csv | Optimized the code | +multi-Volatility | +NP
#           | +input.strip() | +sharp ratio | +call func.in stScr |  
#           | 1 web scr/act opening | +Warning 'SET's API' | Fixed 'valEr: 1' at stVis 
#
#            Big try-except (compre.) =================


# #-#-#-#-# Getting & Storing Part #-#-#-#-# 
# Functions
# --- list_numP: SMA = (Sum of (closing) prices over a period) / (No.of time periods) ---
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

#--- list_numP: EMA = (Current (closing) price * Multiplier) + (Previous EMA * (1 - Multiplier)) ---
def getEMAlist_numP(numP, li_close, isForSignal):
    dayNum = 1
    prevEMA = None
    li_ema_numP = []
    for i in range(len(li_close)):
        try: #To handle EMA(numP=9) of MACD: ->except ->Append null using ""/None 
            if dayNum == numP and isForSignal == False:
                #--- To get 'ema = prevEMA' ---
                sumP = 0
                for j in range(dayNum-numP, dayNum, 1):
                    sumP += float(li_close[j])    
                sma = sumP/numP
                prevEMA = sma
                ema = prevEMA
                #------------------------------
                li_ema_numP.append(ema) #Append 1st ema 
            elif dayNum > numP and isForSignal == False:                
                #--- emaMultiplyer = 2 / (No.of time periods + 1)
                emaMultiplyer = 2/(numP + 1) 
                ema = (float(li_close[i])*emaMultiplyer) + (prevEMA*(1-emaMultiplyer))
                prevEMA = ema #Update prevEMA 
                li_ema_numP.append(ema) #Append ema
            #-------------- For signal only -------------------------
            elif isForSignal == True:                
                if dayNum == 34:
                    #li_macd (= li_close now) starts 1st ele at li_macd[25]
                    #-> EMA(num=9) of MACD will start 1st ele at li_macd[33]
                    #--- To get 'ema = prevEMA' ---
                    sumP = 0
                    for j in range(25, dayNum, 1):
                        sumP += float(li_close[j])
                    sma = sumP/numP
                    prevEMA = sma
                    ema = prevEMA
                    #------------------------------
                    li_ema_numP.append(ema) #Append 1st ema 
                elif dayNum > 34:                    
                    #--- emaMultiplyer = 2 / (No.of time periods + 1)
                    emaMultiplyer = 2/(numP + 1) 
                    ema = (float(li_close[i])*emaMultiplyer) + (prevEMA*(1-emaMultiplyer))
                    prevEMA = ema #Update prevEMA 
                    li_ema_numP.append(ema) #Append ema
                else:                    
                    li_ema_numP.append("")
            #--------------------------------------------------------
            else:
                li_ema_numP.append("") #Append null using ""/None
            dayNum += 1
        except:
            print("!! Something wrong while 'getEMAlist_numP' is being processed !!")
            continue
    return li_ema_numP

# --- [Optimized] list_numP: Upper/Lower Band = SMA +/- k*std (k=2) ---
def getBandList_numP(pos, numP, li_close, li_sma_numP):
    dayNum = 1
    li_pos_numP = []
    for i in range(len(li_close)):
        if dayNum >= numP:
            sumP = 0
            stdS = []
            for j in range(dayNum-numP, dayNum, 1):
                stdS.append(float(li_close[j]))
            #--- Get Upper/Lower Band ---
            std = np.std(stdS, ddof=1) #Sample std deviation
            li_pos_numP.append(
                li_sma_numP[dayNum-1] + (2*std) if pos == "upper"        #Append an Upper Band val
                else li_sma_numP[dayNum-1] - (2*std) if pos == "lower"   #Append a Lower Band val
                else ""        )
        else:
            li_pos_numP.append("") #Append null using ""/None
        dayNum += 1
    return li_pos_numP

# --- list_numP: RSI =100−(100/(1+RS)) ---
def getRSIlist_numP(numP, li_close): #if 14-day RSI -> numP=14, it starts at day 15
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

#--- list: MACD = EMA(numP=12) - EMA(numP=26) ---
def getMACDlist(li_close):
    #--- list: EMA 12 & 26 ---
    li_ema_12 = getEMAlist_numP(12, li_close, False)
    li_ema_26 = getEMAlist_numP(26, li_close, False)
    # Create MACD
    li_macd_tmp = []
    for i in range(len(li_close)):
        if isinstance(li_ema_12[i], numbers.Number) and isinstance(li_ema_26[i], numbers.Number):    
            macd = li_ema_12[i] - li_ema_26[i]
            li_macd_tmp.append(macd) #Append macd 
        else:
            li_macd_tmp.append("") #Append null using ""/None
    return li_macd_tmp 

#--- list: Signal = EMA(numP=9) of MACD ---
def getSignalList(li_macd):
    # Create signal
    #--- li_macd_wnon <- ["" -> None] ---
    li_macd_wnon = [None if val == "" else val for val in li_macd] #Faster & 'easier to read' 
    li_signal_tmp = getEMAlist_numP(9, li_macd_wnon, True)    
    return li_signal_tmp

#--- list: Histogram = MACD - Signal ---
def getHistogramList(li_close, li_macd, li_signal):
    # Create histogram  | X: for...
    arr_macd = np.array(li_macd, dtype=object)                  #Convert to array
    arr_signal = np.array(li_signal, dtype=object)              #if no dtype=obj, all ele.-auto-> str
    arr_macd_wzero = np.array([float(x) if x != "" else 0 for x in arr_macd])     #Tmp: "" -> 0
    arr_signal_wzero = np.array([float(x) if x != "" else 0 for x in arr_signal]) #Tmp: "" -> 0
    arr_histogram_wzero = arr_macd_wzero - arr_signal_wzero     #Subtract
    arr_histogram = np.array(arr_histogram_wzero, dtype=object) #0 -> ""
    arr_histogram[arr_histogram == 0.0] = ""                    #if no dtype=obj, all ele.-auto-> str
    li_histogram = arr_histogram.tolist()                       #Convert to list
    #--- ele. 'MACD - 0' -> "" --- 
    for i in range(len(li_histogram)):
        if i < 33: #EMA(num=9) of MACD will start 1st ele at li_macd[33], so does His.(at li_his.[33])
            li_histogram[i] = ""

    return li_histogram

#--- 2ND VIS : list: 2. Volatility = σ_t = std([R_t-n+1],..,[R_t]) //Sample Diviation (which /n-1) ---
def getVolatilityList(numP, li_close):
    # Create 'df'
    dic_close = {"close": li_close}
    df = pd.DataFrame(dic_close)
    # 1. Cal.& Add 'daily change (%/100)' = R_t = ([P_t] - [P_t-1]) / [P_t-1]	
    df["dayChange"] = df["close"].pct_change() #-> [NaN, 0.xx, 0.yy,..]
    # 2. Cal & Add 'numP-day rolling volatility'    
    df[f"volatility_{numP}"] = df["dayChange"].rolling(window = numP).std()     
    # Add it to 'li_volatility_numP' & Change nan to "" | X: ' "" at 1st '
    li_volatility_numP = df[f"volatility_{numP}"].tolist()
    li_volatility_numP = ["" if pd.isna(val) else val for val in li_volatility_numP]
    
    return li_volatility_numP 

#--- 2ND VIS : list: Normalized Price = P_t/P_0 ---
def getNPlist(li_close):
    # Create 'df'
    dic_close = {"close": li_close}
    df = pd.DataFrame(dic_close)
    # Cal.& Add 'Normalized Price'
    df["np"] = df["close"] / df["close"].iloc[0] #-> [1, P_2/P_0, P_3/P_0,..] 
    # Add it to 'li_np'
    li_np = df["np"].tolist()
    
    return li_np

#--- 2ND VIS : list: Sharp Ratio_t = ([Mean(R_t−n+1:t)] - R_f) / Volatility ---
def getSharpList(numP, li_close, R_f):
    # Create 'df'
    dic_close = {"close": li_close}
    df = pd.DataFrame(dic_close)
    # 1. Cal.& Add 'daily change (%/100)' = R_t = ([P_t] - [P_t-1]) / [P_t-1]	
    df["dayChange"] = df["close"].pct_change()                     #-> [NaN, 0.xx, 0.yy,..]
    # 2. Cal '[Mean(R_t−n+1:t)]'
    dayChange_mean = df["dayChange"].rolling(window = numP).mean() #-> [NaN, 0.xx, 0.yy,..]
    # 3. Get R_f
    R_f = R_f
    # 4. Cal & Add 'numP-day rolling volatility'                    #-> [NaN, NaN,.., 0.xx (day numP+1),..]
    volatility_rolling = df[f"volatility_{numP}"] = df["dayChange"].rolling(window = numP).std() 
    # 5. Cal & Add 'numP-day rolling sharp' ## Correct - Convenient! | ## Start at 1st day of 'li_vola.'
    df[f"sharp_{numP}"] = (dayChange_mean - R_f) / volatility_rolling
    # 6. Add it to 'li_sharp_numP' & Change nan to "" | X: ' "" at 1st '
    li_sharp_numP = df[f"sharp_{numP}"].tolist()
    li_sharp_numP = ["" if pd.isna(val) else val for val in li_sharp_numP]
    
    return li_sharp_numP 
#-------------------------------------------------------------

def getRSDpath_list(purpose): ##### PATH !!!
    RSD_dir = "C://Users//LENOVO//Desktop//thai_stock_expert//output//"
    if purpose == "view":
        RSDfn_list = [  #A concise & eff.way to create a new list. | Already familiar with
            fileName
            for fileName in os.listdir(RSD_dir)
            if os.path.isfile(os.path.join(RSD_dir, fileName))
                     ]
        return RSDfn_list   #Get only "<RSD file name>.<file type>"
    elif purpose == "del":
        RSDpath_list = [
            os.path.join(RSD_dir, fileName)
            for fileName in os.listdir(RSD_dir)
            if os.path.isfile(os.path.join(RSD_dir, fileName))
                     ]        
        return RSDpath_list #Get "RSD's full path"
    else:
        print("Something wrong while 'getRSDpath_list' is being processed !!")

def delRSDpath():
    delStocks = []
    RSDpath_list = getRSDpath_list("del")
    # Optimize using dict
    RSDpath_dic = {}
    for RSDpath in RSDpath_list:
        RSD_dir, fileName = os.path.split(RSDpath) #Split to extract 'fileName.fileType'
        fileNameWOtype, fileType = fileName.split(".")
        RSDpath_dic[fileNameWOtype] = RSDpath
    while True:
        print("Delete all? (y, n, or Exit (exit)): ", end="")
        delAll = input().strip().lower() #Remove space & lower before
        if delAll == "y":
            for pathKey in RSDpath_dic: #pathKey = key | X: .keys()
                os.remove(RSDpath_dic[pathKey])
                delStocks.append(pathKey)
            printStockNames(delStocks)
        elif delAll == "n":
            print("Type the chosen one(s)")
            print("i.e., <round>_<stock name> or <r>_<sn>, <r>_<sn>,..: ", end="")   
            #--- Invalid input here is OK ---
            delFnWOtype_inputs = input().strip().lower()
            if "," in delFnWOtype_inputs:
                li_delFnWOtype = [s.strip() for s in delFnWOtype_inputs.split(",")] #X:'for' in 'for' (O(n^2))
                for key in li_delFnWOtype: #O(n) - for in list
                    if key in RSDpath_dic: #O(1) - search in dict
                        os.remove(RSDpath_dic[key])
                        delStocks.append(key)
            else:
                key = delFnWOtype_inputs 
                if key in RSDpath_dic:     #O(1) - search in dict 
                    os.remove(RSDpath_dic[key])
                    delStocks.append(key)

            printStockNames(delStocks)
            
        elif delAll == "exit":
            return
        else:
            print("Invalid input! Please try again.")
            print("------------------------------------")
            continue
        break

def getLi_numPeriod(numPeriod_inputs, li_close):
    li_numPeriod = []
    if "," in numPeriod_inputs:
        #--- Multi values in 'li_numPeriod' ---
        li_numPeriod = [int(numP.strip()) #A concise & eff.way to create a new list
                        for numP in numPeriod_inputs.split(",") if numP.strip()]
        #--- Fill the rest with "" ---
        li_numPeriod += [""] * (len(li_close) - len(li_numPeriod)) ## Required !! | Better mem.allo.eff. 
    else:
        #--- Only 1 value in 'li_numPeriod' ---
        numP = int(numPeriod_inputs.strip())
        li_numPeriod.append(numP)
        #--- Fill the rest with "" ---
        li_numPeriod += [""] * (len(li_close) - len(li_numPeriod)) ## Required !!
    return li_numPeriod

def printStockNames(li_stockName):
    print("================================")
    print("Here are the touched <round>_<stock name>(s): ")
    for stockName in li_stockName:
        print("----> ", stockName)
    print("================================")
#-------------------------------------------------------------


def getStockData():

    # Scrape annual R_f: https://www.thaibma.or.th/ > Gov.Yield Curve > 3 Month: annual R_f
        #annual R_f (%/100) -[/252]-> R_f | ### stockScraper.py
    percent_ann_R_f = stScr.scrape_percent_ann_R_f("3M")
    R_f = (float(percent_ann_R_f)/100)/252         #=Daily 

    # Initialize an Investor object with your credentials
    investor = Investor(app_id="", app_secret="",
                        broker_id="SANDBOX", app_code="SANDBOX", is_auto_queue = False)
    # Access the market data
    market = investor.MarketData()

    # --- Loop ---
    isAgain = True
    stockNames = []
    while isAgain == True :
        try:
            rnd = 1
            # Get candle stick | *** Latest data = 3 working days before | Unavai.'15m'
            print("//// SET's API doesn't always return up-to-date data & it's occasionally inaccessible including around 4:15-5:15am (GMT+7) ////")
            print("     The amount of the data rows it provides has been occasionally changable ////")
            print("//// Please beware of the last dataRow, remove it if incontinuous and/or inaccurate ////")
            print("Stock Name (Case-Insen) OR Exit (exit):", end=" ")
            sym = input()
            sym = sym.strip().lower()
            #--- Exit before ---
            if sym == "exit":
                printStockNames(stockNames)
                return
            
            print("Interval -1d(daily), 1w(weekly), 1M(monthly),")  # Internal's description
            print("1,3,5,10,30,60,120,240m (per..minute(s)): ", end="") # Unavai. to 'Start-End'
            itv = input().strip()
            if itv in ["1d","1w","1M"]:
                #--- Get lim after 'if itv' ---
                print("Candle Amount (>=3 & <=1000):", end=" ")
                lim = input().strip()
                try:
                    if int(lim) > 1000 or int(lim) < 3:
                        print("Input out of 3-1000! Please try again.")
                        continue #Go back to while #X: break
                except:
                    print("Invalid input! Please try again.")
                    continue
                #------------------------------
                print("Start-End Date? (y or n): ", end="")
                isDate = input().strip()
                if isDate == "y":
                    #--- Start-End Date ---
                    print("Start Date (DD/MM/YYYY): ", end="")
                    sd = input().strip()
                    try:
                        sdS = sd.split("/")
                        y = sdS[2]
                        m = sdS[1]
                        d = sdS[0]
                        startD = f"{y}-{m}-{d}T00:00"
                        print("End Date (DD/MM/YYYY): ", end="")
                        ed = input().strip()
                        edS = ed.split("/")
                        y = edS[2]
                        m = edS[1]
                        d = edS[0]
                        endD = f"{y}-{m}-{d}T23:59"
                    except:
                        print("Invalid input! Please try again.")
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
                lim = input().strip()
                try:
                    if int(lim) > 1000 or int(lim) < 1:
                        print("Input out of 1-1000! Start again.")
                        continue
                except:
                    print("Invalid input! Please try again.")
                    continue
                #------------------------------
                res = market.get_candlestick(symbol=sym, interval=itv, limit=lim, normalized=True)    
            else:
                print("Invalid input! Please try again.")
                continue  

            # Store in list
            li_lastSequence = res["lastSequence"]
            li_time = res["time"]
            li_open = res["open"]
            li_high = res["high"]
            li_low = res["low"]
            li_close = res["close"]
            li_numPeriod = []
            li_macd = []
            li_signal = []
            li_histogram = []
            #--- up to each numPeriod ---
            li_up_all = []          
            li_down_all = []
            li_sma_all = []
            li_ema_all = []
            li_rsi_all = []
            #--- 2ND VIS ---
            li_np = []
            li_numPeriod_2 = []
            li_volatility_all = []
            li_sharp_all = []

            # Add 'numP' to 'li_numPeriod' for the indicators
            while True:
                try:
                    print("SMA,EMA,Upper&Lower,RSI - NO.of Periods")
                    print("1 or Multi (e.g., 20 or 17,25): ", end="")
                    numPeriod_inputs = input().strip()
                    li_numPeriod = getLi_numPeriod(numPeriod_inputs, li_close)

                    print("Volatility,Sharp Ratio - NO.of Periods (same format): ", end="")
                    numPeriod_2_inputs = input().strip()
                    li_numPeriod_2 = getLi_numPeriod(numPeriod_2_inputs, li_close)
                    break
                except:
                    print("Invalid input! Please try again.")

            # Get all indicators for every <numP> in 'li_numPeriod' -in-> each indicator's 'li_<indicator>_all'
            # 'li_<ind.>_all' keeps 'li_<ind.>_numP'no.1, no.2,...
            # X [no need]: dict= {'numP': li_<ind.>_numP}
            for numP in li_numPeriod:
                if str(numP) != "": #"" != None | Handle "" in 'li_numPeriod' here before calling the funcs. below
                  # --- Get all indicators for each <numP> ---
                    # === list_all: SMA ===
                    ## & like the rest: getSMAlist_numP(numP) -added to-> 'li_sma_numP' --> 1 col 'li_sma_numP' in csv
                    li_sma_numP = getSMAlist_numP(numP, li_close)
                    li_sma_all.append(li_sma_numP)

                    # === list_all: EMA ===
                    li_ema_numP = getEMAlist_numP(numP, li_close, False)
                    li_ema_all.append(li_ema_numP)

                    # === list_all: Upper & Lower Bands ===
                    ## Upper
                    li_up_numP = getBandList_numP("upper", numP, li_close, li_sma_numP)
                    li_up_all.append(li_up_numP)
                    ## Lower
                    li_down_numP = getBandList_numP("lower", numP, li_close, li_sma_numP)
                    li_down_all.append(li_down_numP)

                    # === list_all: RSI ===
                    li_rsi_numP = getRSIlist_numP(numP, li_close)
                    li_rsi_all.append(li_rsi_numP)

            # --- 2ND VIS ---
            for numP in li_numPeriod_2:
                if str(numP) != "":
                 # --- Get all indicators for each <numP> ---
                   # === list_all: Volatility ===
                    li_volatility_numP = getVolatilityList(numP, li_close)
                    li_volatility_all.append(li_volatility_numP)

                   # === list_all: Sharp Ratio ===
                    li_sharp_numP = getSharpList(numP, li_close, R_f)
                    li_sharp_all.append(li_sharp_numP)

        # +other indicators <<<<<<<<<<<<<<<<<<<<<<<<<<<
        
            #=== list: MACD ===
            li_macd = getMACDlist(li_close)
            #=== list: Signal ===
            li_signal = getSignalList(li_macd)
            #=== list: Histogram ===
            li_histogram = getHistogramList(li_close, li_macd, li_signal)

           #--- 2ND VIS ---
            li_np = getNPlist(li_close)
                
            li_volume = res["volume"]
            li_value = res["value"]

            rndStr = str(rnd)

          #===== Create .csv & print to it =====
            csvHeader = ['li_time','li_open','li_high','li_low','li_close','li_volume', 'li_numPeriod', ## Required !!
                         'li_numPeriod_2', 'li_macd', 'li_signal', 'li_histogram', 'li_np']           
            #--- Create headers based on 'li_numPeriod' ---
            ## li_sma_numP
            for numPeriod in li_numPeriod: #[int,..,""]
                if str(numPeriod) != "":
                    csvHeader.append(f'li_sma_{numPeriod}')
            ## li_ema_numP
            for numPeriod in li_numPeriod:
                if str(numPeriod) != "":
                    csvHeader.append(f'li_ema_{numPeriod}')
            ## Upper: li_up_numP
            for numPeriod in li_numPeriod:
                if str(numPeriod) != "":
                    csvHeader.append(f'li_up_{numPeriod}')
            ## Lower: li_down_numP
            for numPeriod in li_numPeriod:
                if str(numPeriod) != "":
                    csvHeader.append(f'li_down_{numPeriod}')
            ## li_rsi_numP
            for numPeriod in li_numPeriod:
                if str(numPeriod) != "":
                    csvHeader.append(f'li_rsi_{numPeriod}')

            # --- 2ND VIS ---
            ## li_volatility_numP
            for numPeriod in li_numPeriod_2:
                if str(numPeriod) != "":
                    csvHeader.append(f'li_volatility_{numPeriod}')
            ## li_sharp_numP
            for numPeriod in li_numPeriod_2:
                if str(numPeriod) != "":
                    csvHeader.append(f'li_sharp_{numPeriod}')

                            ##### PATH !!!
            uniPath = f"C://Users//LENOVO//Desktop//thai_stock_expert//output//{rndStr}_{sym}.csv"
            while True:
                if os.path.isfile(uniPath):
                    rnd += 1
                    rndStr = str(rnd)   ##### PATH !!!
                    uniPath = f"C://Users//LENOVO//Desktop//thai_stock_expert//output//{rndStr}_{sym}.csv" 
                else:
                    break
            res_csvFile = uniPath
            
          # [Optimized] From O((i*j)*5) to O(i*j)
            li_indiRow = [ [li[i] for li in
                              #3. Get li[0] = [sma_14_0, sma_20_0,..,rsi_20_0] which is indiRow 1
                              #      ,li[1] = [sma_14_1, sma_20_1,..,rsi_20_1] which is indiRow 2
                              #      ,...   
                           li_sma_all + li_ema_all + li_up_all + li_down_all + li_rsi_all + li_volatility_all
                           + li_sharp_all]
                              #2. Concat.(+), the result is
                                #[
                                #  [sma_14_0, sma_14_1, ..., sma_14_n],
                                #  [sma_20_0, sma_20_1, ..., sma_20_n],
                                #  ...
                                #  [vola._30_0, vola._30_1, ..., vola._30_n]
                                #]
                for i in range(len(li_close)) #1. 1st loop
                         ]
            with open(res_csvFile, "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerow(csvHeader) #X writerows

                for i, indiVals in enumerate(li_indiRow): #'enu.' returns idx(-> i) & val(-> indiVals) in the loop
                    # Convert timestamp
                    timestamp = li_time[i]                   #Unix timestamp -> local time
                    dt = datetime.fromtimestamp(timestamp)   #e.g. 2025-03-25 00:00:00 is OK
                    dateTime = str(dt)
                    # 1. csvRow <-added- fixed values        #float/str() = no diff.                              
                    csvRow = [
                        dateTime, li_open[i], li_high[i], li_low[i], li_close[i], li_volume[i],
                        li_numPeriod[i], li_numPeriod_2[i], li_macd[i], li_signal[i], li_histogram[i],
                        li_np[i]
                             ]
                    # 2. csvRow <-extend csvRow for adding- based-on-'li_numPeriod' values
                    csvRow.extend(indiVals)
                    # 3. Write csvRow in the csv file
                    writer.writerow(csvRow)

            # Display the retrieved data
                #print("close: ", li_close)

            # Store the stock-name history
            stockNames.append(f"{rndStr}_{sym}")

            # Start again
            while True:
                print("Get more? (y or n): ", end="")
                again = input().strip().lower()
                if again == "y":
                    isAgain = True 
                    rnd += 1
                    print("------------------------------------")
                    break # Continue to get more
                elif again == "n":
                    isAgain = False
                    break
                else:
                    print("Invalid input! Please try again.")
            
        except:
            print("Something wrong, please check 'stockRetrieve.py'")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            continue

    # End of getting the data
    printStockNames(stockNames)
            
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
