# ----- Related .py -----
import stockRetrieve as stRet
import stockVisualization as stVis
#------ Operation -----
import os

# ===== Code struc.changed: 'main' -> getS | +delRSDpath =====

while True:
    print("Actions: ")
    print("-> Get stock data - 1")
    print("-> View the retrieved stock data - 2")
    print("-> Visualize stock data - 3")
    print("-> Delete the retrieved stock data - 4")
    print("-> Exit - 5")
    print("Choose your actions (no.): ", end="")
    action = input()
    if action == "1":
        print("------------------------------------")
        stRet.getStockData() #stockRetrieve.py
    elif action == "2":
        print("------------------------------------")
        RSDfn_list = stRet.getRSDpath_list("view") #stockRetrieve.py
        for fn in RSDfn_list:
            print("----> ", fn)
    elif action == "3":
        print("---- Restart the program if it takes too long ----")
        stVis.visualize() #stockVisualization.py | from .csv only
    elif action == "4":
        print("------------------------------------")
        stRet.delRSDpath() #stockRetrieve.py | from .csv only
    elif action == "5":
        break
    else:
        print("Invalid input! Try again.")
    print("------------------------------------")


