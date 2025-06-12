# ----- Related .py -----
import stockRetrieve as stRet
import stockVisualization as stVis

# ===== Code struc.changed: 'main' -> getS =====

while True:
    print("Actions: ")
    print("-> Get stock data - 1")
    print("-> See the retrieved stock data - 2")
    print("-> Visualize stock data - 3")
    print("-> Exit - 4")
    print("Choose your actions (no.): ", end="")
    action = input()
    if action == "1":
        print("------------------------------------")
        stRet.getStockData() #stockRetrieve.py
    elif action == "2":
        print("------------------------------------")
        RSDfn_list = stRet.getRSDfn_list() #stockRetrieve.py
        for fn in RSDfn_list:
            print("----> ", fn)
    elif action == "3":
        print("---- Restart the program if it takes too long ----")
        stVis.visualize() #stockVisualization.py
    elif action == "4":
        break
    else:
        print("Invalid input! Try again.")
    print("------------------------------------")



        


