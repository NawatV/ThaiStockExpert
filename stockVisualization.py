# ----- Plotly -----
import plotly.graph_objects as pgo
import pandas as pd
from plotly.subplots import make_subplots
import plotly.express as px
    #print(px.colors.qualitative.Plotly) | https://plotly.com/python/discrete-color/
# ----- Operation ------
import random
import numbers
from datetime import datetime
import sys


# ========= Read history data in .csv & visualize in candlestick with indicators |
#           Customized the layout | Created func.
#           +Hovermode | +Overbought/sold | +numPeriod after indicator's name |
#           ** Multi-numPs & bugs fixed | Customized the data layout
#           | +Exit opt. | Optimized the code | VIS2 | Cus.the data layout
#           | +input.strip() |Cus.the data layout & layout | +sharp perf.'s colors
#           | Modified 'ranColHex' | VIS 3 | Added dots to graph | Fixed dataRow bug
#
#           Big try-except (compre.) =================


# #-#-#-#-# Visualization Part #-#-#-#-#
#SEE func.visualize() BELOW FIRST

## csvOP: a Pandas DF (2D table)
#  csvOP.shape= (rows, cols)
#  csvOP["colName"] = that entire col | csvOP.iloc[0] = the entire row 1
#       csvOP.at[5,"li_close"] = Closing price at row 6

li_rgb_history = [] #Cleared when start a new vis.

def ranColHex(li_rgb_history):
    while True:
        r = random.randint(51, 200) #0,255 | >200:too light, <51:too dark 
        g = random.randint(51, 200) 
        b = random.randint(51, 200)
        rgb = [r,g,b]
        if r == 152 and g == 251 and b == 152: continue #palegreen
        elif r == 220 and g == 20 and b == 60: continue #crimson
        elif rgb in li_rgb_history: continue                #redundnat
        else:
            li_rgb_history.append(rgb)
            break 
    return "#{:02x}{:02x}{:02x}".format(r, g, b)
        #format: x=lowercase | 02=zero-padded to 2 digits (e.g., 7->07, 15->0f) | e.g., return "#1a2b3c"

