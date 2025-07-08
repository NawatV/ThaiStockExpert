# ----- Related .py -----
import stockRetrieve as stRet
import stockVisualization as stVis
import stockLSTM as stLSTM
import stockGRU as stGRU
#------ Operation -----
import os

# ===== Code struc.changed: 'main' -> getS | +delRSDpath | +input.strip() |
# 'Quo'-Handle all input errors | Cus. | Edited text - all | Use stRe's func. in '2' |
#       Added 'stGRU' =====

while True:
    print("//// Please beware of issue due to invalid/improper input ////")
    print("Actions: ")
    print("-> Get stock data (+web scraping) - 1")
    print("-> View stock data - 2")
    print("-> Visualize: Candlestick - 3")
    print("-> Compare stock data - 4")
    print("-> Predict (+visualize) stock price trend - 5")
    print("-> Delete stock data permanently - 6")
    print("-> Exit - 7")
    print("Choose your actions (no.): ", end="")
    action = input().strip() #Remove space
    if action == "1":
        print("---- Internet connection required ----")
        stRet.getStockData() #stockRetrieve.py
    elif action == "2":
        print("------------------------------------")
        RSDfn_list = stRet.getRSDpath_list("view")  #stockRetrieve.py
        stRet.printStockNames(RSDfn_list)           #stockRetrieve.py
    elif action == "3":
        print("---- Restart the program if it takes too long ----")
        stVis.visualize("3") #stockVisualization.py | from .csv only
    elif action == "4":
        print("---- Restart the program if it takes too long ----")
        stVis.visualize("4") #stockVisualization.py | from .csv only
    elif action == "5":
        print("------------------------------------")
        print("Choose the model type: LSTM - 1, GRU (recommended) - 2: ", end="")
        act = input().strip() #Remove space
        if act == "1":
            stLSTM.runLSTM() #stockLSTM.py (+stVis inside) | from .csv only
        elif act == "2":
            stGRU.runGRU() #stockGRU.py (+stVis inside) | from .csv only
        else:
            print("Invalid input! Please try again.")
    elif action == "6":
        print("------------------------------------")
        stRet.delRSDpath() #stockRetrieve.py | from .csv only
    elif action == "7":
        break
    else:
        print("Invalid input! Please try again.")
    print("------------------------------------")
    
