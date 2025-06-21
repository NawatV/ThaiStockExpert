import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
#------ LSTM model ------
from keras.layers import LSTM, Dropout, SimpleRNN, Dense
from keras.models import Sequential
#------ Visualization ------
import matplotlib.pyplot as plt

#======= LSTM:Predict using 'li_close' & plot stock's price trend (still inaccurate)  ======= 

#============= 1.DATA Part: =============
print("Please wait...")
# Read csv & get headers             
                           ### PATH !!!
data = pd.read_csv("C://Users//LENOVO//Desktop//thai_stock_expert//output//1_amata_LSTM_addRows.csv")


# Normalize data
#--- ->numeric ---
cols_to_use = ['li_open','li_high','li_low','li_close','li_volume'] #<<<< Partial | X: li_time
for col in cols_to_use:
    data[col] = pd.to_numeric(data[col], errors='coerce') #->NaN if inconvertible
data = data.dropna(subset = cols_to_use) #Drop rows with NaNs (e.g. row 'col names')

#--- Normalize to {0,1} --- 
scaler = MinMaxScaler(feature_range=(0,1))

#--- Handle 'Found array with 0 sample(s) (shape=(0, 1))' ---
data_close_normalized = scaler.fit_transform(data[['li_close']]) #X: data[cols_to_use]
#data[['li_close']] returns a 2D DataFrame: shape=(n_rows, 1) 

#data_normalized_df = pd.DataFrame(data_close_normalized, columns = data.columns) | Convert back to DataFrame
#data['li_time'] = pd.to_datetime(data['li_time'], errors='coerce') | str -> datetime


# Create seq: windowSize=15, outputSize=1
def create_sequences(data, window_size):
    X, y = [], []
    for i in range(len(data) - window_size):
        X.append( data[i:(i + window_size)] ) # X=[ [e[0]-e[14]],[e[1]-e[15]],..,[e[n-1-15]-e[n-1]] ]
        y.append( data[i + window_size] )     # y=[ [e[15]]     ,[e[16]],.......,[e[n]]             ]
    return np.array(X), np.array(y)

window_size = 15
X, y = create_sequences(data_close_normalized, window_size)
print(X.shape)  ## Shape = (714,15,1) cuz from i=15(ele 16 due to w_s=15) to i=728(ele 729)
                #X: 'X = X.reshape((X.shape[0], X.shape[1], 1))' - look above
print(y.shape)  ## Shape = (714, 1)


# All= training data
X_train = X
y_train = y

# Split 'X, y' into training & testing sets   
#split = int(0.8 * len(X))
#X_train, X_test = X[:split], X[split:] # X=[ [e[0]-e[14]],[e[1]-e[15]],. | .,[e[n-1-15]-e[n-1]] ]
                                        #          X_train (80%)          |     X_test (20%)       
#y_train, y_test = y[:split], y[split:] # y=[ [e[15]]     ,[e[16]],.......|..,[e[n]]             ]
                                        #          y_train (80%)          |     y_test (20%) 


#======== 2.TRAIN a LSTM model (4 LSTM layers + 1 output layer): ========
# Compile & summarize it
lstm_model = Sequential()

# 1st LSTM layer with dropout
lstm_model.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
            #(50 neurons, LSTM output = seq,               (no.of time steps, of feature(=1('Close')) | X.shape=(714,15,1)
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


#======== 3.TEST the LSTM model: ========
x_last_seq = data_close_normalized[-window_size:]       #Shape = (15, 1) | [ ..,[e[n-1-15]-e[n-1]] ] }See above
x_last_seq = x_last_seq.reshape((1, window_size, 1))    #Reshape -> (1, 15, 1)


# Make price trend prediction for the next n=input days
y_pred_vals = [] #@@@
current_input = x_last_seq.copy() #Shape= (1, 15, 1) =[batch_size, len(seq), feature]
print("Predict for the next (days): ", end="")
n = int(input())
for _ in range(n):
    ## Predict 'y_next_pred'   | Shape 2D: (-1,1)
    y_next_pred = lstm_model.predict(current_input)             #** y_next_pred: np.array( [[0.17280594]] )
    # Add to 'y_pred_vals'
    y_pred_vals.append(y_next_pred[0][0])                       #** y_next_pred[0][0]: 0.17280594
    # Reshape to 3D: (1,1,1)
    y_next_pred_reshaped = np.reshape(y_next_pred, (1, 1, 1))   #-> y_next_pred: np.array( [[[0.17280594]]] )
    # Concatenate properly           To slice (1, [day1-cut,day2,..day15], 1), To add 'y_next_pred_re.'
                                   #So we get (1, [day2,.., day15, y_next_pred_re(=day16)], 1)
    next_input = np.concatenate((current_input[:, 1:, :], y_next_pred_reshaped), axis=1)
    # Get 'current_input'
    current_input = next_input
     

# Perform 'inverse transform' = Convert from the normalized back to the original scale (= real prices)
                                           #np.array: Ensure y_pred_vals's format is fit to 'inverse_transform()'
                                           #.reshape(-1,1): Converts it to 2D:shape=(n,1) as required
y_pred_vals_actual = scaler.inverse_transform(np.array(y_pred_vals).reshape(-1, 1)) #@@@
#--- All past values ---
y_vals_actual = scaler.inverse_transform(y_train.reshape(-1, 1))                    


#======== 4.VISUALIZE the outputs: ========
# Plot the outputs
plt.figure(figsize=(10,6))

plt.plot(range(len(y_vals_actual)), y_vals_actual, label='Actual', color='black')
plt.plot(range(len(y_vals_actual), len(y_vals_actual) + len(y_pred_vals_actual)), y_pred_vals_actual,
    label='Predicted Trend', color='blue') #linestyle='--'
    #Actual prices are plotted from index 0 to 713
    #Predicted price trend is plotted from index 714 to 714+n (depending on n)
#plt.plot(y_vals_actual, label='Actual', color='black')
#plt.plot(y_pred_vals_actual, label='Predicted Trend', linestyle='--', color='blue')
plt.axvline(x=len(y_vals_actual)-1, color='red', linestyle=':', label='Prediction Started!')

plt.title('Actual & "Predicted Trend"')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.show()
