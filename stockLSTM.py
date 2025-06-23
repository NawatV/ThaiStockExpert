import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
#------ LSTM model ------
from keras.layers import LSTM, Dropout, SimpleRNN, Dense
from keras.models import Sequential
#------ Visualization ------
import matplotlib.pyplot as plt

#======= Optimizing attempt (= 100->25 days, _cutLatest.csv) ||
#        LSTM:P&P using 5 col.s ('li_open',..,'li_vol.') (accuracy-better) =======

#============= 1.DATA Part: =============
### Shape 2D= (no. of row, no. of col)
### Shape 3D= (no. of sample(=row), no. of time_step(=window_size), no. feature(=column to use))

print("Please wait...")
# Read csv & get headers             
                           ### PATH !!!
data = pd.read_csv("C://Users//LENOVO//Desktop//thai_stock_expert//output//1_pttep_LSTM_cutLatest.csv")


# Normalize data
#--- ->numeric ---
cols_to_use = ['li_open','li_high','li_low','li_close','li_volume'] #All essen.static col.s | X: li_time
for col in cols_to_use:
    data[col] = pd.to_numeric(data[col], errors='coerce')           #->NaN if inconvertible
data = data.dropna(subset = cols_to_use)                            #Drop rows with NaNs (e.g. row 'col names')

#--- Normalize data(=5 col) to {0,1} --- 
scaler = MinMaxScaler(feature_range=(0,1))
data_normalized = scaler.fit_transform(data[cols_to_use]) #Shape 2D= (n_rows, 5)
                                                          #Data=
                                                            #[0.41 0.52 0.39 0.44 0.17]
                                                            #... //e.g.
    #data[['li_close']] returns a 2D DataFrame: shape 2D= (n_rows, 1) 
    #data_normalized_df = pd.DataFrame(data_close_normalized, columns = data.columns) | Convert back to DataFrame
    #data['li_time'] = pd.to_datetime(data['li_time'], errors='coerce') | str -> datetime


# Create seq 
def create_sequences(data_normalized, window_size):
    X, y = [], []
    for i in range(len(data_normalized) - window_size):
        X.append( data_normalized[i:(i + window_size)] )                           # X=[ [5e[0]-5e[99]],[5e[1]-5e[100]],..,[5e[n-1-100]-5e[n-1]] ]
        y.append( data_normalized[i + window_size, cols_to_use.index('li_close')] )# y=[ [5e[100]]     ,[5e[101]],.......,[5e[n]]             ]
    return np.array(X), np.array(y)

#### Based upon testings, optimal: USE 1. {5 COL} &
####                                   2. {[4:1] 'window_size= 100d' to predict the 'outputSize= 25-d' price trend}  <<<<
####      with '_cutLatest.csv' due to 1 incontinuous-date data row by SET API                                    <<<<
window_size = 100 
X, y = create_sequences(data_normalized, window_size)
print("X.shape:", X.shape)  ## Shape 3D= (allRows -w_s, w_s, 5) = (628, 100, 5) //i=100(ele 16 due to w_s=100) to i=728(ele 729)
print("y.shape:", y.shape)  ## Shape 1D= (allRows -w_s,) = (628,)


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

# 1st LSTM layer with dropout
lstm_model.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    #(50 neurons, LSTM output = seq,
    #input_shape= (no.of time steps, of feature(=5 cols to use; 'li_open',..'li_vol.')
    #X.shape (3D)= (629, 100, 5) 
                           
lstm_model.add(Dropout(0.2))
            #Helps prevent overfitting by disabling 20%*neurons during training            
                                
# 2nd LSTM layer with dropout
lstm_model.add(LSTM(50, return_sequences=True))
lstm_model.add(Dropout(0.2))

# 3rd LSTM layer with dropout
lstm_model.add(LSTM(50, return_sequences=True))
lstm_model.add(Dropout(0.2))

# 4th LSTM layer with dropout
lstm_model.add(LSTM(50))    #return_sequences=False cuz it's the last recurrent layer
lstm_model.add(Dropout(0.2))

# Output layer
lstm_model.add(Dense(1))    #Adds a Dense(fully connected)output layer with 1 neuron
                            #It connects all outputs from the previous LSTM layer