def getCandyStick(rnd_stockName):
    csvFileName = rnd_stockName
    # Read csv      ##### PATH !!!
    csvPath = f"C://Users//LENOVO//Desktop//thai_stock_expert//output//{csvFileName}.csv"   
    csvOP = pd.read_csv(csvPath, keep_default_na=False) ## Change from nan (not a no.) to ""

    ###---- Bug fixed: ambiguous date formats by inferring & standardizing ----
    csvOP["li_time"] = pd.to_datetime(csvOP["li_time"], errors="coerce")
    #--- Drop rows with invalid or missing dates ---
    csvOP = csvOP[csvOP["li_time"].notna()]

    # Remove any row entirely empty/ only ""
        #csvOP.dropna(how='all', inplace=True) 
        #csvOP = csvOP[ csvOP["li_time"].str.strip() != "" ]
        #csvOP = csvOP[~(csvOP == "").all(axis=1)]
    
    #--- Get all the csv headers ---
    csvHeaders = list(csvOP.columns)                    #-> ["li_date", "li_open",..]
    #=== To_numeric ### Solved a big confusion by lib.Pandas | ## to 'X.0' ===
    for csvH in csvHeaders:
        if csvH != "li_time":
            csvOP[csvH] = pd.to_numeric(csvOP[csvH], errors="coerce") ## Change from "" to nan
    
    # Get title
    names = csvFileName.split("_")
    name = names[1]
    name = name.upper()
    title = f"Candlestick Chart & Volume with Indicators: {name}"

    # Get 'li_numPeriod'
    li_numPeriod = csvOP["li_numPeriod"]

    # Create a layout grid of plots (subplots); 6 rows 1 col
    fig = make_subplots(shared_xaxes= True, #Solved: trade-off (-)date (+)vol.movable
                        #specs=[ [{}], [{}], [{}], [{}] ], #X - specs=[[{"type": "xy"}], [{"type": "candlestick"}]])
                        vertical_spacing= 0.001, #<-0.03<-0.25 
                        row_width=[0.07, 0.07, 0.07, 0.07, 0.09, 1.5], #View: down->up = turn left 90c & look
                        #X [no need]- subplot_titles=("Plot 1", "Plot 2",..)
                        rows= 6, cols= 1
                        )

    # 1st row: Add trace 1 to row[0]col[0]
    fig.add_trace(pgo.Candlestick(  
        x= csvOP["li_time"],    
        open= csvOP["li_open"],
        high= csvOP["li_high"],
        low= csvOP["li_low"],
        close= csvOP["li_close"],
        name="Candlestick",
        increasing_line_color="palegreen",   
        decreasing_line_color="crimson",
                                 ),
        row=1, col=1
                  )

    # 2nd row: No use -> Solved the layout prob.

    # 3rd row: Add trace 2 to row[2]col[0]
    dts = pd.to_datetime(csvOP["li_time"])
        #Estimate the interval between data points
    interval_ms = (dts[1] - dts[0]).total_seconds() * 1000
        #Set bar width as ~50% of that interval
    bar_width = interval_ms * 0.5

    fig.add_trace(
        pgo.Bar(x=csvOP["li_time"], y=csvOP["li_volume"],        
            width= bar_width , name="Volume", #X visible='legendonly'
            marker_color="darkblue"
                ),
        row=3, col=1
                 )

    # 4th row: Add trace 3 to row[3]col[0]
    for numP in li_numPeriod:
        if isinstance(numP, numbers.Number) and not pd.isna(numP):
            numP = int(numP)
            fig.add_trace(
                pgo.Scatter(x=csvOP["li_time"], y=csvOP[f"li_rsi_{numP}"],
                mode ="lines", name= f"RSI {numP}", showlegend= False,
                marker_color= ranColHex(li_rgb_history),
                hovertemplate= f"RSI {numP} : %{{y:.2f}}<extra></extra>"
                    ),
                row=4, col=1
                 )
    #--- Overbought >70,red, Oversold <30,green) ---                            
    fig.add_hrect(y0=70, y1=100, line_width=0, fillcolor="red", opacity=0.2, row=4, col=1)
    fig.add_hrect(y0=0, y1=30, line_width=0, fillcolor="green", opacity=0.2, row=4, col=1)


    # 5th row: Add trace 4 to row[4]col[0]
    #--- MACD ---
    fig.add_trace(
        pgo.Scatter(x=csvOP["li_time"], y=csvOP["li_macd"],
            mode ="lines", name= "MACD", showlegend= False,
            marker_color= ranColHex(li_rgb_history),
            hovertemplate= "MACD : %{y:.2f}<extra></extra>"
                    ),
                row=5, col=1
                 )
    #--- Signal ---
    fig.add_trace(
        pgo.Scatter(x=csvOP["li_time"], y=csvOP["li_signal"],
                mode ="lines", name= "Signal", showlegend= False,
                marker_color= ranColHex(li_rgb_history),
                hovertemplate= "Signal : %{y:.2f}<extra></extra>"
                    ),
                row=5, col=1
                 )

    # 6th row: Add trace 5 to row[5]col[0]
    #--- Histogram (>0,green, <0,red, =0,black ) ---
    histVals = csvOP["li_histogram"]
    histCol = ["green" if val > 0 else "red" if val < 0 else "black" for val in histVals]
    
    fig.add_trace(
        pgo.Bar(x=csvOP["li_time"], y=csvOP["li_histogram"], base=0, #To expand from the baseline
            width= bar_width, name="Histogram", #X visible='legendonly'
            marker_color= histCol, #Dynamic coloring here
            hovertemplate= "Histogram : %{y:.2f}<extra></extra>"
                    ),
            row=6, col=1
             )


    # Update layout
    #--- Axis-X & Y ---    
    fig.update_layout(title= title,
        hovermode="x unified",              #= vertical line + unified tooltip
        xaxis= dict(title="",
                    title_font= dict(size=12, color="black"),
                        #tickangle= -45,    ##Plot dots in line graph
                        #tickfont= dict(size=12, color='black'),
                    tickformat= ".2f",
                    showgrid=True,
                    gridcolor="lightgray",
                    rangeslider=dict(
                        visible= True,
                        thickness= 0.06     ## key
                        ),
                    type="date"             #Needed for date-based sliders
                    ),

        # xaxis2 - No use

        ### (1st y-axis) 
        yaxis= dict(title= f"Price: {name}",
                    title_font= dict(size=12, color="black"),
                    #dtick="..",            ##Plot dots in line graph
                    tickformat= ".2f",      #Limit to 2 decimal places
                    domain=[0.51, 1]        #[gap below, total height] 
                    ),

        ### (3rd y-axis)
        yaxis3= dict(title="Volume",
                     title_font= dict(size=10, color="black"),
                     domain=[0.31,0.41]
                     ),                     #X: height = 800 due to unresponsive to browser

        ### (4th y-axis)
        yaxis4= dict(title= "RSI", 
                     title_font= dict(size=10, color="black"),
                     domain=[0.22, 0.28],
                     range=[0, 100]         #For Overbought & Oversold 
                     ),
                      
        ### (5th y-axis)
        yaxis5= dict( title=dict (text="MACD<br>& Signal"),  #Line break here
                      title_font= dict(size=8, color="black"),
                      domain=[0.11, 0.20],
                    ),

        ### (6th y-axis)
        yaxis6= dict( title=dict (text="Histogram"),  #Line break here
                      title_font= dict(size=10, color="black"),
                      domain=[0, 0.09],
                      zeroline=True,        #To ensure the histogram expands from 0
                      zerolinewidth=1,
                      zerolinecolor="grey",
                      range=None
                    )     
        )

    # Add details on the layout
    for numP in li_numPeriod:
        if isinstance(numP, numbers.Number) and not pd.isna(numP):
            numP = int(numP)
            #--- SMA ---
            fig.add_trace(pgo.Scatter(x= csvOP["li_time"], y= csvOP[f"li_sma_{numP}"], mode="lines", name= f"SMA {numP}",
                marker= dict(color= ranColHex(li_rgb_history), line= dict(width=0.025))), row=1, col=1)
            #--- EMA ---
            fig.add_trace(pgo.Scatter(x= csvOP["li_time"], y= csvOP[f"li_ema_{numP}"], mode="lines", name= f"EMA {numP}",
                marker= dict(color= ranColHex(li_rgb_history), line= dict(width=0.025))), row=1, col=1)
            #--- Upper Bands ---
            fig.add_trace(pgo.Scatter(x= csvOP["li_time"], y= csvOP[f"li_up_{numP}"], mode="lines", name= f"Upper {numP}",
                marker= dict(color= ranColHex(li_rgb_history), line= dict(width=0.025))), row=1, col=1)
            #--- Lower Bands ---
            fig.add_trace(pgo.Scatter(x= csvOP["li_time"], y= csvOP[f"li_down_{numP}"], mode="lines", name= f"Lower {numP}",
                marker= dict(color= ranColHex(li_rgb_history), line= dict(width=0.025))), row=1, col=1)
    fig.show()


