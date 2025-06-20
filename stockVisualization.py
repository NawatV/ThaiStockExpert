# ----- Plotly -----
import plotly.graph_objects as pgo
import pandas as pd
from plotly.subplots import make_subplots
import plotly.express as px
    #print(px.colors.qualitative.Plotly) | https://plotly.com/python/discrete-color/
# ----- Operation ------
import random
import numbers


# ========= Read history data in .csv & visualize in candlestick with indicators |
#           Customized the layout | Create func. | try-except
#           +Hovermode | +Overbought/sold | +numPeriod after indicator's name |
#           ** Multi-numPs & bugs fixed | Customized the data layout
#           | +Exit opt. | Optimized the code | VIS2: multi-Volatility & NP | Cus.the data layout
#           | +input.strip()
#
#           X(TMP): try-except =================


# #-#-#-#-# Visualization Part #-#-#-#-#
#SEE func.visualize() BELOW FIRST

def ranColHex():
    while True:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255) 
        if r == 152 and g == 251 and b == 152: continue #palegreen
        elif r == 220 and g == 20 and b == 60: continue #crimson
        elif r >= 210 and g >= 210 and b >= 210: continue #too light
        elif r <= 50 and g <= 50 and b <= 50: continue #too dark
        else: break 
    return "#{:02x}{:02x}{:02x}".format(r, g, b)
        #format: x=lowercase | 02=zero-padded to 2 digits (e.g., 7->07, 15->0f) | e.g., return "#1a2b3c"

def getCandyStick(rnd_stockName):
#    try:
    csvFileName = rnd_stockName.lower()                 # -> lower for csv file's name
    # Read csv      ##### PATH !!!
    csvPath = f"C://Users//LENOVO//Desktop//thai_stock_expert//output//{csvFileName}.csv"   
    csvOP = pd.read_csv(csvPath, keep_default_na=False) #Change from nan (not a no.) to ""
    #--- Get all the csv headers ---
    csvHeaders = list(csvOP.columns)                    #-> ["li_date", "li_open",..]
    #=== To_numeric ### Solved a big confusion by lib.Pandas | ### to 'X.0' ===
    for csvH in csvHeaders:
        if csvH != "li_time":
            csvOP[csvH] = pd.to_numeric(csvOP[csvH], errors="coerce") ### Change from "" to nan
    
    # Get title
    names = csvFileName.split("_")
    name = names[1]
    name = name.upper()
    title = f"Candlestick Chart with Indicators: {name}"

    # Get 'li_numPeriod'
    li_numPeriod = csvOP["li_numPeriod"]

    # Create a layout grid of plots (subplots); 4 rows 1 col
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
        marker_color="darkblue",
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
                marker_color= ranColHex(),
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
            marker_color= ranColHex(),
            hovertemplate= "MACD : %{y:.2f}<extra></extra>"
                    ),
                row=5, col=1
                 )
    #--- Signal ---
    fig.add_trace(
        pgo.Scatter(x=csvOP["li_time"], y=csvOP["li_signal"],
                mode ="lines", name= "Signal", showlegend= False,
                marker_color= ranColHex(),
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
                    domain=[0.51, 1],       #[gap below, total height]
                    ),

        ### (3rd y-axis)
        yaxis3= dict(title="Volume",
                     title_font= dict(size=10, color="black"),
                     domain=[0.31,0.41]
                     ),                     #X: height = 800 due to unresponsive to browser
                    
        ### (4th y-axis)
        yaxis4= dict(title= "RSI", 
                     title_font= dict(size=10, color="black"),
                     domain=[0.22,0.28],
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
                      zeroline=True,        #Ensures histogram expands from 0
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
                marker= dict(color= ranColHex(), line= dict(width=0.025))), row=1, col=1)
            #--- EMA ---
            fig.add_trace(pgo.Scatter(x= csvOP["li_time"], y= csvOP[f"li_ema_{numP}"], mode="lines", name= f"EMA {numP}",
                marker= dict(color= ranColHex(), line= dict(width=0.025))), row=1, col=1)
            #--- Upper Bands ---
            fig.add_trace(pgo.Scatter(x= csvOP["li_time"], y= csvOP[f"li_up_{numP}"], mode="lines", name= f"Upper {numP}",
                marker= dict(color= ranColHex(), line= dict(width=0.025))), row=1, col=1)
            #--- Lower Bands ---
            fig.add_trace(pgo.Scatter(x= csvOP["li_time"], y= csvOP[f"li_down_{numP}"], mode="lines", name= f"Lower {numP}",
                marker= dict(color= ranColHex(), line= dict(width=0.025))), row=1, col=1)
    fig.show()
                
