# ----- Plotly -----
import plotly.graph_objects as pgo
import pandas as pd
from plotly.subplots import make_subplots
import plotly.express as px
    #print(px.colors.qualitative.Plotly) | https://plotly.com/python/discrete-color/
# ----- Color ------
import random
# ----- Number -----
import numbers


# ========= Read history data in .csv & visualize in candlestick with indicators |
#           Customize the layout | Create func. |
#           +Hovermode | +Overbought/sold | +numPeriod after indicator's name |
#           ** Multi-numPs & bugs fixed
#           *** X(=tmp): try-except =================


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

def getCandySticks(rnd_stockName):
#    try:
    # -> lower for csv file's name
    csvFileName = rnd_stockName.lower()
    # Read csv      ##### PATH !!!
    csvPath = f"C://Users//LENOVO//Desktop//thai_stock_expert//output//{csvFileName}.csv"   
    csvOP = pd.read_csv(csvPath, keep_default_na=False) #Change from nan (not a no.) to ""
    #--- Get all the csv headers ---
    csvHeaders = list(csvOP.columns) #-> ["li_date", "li_open",..]
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
                        row_width=[0.07, 0.07, 0.09, 1.5], #View: down->up = turn left 90c & look
                            #X [no need]- subplot_titles=("Plot 1", "Plot 2", "Plot 3", "Plot 4")
                        rows= 4, cols= 1
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
                pgo.Scatter(x=csvOP["li_time"], y=csvOP[f"li_rsi_{numP}"], mode ="lines",         
                name= f"RSI {numP}", showlegend= False,
                marker_color= ranColHex()
                    ),
                row=4, col=1
                 )
    
    #--- Overbought >70,red, Oversold <30,green) ---                            
    fig.add_hrect(y0=70, y1=100, line_width=0, fillcolor="red", opacity=0.2, row=4, col=1)
    fig.add_hrect(y0=0, y1=30, line_width=0, fillcolor="green", opacity=0.2, row=4, col=1)


    # Update layout
    #--- Axis-X & Y ---    
    fig.update_layout(title= title,
        hovermode="x unified",  #= vertical line + unified tooltip
        xaxis= dict(title="",
                    title_font= dict(size=12, color="black"),
                        #tickangle= -45,    ##Plot dots in line graph
                        #tickfont= dict(size=12, color='black'),
                    tickformat= ".2f",
                    showgrid=True,
                    gridcolor="lightgray",
                    rangeslider=dict(
                        visible= True,
                        thickness= 0.06 ## key
                        ),
                    type="date"  #Needed for date-based sliders
                    ),

        # xaxis2 - No use

        ### (1st y-axis) 
        yaxis= dict(title= f"Price: {name}",
                    title_font= dict(size=12, color="black"),
                    #dtick="..",            ##Plot dots in line graph
                    #tickfont= dict(size=12, color='black'),
                    tickformat= ".2f", #Limit to 2 decimal places
                    domain=[0.27, 1], 
                        #shrink candlestick plot to 80% height, leaving 20% gap at the bottom
                    ),

        ### (3rd y-axis)
        yaxis3= dict(title="Volume",
                     title_font= dict(size=10, color="black"),
                     #tickformat= ".2f",
                     domain=[0.07,0.17]
                     ),
                    #X: height = 800 due to unresponsive to browser

        ### (4th y-axis)
        yaxis4= dict(title= f"RSI", 
                     title_font= dict(size=10, color="black"),
                     #tickformat= ".2f",
                     domain=[0,0.06],
                     range=[0, 100] #for Overbought & Oversold 
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
#-------------------------------


def visualize():
    isAgain = True
    while isAgain == True :
#        try:
            print("Type <round>_<stock> to be visualized: ", end="")
            rnd_stockName = input()

    # Visualize ##### Make sure the imported .py's path = this .py's path before 
            getCandySticks(rnd_stockName)

            print("Visualize more? (y or n): ", end="")
            again = input()
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
