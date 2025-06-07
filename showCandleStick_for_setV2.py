import plotly.graph_objects as pgo
import pandas as pd
from plotly.subplots import make_subplots
import plotly.express as px
    #print(px.colors.qualitative.Plotly) | https://plotly.com/python/discrete-color/

# ========= Read history data in .csv & visualize in candlestick with indicators |
#           X(tmp): try-except | Customize the layout =================
#try:
# Read .csv      #>>>>>>>> Change to func & getPath
csvPath = "C://Users//LENOVO//Desktop//thai_stock_expert//output//amata_2.csv"   
csvOP = pd.read_csv(csvPath)
# --- Get title ---
stNs = csvPath.split("//") 
nameTmp = stNs[len(stNs)-1]
nameTmps = nameTmp.split("_")
nname = nameTmps[0]
name = nname.upper()
ttl = f"Candlestick Chart with Indicators: {name}"

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
    x= csvOP['li_time'],    
    open= csvOP['li_open'],
    high= csvOP['li_high'],
    low= csvOP['li_low'],
    close= csvOP['li_close'],
    name="Candlestick",
    increasing_line_color="palegreen",   
    decreasing_line_color="crimson"  
    ),
    row=1, col=1)

### 2nd row: No use -> Solved the layout prob.

# 3rd row: Add trace 2 to row[2]col[0]
dts = pd.to_datetime(csvOP['li_time'])
    #Estimate the interval between data points
interval_ms = (dts[1] - dts[0]).total_seconds() * 1000
    #Set bar width as ~50% of that interval
bar_width = interval_ms * 0.5

fig.add_trace(
    pgo.Bar(x=csvOP['li_time'], y=csvOP['li_volume'],           
    width= bar_width , name="Volume", #X visible='legendonly'
    marker_color='darkblue'
            ),
    row=3, col=1
             )

# 4th row: Add trace 3 to row[3]col[0]
fig.add_trace(
    pgo.Scatter(x=csvOP['li_time'], y=csvOP['li_rsi'], mode="lines",          
    name="RSI", #X visible='legendonly'
    marker_color='orange'
            ),
    row=4, col=1
             )

# ----- No use, subplots->add_trace instead -----
# Candlestick
# fig = pgo.Figure(data=[pgo.Candlestick(x= csvOP['li_time'],
# open= csvOP['li_open'], high= csvOP['li_high'], low= csvOP['li_low'], close= csvOP['li_close'],
# increasing_line_color="green", decreasing_line_color="brown" )])
## Already inserted x for the hidden ones in .csv
# fig = pgo.Figure()


# Update layout
#--- Axis-X & Y ---    
fig.update_layout(title= ttl,
    xaxis= dict(title="",
                title_font= dict(size=12, color='black'),
                    #tickangle= -45,    ## Plot dots in line graph
                    #tickfont= dict(size=12, color='black'),
                showgrid=True,
                gridcolor='lightgray',
                rangeslider=dict(
                    visible= True,
                    thickness= 0.06 ## key
                    ),
                type="date"  # Needed for date-based sliders
                ),

    # xaxis2 - No use

    ###     
    yaxis= dict(title= f"Price: {name}",
                title_font= dict(size=12, color='black'),
                #dtick="..",            ## Plot dots in line graph
                #tickfont= dict(size=12, color='black'),    
                domain=[0.27, 1], 
                    #shrink candlestick plot to 80% height, leaving 20% gap at the bottom
                ),

    ### (3rd (bottom) y-axis)
    yaxis3= dict(title="Volume",
                 title_font= dict(size=12, color='black'),
                 domain=[0.07,0.17]
                 ),
                #X: height = 800 due to unresponsive to browser

    ### (4th (bottom) y-axis)
    yaxis4= dict(title="RSI",
                 title_font= dict(size=12, color='black'),
                 domain=[0,0.06]
                 )
    )

# Add details on the layout
#--- SMA & EMA ---
fig.add_trace(pgo.Scatter(x= csvOP['li_time'], y= csvOP['li_sma'], mode='lines', name='SMA',
              marker= dict(color= "grey", line= dict(width=0.025))))
fig.add_trace(pgo.Scatter(x= csvOP['li_time'], y= csvOP['li_ema'], mode='lines', name='EMA',
              marker= dict(color= "black", line= dict(width=0.025))))
#--- upper & lower bands ---
fig.add_trace(pgo.Scatter(x= csvOP['li_time'], y= csvOP['li_up'], mode='lines', name='Upper Band',
              marker= dict(color= "green", line= dict(width=0.025))))
fig.add_trace(pgo.Scatter(x= csvOP['li_time'], y= csvOP['li_down'], mode='lines', name='Lower Band',
              marker= dict(color= "red", line= dict(width=0.025))))

fig.show()
            

#except:
#    print("Something wrong, check the source code!")
#    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