#--- 2ND VIS ---
def compareStock(rnd_stockName_inputs):
    # Create 'li_compareInputs'
    if "," in rnd_stockName_inputs:
        li_compareInputs = [s.strip() for s in rnd_stockName_inputs.split(",")]
    else:
        li_compareInputs = [rnd_stockName_inputs.strip()]

    #------ Outside the loop ------
    # Create a layout grid of plots (subplots); 4 rows 1 col
    fig = make_subplots(shared_xaxes= True, #Solved: trade-off (-)date (+)vol.movable
                        vertical_spacing= 0.001,
                        row_width=[0.09, 0.09, 0.09, 1.5], #View: down->up
                        rows= 4, cols= 1)    
    set_name = set()
    #--- SRC: Sharp Ratio's Colorization ---        
    y0 = sys.float_info.max   #SRC: 100% for new_y0 < y0. So y0 <- new_y0 
    y1 = -sys.float_info.max  #SRC: Reverse the same logic 

    # Loop for each stock
    for cin in li_compareInputs:
        csvFileName = cin
        # Read csv      ##### PATH !!!
        csvPath = f"C://Users//LENOVO//Desktop//thai_stock_expert//output//{csvFileName}.csv"   
        csvOP = pd.read_csv(csvPath, keep_default_na=False) ## Change from nan (not a no.) to ""

        ###---- Bug fixed: ambiguous date formats by inferring & standardizing ----
        csvOP["li_time"] = pd.to_datetime(csvOP["li_time"], errors="coerce")
        #--- Drop rows with invalid or missing dates ---
        csvOP = csvOP[csvOP["li_time"].notna()]

        #--- Get all the csv headers ---
        csvHeaders = list(csvOP.columns)                    #-> ["li_date", "li_open",..]
        #=== To_numeric ### Solved a big confusion by lib.Pandas | ## to 'X.0' ===
        for csvH in csvHeaders:
            if csvH != "li_time":
                csvOP[csvH] = pd.to_numeric(csvOP[csvH], errors="coerce")
                                                            ### Change ALL(except li_time) from "" to nan

        # Get 'name'
        names = csvFileName.split("_")
        name = names[1]
        name = name.upper()
        set_name.add(name)

        # Get 'li_numPeriod_2'
        li_numPeriod_2 = csvOP["li_numPeriod_2"]

        # Set the color for this stock data
        stockCol = ranColHex(li_rgb_history)


        # 1st row: Add trace 1 to row[0]col[0] | Add details on the layout
        fig.add_trace(pgo.Scatter(x= csvOP["li_time"],  #<- .iloc[i] -> type='str'
                                  y= csvOP["li_np"], mode="lines", name= f"{name} (NP)",
            marker= dict(color= stockCol, line= dict(width=0.025))), row=1, col=1 )

        # 2nd row: No use -> Solved the layout prob.

        # 3rd row: Add trace 2 to row[2]col[0]
        for numP2 in li_numPeriod_2 :
            if isinstance(numP2, numbers.Number) and not pd.isna(numP2):
                numP2 = int(numP2)
                fig.add_trace(pgo.Scatter(x= csvOP["li_time"],
                                          y= csvOP[f"li_volatility_{numP2}"], mode="lines",
                    name= f"{name} (Vol {numP2})",
                    marker= dict(color= stockCol, line= dict(width=0.025)),
                    hovertemplate= f"{name} : Vol {numP2} : %{{y:.2f}}<extra></extra>"
                                          ), row=3, col=1 )

        # 4th row: Add trace 3 to row[3]col[0]
        # Plot 'Sharp Ratio'
        for numP2 in li_numPeriod_2:
            if isinstance(numP2, numbers.Number) and not pd.isna(numP2):
                numP2 = int(numP2)
                fig.add_trace(pgo.Scatter(x= csvOP["li_time"],
                                          y= csvOP[f"li_sharp_{numP2}"], mode="lines",
                    name= f"{name} (Sharp {numP2})",
                    marker= dict(color= stockCol, line= dict(width=0.025)),
                    hovertemplate= f"{name} : Sharp {numP2} : %{{y:.2f}}<extra></extra>"
                                          ), row=4, col=1 )
        # Set y0, y1
        for numP2 in li_numPeriod_2:
            if isinstance(numP2, numbers.Number) and not pd.isna(numP2):
                numP2 = int(numP2)
                #--- li_sharp_tmp: "" -> .min | get new_y0&_y1 ---
                li_sharp_numP = csvOP[f"li_sharp_{numP2}"]      #-> [NaN, NaN,.., val]                
                #--- forMin --- 
                li_sharp_forMin = [sys.float_info.max if pd.isna(val) else val for val in li_sharp_numP]
                new_y0 = min(li_sharp_forMin)
                #--- forMax ---
                li_sharp_forMax = [-sys.float_info.max if pd.isna(val) else val for val in li_sharp_numP] 
                new_y1 = max(li_sharp_forMax)
                # Set y0, y1
                if new_y0 < y0: y0 = new_y0 #SRC: Same
                if new_y1 > y1: y1 = new_y1 #SRC: Reversely same
            
    # Get 'title' 
    title = "Performance & Risk Comparison: "
    for name in set_name:
        title += name + " | "


    # Update layout
    #--- Axis-X & Y ---    
    fig.update_layout(title= title,
        hovermode="x unified",              #= vertical line + unified tooltip
        xaxis= dict(title="",
                    title_font= dict(size=12, color="black"),
                    tickformat= ".2f",
                    showgrid=True,
                    gridcolor="lightgray",
                    rangeslider=dict(
                        visible= True,
                        thickness= 0.06     ## key
                        ),
                    type="date"             #Needed for date-based sliders
                    ),

        # xaxis2 - No use

        ### (1st y-axis) 
        yaxis= dict(title= f"Normalized Price",
                    title_font= dict(size=12, color="black"),
                    #dtick="..",            ##Plot dots in line graph
                    tickformat= ".2f",      #Limit to 2 decimal places
                    domain=[0.48, 1]        #[gap below, total height] 
                    ),

        ### (3rd y-axis)
        yaxis3= dict(title="Volatility",
                     title_font= dict(size=10, color="black"),
                     domain=[0.20,0.34] 
                     ),                        

        ### (4th y-axis)
        yaxis4= dict(title="Sharp Ratio",
                     title_font= dict(size=10, color="black"),
                     domain=[0.00,0.14] 
                     ),                        
        )

    #--- SRC: Sharp Perf.'s Colors: >0.1 above R_f | =0 no excess return | <0 below R_f ---  
    #--- Green ---
    fig.add_hrect( #x0=x0, x1=x1,
                       #X: xref="x", yref="y4"          #<- x4
                       #X: xref="paper", yref="paper"   #"paper" makes y span the full subplot | xref="x" 
        y0=0.1, y1=y1, line_width=0, fillcolor="green", opacity=0.2, row=4, col=1)
    #--- Red ---
    fig.add_hrect(y0=y0, y1=0, line_width=0, fillcolor="red", opacity=0.2, row=4, col=1)
    
    fig.show()