#    except:
#        print("Something wrong, check the source code!")
#        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    #return


#--- 2ND VIS ---
def compareStock(rnd_stockName_inputs):
#    try:
    # Create 'li_compareInputs'
    if "," in rnd_stockName_inputs:
        li_compareInputs = [s.strip() for s in rnd_stockName_inputs.split(",")]
    else:
        li_compareInputs = [rnd_stockName_inputs.strip()]

    #------ Outside the loop ------
    # Create a layout grid of plots (subplots); 3 rows 1 col
    fig = make_subplots(shared_xaxes= True, #Solved: trade-off (-)date (+)vol.movable
                        vertical_spacing= 0.001,
                        row_width=[0.09, 0.09, 1.5], #View: down->up
                        rows= 3, cols= 1)    
    set_name = set()

    # Loop for each stock
    for cin in li_compareInputs:
        csvFileName = cin.lower()
        # Read csv      ##### PATH !!!
        csvPath = f"C://Users//LENOVO//Desktop//thai_stock_expert//output//{csvFileName}.csv"   
        csvOP = pd.read_csv(csvPath, keep_default_na=False) #Change from nan (not a no.) to ""
        #--- Get all the csv headers ---
        csvHeaders = list(csvOP.columns)                    #-> ["li_date", "li_open",..]
        #=== To_numeric ### Solved a big confusion by lib.Pandas | ## to 'X.0' ===
        for csvH in csvHeaders:
            if csvH != "li_time":
                csvOP[csvH] = pd.to_numeric(csvOP[csvH], errors="coerce") ## Change from "" to nan

        # Get 'name'
        names = csvFileName.split("_")
        name = names[1]
        name = name.upper()
        set_name.add(name)

        # Get 'li_numPeriod_2'
        li_numPeriod_2 = csvOP["li_numPeriod_2"]

        # Set the color for this stock data
        stockCol = ranColHex()


        # 1st row: Add trace 1 to row[0]col[0] | Add details on the layout
        fig.add_trace(pgo.Scatter(x= csvOP["li_time"],
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


    # Get 'title' 
    title = "Comparison: "
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
                    domain=[0.31, 1]        #[gap below, total height] 
                    ),

        ### (3rd y-axis)
        yaxis3= dict(title="Volatility",
                     title_font= dict(size=10, color="black"),
                     domain=[0.00,0.17] 
                     ),                        
        )

    fig.show()
    
#    except:
#        print("Something wrong, check the source code!")
#        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    #return

#--------------------------------------------------------------


def visualize(visType): #### Make sure the imported .py's path = this .py's path before
    isAgain = True
    while isAgain == True :
#        try:
        print("!! Accuracy depends on the retrieved data !!")
        if visType == "3":
            print("Type 1 <round>_<stock> or Exit (exit): ", end="")
            rnd_stockName = input().strip()
            #--- Exit before ---
            if rnd_stockName == "exit": return
            # Visualize: Candlestick
            getCandyStick(rnd_stockName)
        elif visType == "4":
            print("Type >=1 <round>_<stock> or Exit (exit)")
            print("1 or Multi(e.g., <r1>_<s1>, <r1>_<s2>): ", end="")
            rnd_stockName_inputs = input().strip()
            #--- Exit before ---
            if rnd_stockName_inputs == "exit": return
            # Compare stock data
            compareStock(rnd_stockName_inputs)

        print("Do more? (y or n): ", end="")
        again = input().strip()
        if again == "y":
            isAgain = True
            print("------------------------------------")
        elif again == "n":
            isAgain = False
            print("====================================")
        else:
            print("Invalid input! Try again.")
            
#        except:
#            print("Invalid stock name OR something wrong!")
#            continue

# ================= END OF PROGRAM =================