lstm_model.compile(optimizer='adam', loss='mean_squared_error')
                            #adam (smart gradient-based): popular for time series & NN
                            #'MSE': loss func. telling the model how wrong it is during training
lstm_model.summary()

# Train it
lstm_model.fit(X_train, y_train, epochs=30, batch_size=24, verbose=1)
    #y_train: e.g., next closing price after each sequence
    #epochs: The model iterates over the entire dataset 30 times -> learn better but too much=overfitting
    #batch_size: The model processes the data in mini-batches of 24 samples
        #Each weight update is done after processing one batch.
        #lower val= more updates -> learn better | higher val= faster training but might skip nuances
    #verbose: controls the output display > 1: Progress bar

    #Output E.g.:
        #Epoch 1/30
        #250/250 [==============================] - 3s 6ms/step - loss: 0.0041


#======== 3.TEST the LSTM model & Reshape: ========
x_last_seq = data_normalized[-window_size:]                         #Shape 3D= (w_s, 5) | [ ..,[e[n-1-100]-e[n-1]] ] }See above
x_last_seq = x_last_seq.reshape((1, window_size, len(cols_to_use))) #Reshape -> (1, w_s, 5)= (batch_size, len(seq), feature)
                               
# Make price trend prediction for the next n=input days (+Reshape)
y_pred_vals = [] #@@@
x_current_input = x_last_seq.copy() #Shape: See above 
print("Predict for the next (days): ", end="")                  #<<<< Reorganize customizing allowance later 
n = int(input())
for _ in range(n):
    #### Predict 'y_next_pred'  //Shape 2D= (-1,1)
    y_next_pred = lstm_model.predict(x_current_input)           #** y_next_pred: np.array( [[0.17280594]] )
    # Add to 'y_pred_vals'
    y_pred_vals.append(y_next_pred[0][0])                       #** y_next_pred[0][0]: 0.17280594

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
# Create dummy to solve the error    //To slice d_n [100:to n] of 5 features | dum's shape is 2D= (729-1-100, 5)
dum_y_vals_actual = data_normalized [ window_size : window_size + len(y_train) ].copy()

                  #//To slice dum [all rows of d_n['li_close']] <- y_train (1D=(628,)) | dum's shape is 2D= (729-1-100, 5)
dum_y_vals_actual [:, cols_to_use.index('li_close')] = y_train

                  #To inverse-transform only dum [all rows of d_n['li_close']] from dum whose shape is 2D= (729-1-100, 5)
                  # and this shape satisfies 'scaler' (also see above) expecting 2D= (rows(=628), 5)
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
#y_test_reshaped = scaler.inverse_transform(y_test.reshape(-1, 1))
#y_pred = lstm_model.predict(X_test)
#y_pred_reshaped = scaler.inverse_transform(y_pred.reshape(-1, 1))
#----------------------------------------------------------------


#======== 4.VISUALIZE the outputs: ========
# Plot the outputs
plt.figure(figsize=(10,6))
                                    ##'Train part' (actual prices) to be plotted from idx 0-713
plt.plot(range(len(y_vals_actual_in)), y_vals_actual_in, label='Actual', color='black')
                                    ##'Future part'(predicted price trend) to be plotted from idx 714- 714+n (up to n)
plt.plot(range(len(y_vals_actual_in), len(y_vals_actual_in) + len(y_pred_vals_in)), y_pred_vals_in,
                                                   label='Predicted Trend', color='blue') #linestyle='--'
plt.axvline(x=len(y_vals_actual_in)-1, color='red', linestyle=':', label='Prediction Started!')

#---------- Former Manipulation --------------------------------
#plt.plot(range(len(y_train_reshaped)), y_train_reshaped, label='Actual', color='black')
#plt.plot(range(len(y_train_reshaped), len(y_train_reshaped) + len(y_test_reshaped)),
#                                    y_test_reshaped, label='Actual', color='black')
#plt.plot(range(len(y_train_reshaped), len(y_train_reshaped) + len(y_pred_reshaped)),
#                                    y_pred_reshaped, label='Actual', linestyle='--', color='red')
#plt.axvline(x=len(y_train_reshaped)-1, color='black', linestyle=':', label='Prediction Started!')
                  #Starting Point
#----------------------------------------------------------------

plt.title('Actual & "Predicted Trend"')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.show()