#--------------------------------------------------------------

#--- 3RD VIS ---
def getPredictedPriceTrend(stName, dt_actual, dt_pred, y_vals_actual_in, y_pred_vals_in): #<<<<<
    #type(dt_actual)='pandas..Series'(1D array): a col sliced from a DataFrame 'data'
        #= data['li_time'].iloc[slice_at : stop_before]
    #type(dt_pred)='pandas..DatetimeIndex': a pandas obj for time-based indexing for x-axis val in Plotly/Matplotlib
        #= pd.date_range(start=.., periods=.., freq=..)
    #type(y_vals_actual_in)='numpy.ndarray': a NumPy array containing actual price values (after inverse transform)
        #= scaler.inverse_transform(x)[:, cols_to_use.index('li_close')] //x's shape is 2D= (729-1-100, 5) 
    #type(y_pred_vals_in)='numpy.ndarray': 'same as above'

    
    # Create a layout grid of plots (subplots); 1 row 1 col
    fig = make_subplots(shared_xaxes= True, #Solved: trade-off (-)date (+)vol.movable
                        vertical_spacing= 0.001,
                        row_width=[1], #View: down->up
                        rows= 1, cols= 1)    

    # 1st row: Add trace 1 to row[0]col[0] | Add details on the layout
    fig.add_trace(pgo.Scatter(x= dt_actual,  #<- .iloc[i] -> type='str'
                              y= y_vals_actual_in, mode="lines+markers", name= f"{stName} - Actual",
                    line= dict(color="black"), #X: width=2
                    marker= dict(size=4, color="black", opacity=1, line= dict(width=0.025, color="black"))),
                    row=1, col=1)

    # 1st row: Add trace 2 to row[0]col[0] | Add details on the layout
    fig.add_trace(pgo.Scatter(x= dt_pred,   
                              y= y_pred_vals_in, mode="lines+markers", name= f"{stName} - Predicted Trend",
                    line=dict(color="blue"),
                    marker= dict(size=4, color="blue", opacity=1, line= dict(width=0.025, color="blue"))),
                    row=1, col=1)

    #---------- Former manipulation -------------------------
    #fig.add_trace(pgo.Scatter(x= dt_actual,
    #                          y= y_vals_actual_in, mode="lines", name= f"{stName} - Actual",
    #              marker= dict(color="black", line= dict(width=0.025))), row=1, col=1 )
    #X: fig.add_vline(..)
    #--------------------------------------------------------
 
    # Get 'title' 
    title = f"Predict Stock Price Trend: {stName}"


    # Update layout
    #--- Axis-X & Y ---    
    fig.update_layout(title= title,
        hovermode="x unified",              #= vertical line + unified tooltip
        xaxis= dict(title="",
                    title_font= dict(size=12, color="black"),
                    #tickformat= ".2f",
                    showgrid=True,
                    gridcolor="lightgray",
                    rangeslider=dict(
                        visible= True,
                        thickness= 0.06     ## key
                        ),
                    type="date"             #Needed for date-based sliders
                    ),
                      
        ### (1st y-axis) 
        yaxis= dict(title= f"Price",
                    title_font= dict(size=12, color="black"),
                    #dtick="..",            ##Plot dots in line graph
                    tickformat= ".2f",      #Limit to 2 decimal places
                    #domain=[0.48, 1]        #[gap below, total height] 
                    ),                     
        )

    fig.show()
