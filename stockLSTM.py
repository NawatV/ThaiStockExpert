import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
#------ LSTM model ------
from keras.models import Sequential
from keras.layers import LSTM, Bidirectional, Dropout, SimpleRNN, Dense, LayerNormalization
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import load_model
#------ Visualization ------
import matplotlib.pyplot as plt
#------ Related .py -----
import stockRetrieve as stRet
import stockVisualization as stVis

#======= Optimizing attempt (= 100->25 days, _cutLatest.csv) |
#        LSTM:P&P using 5 col.s ('li_open',..,'li_vol.') (accuracy-better) |
#        Added dt (X: dt then day no.) & stName | ->Def-while-try | Call func. in stVis |
#        Integrated to the proj | Handle all input errors |
#        Optimizing attempt (+biLstm, Changed struc.& compile(opti.=RMSprop, loss=huber))
#           (accuracy-better) || Opt.att. (+shuffle=False, Xdropout) | Fixed dataRow bug
#        Big try-except (compre.)   =======



#============= 1.DATA Part: =============
### Shape 1D= (no. of ele,)           = [ele1,ele2,..,eleN] 
### Shape 2D= (no. of row, no. of col)= [[row1],[row2],..,[rowN]] where row1 = col1,col2,..,colN
### Shape 3D= (no. of sample(=row), no. of time_step(=window_size), no. feature(=column to use))

def runLSTM():
    isAgain = True
    while isAgain == True:
#        try:
        print("//// The market is influenced by several factors.")
        print("     So you will get probabilities, not certainties as the results. ////")
        print("**** Based on testings & all the conditions,")
        print("     'no.of days to be used' should= 360 or 100 & 'no.of days to be predicted' should= 90 or 25 respectively [or at least 4/1].")
        print("     (The details will be displayed later) ****")        
        print("!!!! Due to holidays,etc., unfitting date for the predicted. Count as day1,2,.. instead !!!!")
        print("----------------------------------------------------------------------")
        
        # Get csvPath by rnd_stockName
        csvPath = ""
        rnd_stockName = ""
        while True:
            print("!! The data must be daily & retrieved under 'Candle Amount= 1000' !!")
            print("Type 1 <round>_<stock> or Exit (exit): ", end="")
            rnd_stockName = input().strip().lower()
        ## Return to main.py
            if rnd_stockName == "exit": return 
                            ### PATH !!!
            RSDpath_list = stRet.getRSDpath_list("del") #for checking
            csvPath = next((path for path in RSDpath_list if rnd_stockName in path), "")
            if csvPath == "":
                print("Invalid input! Please try again.")
                continue
            break

        # Read csv & get stName
        data = pd.read_csv(csvPath)

        ###---- Bug fixed: ambiguous date formats by inferring & standardizing ----
        data["li_time"] = pd.to_datetime(data["li_time"], errors="coerce")
        #--- Drop rows with invalid or missing dates ---
        data = data[data["li_time"].notna()]
        
        #--- Check the dataRows' sufficiency ---  
        if len(data['li_close']) < 720: #Total= 728 & might be dynamic in the future
            print("Improper input! Please try again.")
            continue
        
        stName = rnd_stockName.split("_")[1].upper()


        # Normalize data
        #--- -> numeric ---
        cols_to_use = ['li_open','li_high','li_low','li_close','li_volume'] #All essen.static col.s | X: li_time
        for col in cols_to_use:
            data[col] = pd.to_numeric(data[col], errors='coerce')           #->NaN if inconvertible
        data = data.dropna(subset = cols_to_use)                            #Drop rows with NaNs (e.g. row 'col names')
        #--- str -> dateTime ---
        data['li_time'] = pd.to_datetime(data['li_time'], errors='coerce')

        #--- Normalize data(=5 col) to {0,1} --- 
        scaler = MinMaxScaler(feature_range=(0,1))
        data_normalized = scaler.fit_transform(data[cols_to_use]) #Shape 2D= (n_rows, 5)
                                                                  #Data= [
                                                                    #[0.41, 0.52, 0.39, 0.44, 0.17]
                                                                    #... ] //e.g.
            #data[['li_close']] returns a 2D DataFrame: shape 2D= (n_rows, 1) 
            #data_normalized_df = pd.DataFrame(data_normalized, columns = data.columns) | Convert back to DataFrame


        # Create seq 
        def create_sequences(data_normalized, window_size):
            X, y = [], []
            for i in range(len(data_normalized) - window_size):
                X.append( data_normalized[i:(i + window_size)] )                           # X=[ [5e[0]-5e[99]],[5e[1]-5e[100]],..,[5e[n-1-100]-5e[n-1]] ]
                y.append( data_normalized[i + window_size, cols_to_use.index('li_close')] )# y=[ [5e[100]]     ,[5e[101]],.......,[5e[n]]             ]
            return np.array(X), np.array(y)

        #### Based upon testings, optimal: USE 1. {5 COL} &
        ####      2. {[4:1] 'window_size= 360d or 100d' to predict the 'outputSize= 90-d or 25-d (respectively)' price trend}
        ####      with removing the last row, 1 incontinuous-date and/or inaccurate dataRow by SET API
        while True:
            print("No.of days whose data will be used to predict (<= 360)")
            print("based on all conditions & testings. It should= 360 or 100: ", end="")
            window_size = int(input().strip()) ##No need to declare outside the while loop
            if 0 < window_size <= 360:
                break
            else:
                print("Improper input! Please try again.")
                continue
            
        X, y = create_sequences(data_normalized, window_size)
        print("X.shape:", X.shape)  ## Shape 3D= (allRows -w_s, w_s, 5) = (627, 100, 5) //i=100(ele 101 due to w_s=100) to i=727(ele 728)
        print("y.shape:", y.shape)  ## Shape 1D= (allRows -w_s,) = (627,)


        # All= training data
        X_train = X
        y_train = y
        #---------- Former manipulation --------------------------------
        # Split 'X, y' into training & testing sets //w_s = 15
        #split = int(0.8 * len(X))
        #X_train, X_test = X[:split], X[split:] # X=[ [e[0]-e[14]],[e[1]-e[15]],. | .,[e[n-1-15]-e[n-1]] ]
                                                #          X_train (80%)          |     X_test (20%)       
        #y_train, y_test = y[:split], y[split:] # y=[ [e[15]]     ,[e[16]],.......|..,[e[n]]             ]
                                                #          y_train (80%)          |     y_test (20%) 
        #----------------------------------------------------------------


        #======== 2.TRAIN a LSTM model (4 LSTM layers + 1 output layer): ========
        # Compile & summarize it
        lstm_model = Sequential()

        #----------- Model's Structure ---------------------------------
        #////// Empirical Optimization from Testings //////
        #  1.Neurons 50->25 doesn't help (overfitting was suspected)
        #**2.Neurons 50->100 helps (underfitting was suspected)
        #**3.+BiLSTM & Changed the stru. help: [so far] LSTM100-LSTM100-LSTM100-BiLSTM100-Dense1
        #  4.+Batch/Layer-Normalization doesn't sig. help
        #**5.Changing to compile(optimizer='RMSprop', loss='huber') helps
        #**6.+shuffle=False helps
        #  7.Dropout 0.2->0.8 doesn't help
        #**8.Dropout 0.0 helps
        #xx9.biL(100)-biL(100)-biL(100)-Lstm(200)-dense(1)
        #xx10.dense during the journey
        #////// Already saved all the results' pics named <testDescription>.png & noted 'know-how' //////  
        
        # 1st LSTM layer with dropout
        #lstm_model.add(Bidirectional(LSTM(100, return_sequences=True), input_shape=(window_size, 5)))
            ### Learning Pattern: <-- and --> (no for real-time price trend prediction)
        lstm_model.add(LSTM(100, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
                #(50 neurons, LSTM output = seq,
                #input_shape= (no.of time steps, of feature(=5 cols to use; 'li_open',..'li_vol.')
                #X.shape (3D)= (629, 100, 5)
            ### Learning Pattern: --> time t
        #lstm_model.add(LayerNormalization())
        #lstm_model.add(Dropout(0.2))
            #Helps prevent overfitting by disabling 20%*neurons during training            
                                        
        # 2nd LSTM layer with dropout
        #lstm_model.add(Bidirectional(LSTM(100, return_sequences=True), input_shape=(window_size, 5)))
        lstm_model.add(LSTM(100, return_sequences=True))
        #lstm_model.add(LayerNormalization())
        #lstm_model.add(Dropout(0.2))

        # 3rd LSTM layer with dropout
        #lstm_model.add(Bidirectional(LSTM(100, return_sequences=True), input_shape=(window_size, 5)))
        lstm_model.add(LSTM(100, return_sequences=True))
        #lstm_model.add(LayerNormalization())
        #lstm_model.add(Dropout(0.2))

        # 4th LSTM layer with dropout
        lstm_model.add(Bidirectional(LSTM(100), input_shape=(window_size, 5)))
        #lstm_model.add(LSTM(100))    #return_sequences=False cuz it's the last recurrent layer
        #lstm_model.add(LayerNormalization())
        #lstm_model.add(Dropout(0.2))

        # Output layer 
        lstm_model.add(Dense(1))    #Add a Dense(fully connected)output layer with 1 neuron
                                    #It connects all outputs from the previous LSTM layer
        lstm_model.compile(optimizer='RMSprop', loss='huber')
                                    #RMSprop: designed for LSTM with smoother convergence in time series models
                                    #huber: less sensi. to outliers. It behaves= MSE for small errors (squared) 
                                    #       &= MAE for larger errors (linear)
        #lstm_model.compile(optimizer='adam', loss='mean_squared_error')
                                    #adam (smart gradient-based): popular for time series & NN
                                    #'MSE': loss func. telling the model how wrong it is during training
        lstm_model.summary()
        print("*** Optimizer: ", lstm_model.optimizer.__class__.__name__)
        print("*** Loss Function: ", lstm_model.loss)
        #--------------------------------------------------------------

        # Train it
        print("////////// Training the model, please wait. ////////////////")
        #X: Early Stopping | save->load_model() | 
        
        lstm_model.fit(X_train, y_train, epochs=30, batch_size=24, verbose=0, shuffle=False)
            #y_train: e.g., next closing price after each sequence
            #epochs=30 : The model iterates over the entire dataset 30 times -> learn better but too much=overfitting
            #       an epoch contains <?> batches
            #batch_size=n : The model processes 'n samples (data points) at once' ('..' = a batch)
            #       before the model's weights are updated based on the avg loss across the entire batch
            #       (accum. gradients from the entire batch for the LSTM case) calculated for those samples
            #  So <?> = total samples (data points) / batch_size
            #  n: less= handling 'unseen' better & slower convergence | more= 'opposite'
            #verbose: controls the output display > 1: Progress bar | 0: Show nothing

            # ****** > Obsidian ******  

            #Output E.g.:
                #Epoch 1/30
                #250/250 [==============================] - 3s 6ms/step - loss: 0.0041

        #======== 3.TEST the LSTM model & Reshape: ========
        x_last_seq = data_normalized[-window_size:]                         #Shape 3D= (w_s, 5) | [ ..,[e[n-1-100]-e[n-1]] ] }See above
        x_last_seq = x_last_seq.reshape((1, window_size, len(cols_to_use))) #Reshape -> (1, w_s, 5)= (batch_size, len(seq), feature)
                                       
        # Make price trend prediction for the next n=input days (+Reshape)
        y_pred_vals = [] #@@@
        x_current_input = x_last_seq.copy() #Shape: See above 

        while True:
            print("No.of days to be predicted (<= no.of days to be used // 4)-")
            print("based on all the conditions & testings. It should= 90 or 25: ", end="") 
            dayPredicted = int(input().strip())
            if 0 < dayPredicted <= window_size//4:
                break
            else:
                print("Improper input! Please try again.")
                continue

        print("////////// Predicting the price trend, please wait. ////////////////")
        for _ in range(dayPredicted):
            #### Predict 'y_next_pred'  //Shape 2D= (-1,1)
            y_next_pred = lstm_model.predict(x_current_input, verbose=0)  #** y_next_pred: np.array( [[0.17280594]] )
            # Add to 'y_pred_vals'
            y_pred_vals.append(y_next_pred[0][0])                         #** y_next_pred[0][0]: 0.17280594

            #----------- Former ---------------
            # Reshape to 3D: (1,1,1)
            #y_next_pred_reshaped = np.reshape(y_next_pred, (1, 1, 1))  #-> y_next_pred: np.array( [[[0.17280594]]] )
            #----------------------------------

            # Concatenate properly
            last_known_features = x_current_input[0, -1, :].copy() #To slice ('1', 'last day of w_s', '5 features(=cols to use)')
                                                                   #-> Get '1D array of shape (5,)'= [open_val,..,vol_val] 
            next_input_features = last_known_features.copy()       #'last_known' -> 'next_input'
            next_input_features[cols_to_use.index('li_close')] = y_next_pred[0][0] #Keep a y_next_pred val (x.xx) in next_input['li_close']

            # Reshape 'y_next_pred' from 2D to 3D:(1,1,5) to be matched with the 3D struc.
            y_next_pred_reshaped = next_input_features.reshape(1, 1, len(cols_to_use))
            # Slice (1, [day1-cut,day2,..day100], 1)
            x_cur_input_sliced = x_current_input[:, 1:, :]
            # Add arr. x_cur_sliced (1,99,5) <- y_next_pred_re (1,1,5). So we get (1, [day2,..,day100, y_next_pred_re(=day101)], 5)
            next_input = np.concatenate( (x_cur_input_sliced, y_next_pred_reshaped), axis=1 )

            # Get 'x_current_input'
            x_current_input = next_input
             

        # Inverse Transform: Convert from the normalized back to the original scale (= real prices)

        #----------- Former ---------------
                                        # np.array: Ensure y_pred_vals's format fits 'inverse_transform()'
                                        # .reshape(-1,1): Converts it to 2D shape:(n,1) as required
        #y_vals_actual_in = scaler.inverse_transform(y_train.reshape(-1, 1))                    
        #----------------------------------

        ## 'Train part' to be plotted | Fixed 'Add arr.(1,99,5) <- (1,1,1-must=5)' error
        # Create dummy to solve the error    //To slice d_n [100:to n] of 5 features | dum's shape is 2D= (728-1-100, 5)
        dum_y_vals_actual = data_normalized [ window_size : window_size + len(y_train) ].copy()

                          #//To slice dum [all rows of d_n['li_close']] <- y_train (1D=(627,)) | dum's shape is 2D= (728-1-100, 5)
        dum_y_vals_actual [:, cols_to_use.index('li_close')] = y_train

                          #To inverse-transform only dum [all rows of d_n['li_close']] from dum whose shape is 2D= (728-1-100, 5)
                          # and this shape satisfies 'scaler' (also see above) expecting 2D= (rows(=627), 5)
        y_vals_actual_in = scaler.inverse_transform(dum_y_vals_actual)[:, cols_to_use.index('li_close')]  #@@@

        ## 'Future part' to be plotted | Fixed 'Add arr.(1,99,5) <- (1,1,1)' error
                            #Select $'the last row' (Shape 1D= (5,) (=[x,y,z,..]) & != 2D= (1,5))
                            #np.tile(): Repeat $'that row' n times | (n,1) which is (no.of row, no.of col)
                            #1: as-is; no repetition across col
        dummy_preds = np.tile( data_normalized[-1], (len(y_pred_vals), 1) )     #Shape: (future_days, 5)
        #X: dummy_preds = np.zeros((len(y_pred_vals), len(cols_to_use))) #Create an 0 array (row no., col no.)
        dummy_preds[:, cols_to_use.index('li_close')] = y_pred_vals 
                            
        y_pred_vals_in = scaler.inverse_transform(dummy_preds)[:, cols_to_use.index('li_close')]    #@@@    

        #---------- Former Manipulation --------------------------------
        #y_pred_vals_in = scaler.inverse_transform(np.array(y_pred_vals).reshape(-1, 1)) 

        #y_train_reshaped = scaler.inverse_transform(y_train.reshape(-1, 1)) 
        #y_test_reshaped = scaler.inverse_transform(y_test.reshape(-1, 1))  #Shape 2D= (n_samples, 1)
        #y_pred = lstm_model.predict(X_test)
        #y_pred_reshaped = scaler.inverse_transform(y_pred.reshape(-1, 1))  #Shape 2D= (n_samples, 1)

        #--- Model Evaluation ---
        #rmse = np.sqrt(mean_squared_error(y_test_reshaped, y_pred_reshaped))
        #mae = mean_absolute_error(y_test_reshaped, y_pred_reshaped)
        #----------------------------------------------------------------


        #======== 4.VISUALIZE the outputs: ========

        #--- Get proper time vals | .iloc: select rows/cols by idx in DataFrame ---
        ### 'dt_actual' starts at li_time[window_size] due to 'Create seq' & the other logics  
        dt_actual = data['li_time'].iloc[window_size : window_size + len(y_vals_actual_in)]
        dt_pred = pd.date_range(start= dt_actual.iloc[-1] + pd.Timedelta(days=1), periods= len(y_pred_vals_in), freq='B')
                #freq='B' (Busi.day skipping weekend) //X: D
        stVis.getPredictedPriceTrend(stName, dt_actual, dt_pred, y_vals_actual_in, y_pred_vals_in)
        print("---------- Price Trend Prediction Visualized! ----------")

        print("Run more? (y or n): ", end="")
        again = input().strip().lower()
        if again == "y":
            isAgain = True
            print("------------------------------------")
        elif again == "n":
            isAgain = False
            print("====================================")
        else:
            print("Invalid input! Please try again.")

#        except:
#            print("Something wrong, please check 'stockLSTM.py'")
#            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
#            continue

# ================= END OF PROGRAM =================
