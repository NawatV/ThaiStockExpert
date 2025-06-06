import plotly.graph_objects as pgo
import pandas as pd

# ========= Read history data in .csv & visualize in candlestick with indicators
#           try-except =================
try:
    # Read .csv     ### PATH !!! (still fixed)
    csvPath = "C://Users//LENOVO//Desktop//thai_stock_expert//output//ptt_2.csv"   
    csvOP = pd.read_csv(csvPath)
    # --- Get title ---
    stNs = csvPath.split("//") 
    n = stNs[len(stNs)-1]
    ns = n.split("_")
    na = ns[0]
    name = na.upper()
    ttl = f"Candlestick Chart with Indicators: {name}"

    # Candlestick
    fig = pgo.Figure(data=[pgo.Candlestick(x= csvOP['li_time'],
                    open= csvOP['li_open'],
                    high= csvOP['li_high'],
                    low= csvOP['li_low'],
                    close= csvOP['li_close'])])
        # Already inserted x for the hidden ones in .csv

    # Add details
    #--- mavg ---

#>>>>> fig.add_trace(pgo.Scatter(x= csvOP['li_time'], y= csvOP['mavg'], mode='lines', name='Moving Average'))

    #--- upper & lower bands ---
    fig.add_trace(pgo.Scatter(x= csvOP['li_time'], y= csvOP['up'], mode='lines', name='Upper Band'))
    fig.add_trace(pgo.Scatter(x= csvOP['li_time'], y= csvOP['dn'], mode='lines', name='Lower Band'))
    #--- title ---    
    fig.update_layout(title= ttl)
    #--- SMA & EMA ---
    fig.add_trace(pgo.Scatter(x= csvOP['li_time'], y= csvOP['li_sma'], mode='lines', name='SMA'))
    fig.add_trace(pgo.Scatter(x= csvOP['li_time'], y= csvOP['li_ema'], mode='lines', name='EMA'))
   
    fig.show()
except:
    print("Something wrong, check the source code!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