#--------------------------------------------------------------


def visualize(visType): #### Make sure the imported .py's path = this .py's path before 
    isAgain = True
    while isAgain == True :
        try:
            li_rgb_history = [] #Cleared
            print("!! Accuracy depends on the retrieved data !!")
            if visType == "3":
                print("Type 1 <round>_<stock> or Exit (exit): ", end="")
                rnd_stockName = input().strip().lower() #strip & lower before passing this param
                #--- Exit before ---
                if rnd_stockName == "exit": return
                # Visualize: Candlestick
                getCandyStick(rnd_stockName)
            elif visType == "4":
                print("!!! Please do not compare using different intervals and/or others !!!")
                print("Type >=1 <round>_<stock> or Exit (exit)")
                print("1 or Multi(e.g., <r1>_<s1>, <r1>_<s2>): ", end="")
                rnd_stockName_inputs = input().strip().lower()
                #--- Exit before ---
                if rnd_stockName_inputs == "exit": return
                # Compare stock data
                compareStock(rnd_stockName_inputs)
            #elif visType == "5":
                #--- Exit before: in stockLSTM.py ---
                # Visualize: PredictedPriceTrend
                #--- getPredictedPriceTrend(..): in stockLSTM.py ---
                
            print("Visualize more? (y or n): ", end="")
            again = input().strip().lower()
            if again == "y":
                isAgain = True
                print("------------------------------------")
            elif again == "n":
                isAgain = False
                print("====================================")
            else:
                print("Invalid input! Please try again.")
                
        except:
            print("Invalid stock name OR something wrong,")
            print("please check 'stockVisualization.py'")
            continue

# ================= END OF PROGRAM =================
