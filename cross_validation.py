import numpy as np
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_percentage_error, r2_score, mean_squared_error, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor, StackingRegressor, AdaBoostRegressor
from sklearn.linear_model import BayesianRidge, ElasticNet, Lasso, TheilSenRegressor
from sklearn.svm import SVR
from sklearn.model_selection import RandomizedSearchCV
from xgboost import XGBRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.utils import shuffle
import random
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold, StratifiedKFold
from plot_histogram import draw_histo
from sklearn.utils import shuffle
import tensorflow as tf
from tensorflow import keras
from keras import layers
from keras import optimizers as opti
from keras import losses
from keras.models import Sequential
from keras.layers import Dense, Dropout, MaxPooling1D, Flatten, Convolution1D, LSTM, Activation
from keras.layers import Dropout, Flatten, Conv2D, MaxPooling2D, BatchNormalization
from tensorflow_addons.metrics import r_square
from keras.callbacks import EarlyStopping

def cleanOutlier(x, y):
    # Gid rid of y values exceeding 2 std value
    y_std = np.std(y)
    y_median = np.median(y)
    # quartile_1 = np.round(np.quantile(y, 0.25), 2)
    # quartile_3 = np.round(np.quantile(y, 0.75), 2)
    # # Interquartile range
    # iqr = np.round(quartile_3 - quartile_1, 2)
    range_ = 2
    up_boundary = np.mean(y) + range_ * y_std 
    low_boundary = np.mean(y) - range_ * y_std 
    
    remaining = np.where(y <= up_boundary)[0]
    y_new = y[remaining]
    x_new = x[remaining]
    remaining2 = np.where(y_new >= low_boundary)[0]
    y_new2 = y_new[remaining2]
    x_new2 = x_new[remaining2]

    return x_new2, y_new2

def normalizationX(array_):
    # array should be 2-D array
    # array.shape[0]: amount of samples
    # array.shape[1]: amount of features
    array = np.copy(array_)
    minValue = []
    maxValue = []
    for featureIdx in range(0, array_.shape[1]):
        if featureIdx == array_.shape[1] - 1: # Location has been normalized before
            break
        mini = np.amin(array[:, featureIdx])
        maxi = np.amax(array[:, featureIdx])
        minValue.append(mini)
        maxValue.append(maxi)
        array[:, featureIdx] = (array[:, featureIdx] - mini) / (maxi - mini)
        
    
    return array, np.array(minValue), np.array(maxValue)

def normalization_signal(signals_lst):
    minValue = []
    maxValue = []
    signals_lst_channel = np.moveaxis(signals_lst, -1, 0) # [n_samples, n_length, n_channels] => [n_channels, n_samples, n_length]
    signals_lst_new = np.copy(signals_lst_channel)
    for channel_idx, channel_signals in enumerate(signals_lst_channel):
        mini = np.amin(channel_signals)
        maxi = np.amax(channel_signals)
        signals_lst_new[channel_idx] = (channel_signals - mini) / (maxi - mini)
    signals_lst_new = np.moveaxis(signals_lst_new, 0, -1)    # [n_channels, n_samples, n_length] => [n_samples, n_length, n_channels]
    return signals_lst_new, np.array(minValue), np.array(maxValue)
    
    
def normalizationY(array_):
    # array should be 1-D array
    # array.shape: amount of samples
    array = np.copy(array_)
    mini = np.amin(array)
    maxi = np.amax(array)

    array = (array - mini) / (maxi - mini)
        
    return array, mini, maxi

def datasetCreating(x_, y_):
    xTrain, xTest, yTrain, yTest = train_test_split(x_, y_, test_size=0.1, random_state=75)

    return xTrain, yTrain, xTest, yTest

def class_labeling(y, y_thresholds):
    y_class = np.copy(y)
    for sample_idx, sample_value in enumerate(y):
        for split_idx, threshold in enumerate(y_thresholds):
            if sample_value < threshold:
                sample_class = split_idx
                break
            else:
                if split_idx == len(y_thresholds)-1: # when it exceeds the biggerest value
                    sample_class = len(y_thresholds)
                continue
        y_class[sample_idx] = sample_class
    return y_class

def show_train_history_NN(history_, loss, metric_name_tr, metric_name_val, fold_idx):
    loss_tr = history_.history['loss']
    loss_val = history_.history['val_loss']
    metric_tr = history_.history[metric_name_tr]
    metric_val = history_.history[metric_name_val]
    plt.figure(figsize=(16, 6))
    ax1 = plt.subplot(121)
    ax1.plot(loss_tr, '-o', label='train', lw=5)
    ax1.plot(loss_val, '-o', label='val', lw=5)
    ax1.set_ylabel(f'{loss}', fontsize=24)
    ax1.set_xlabel('Epoch', fontsize=24)
    ax1.tick_params(axis='both', which='major', labelsize=20)
    ax1.legend(loc='best', fontsize=20)
    ax1.grid(True)
    # ax1.set_ylim((0, 60))

    
    ax2 = plt.subplot(122)
    ax2.plot(metric_tr, '-o', label='train', lw=5)
    ax2.plot(metric_val, '-o', label='val', lw=5)
    ax2.set_ylabel(f'{metric_name_tr}', fontsize=24)
    ax2.set_xlabel('Epoch', fontsize=24)
    ax2.tick_params(axis='both', which='major', labelsize=20)
    ax2.grid(True)
    ax2.legend(loc='best', fontsize=20)
    # ax2.set_ylim((0, 10))
    plt.suptitle(f'fold {fold_idx+1} Train History', fontsize=26)
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    plt.show()
    plt.close()

def show_train_history_NN_onlyTrain(history_, loss, metric_name_tr, fold_idx):
    loss_tr = history_.history['loss']
    metric_tr = history_.history[metric_name_tr]
    plt.figure(figsize=(16, 6))
    ax1 = plt.subplot(121)
    ax1.plot(loss_tr, '-o', label='train', lw=5)
    ax1.set_ylabel(f'{loss}', fontsize=24)
    ax1.set_xlabel('Epoch', fontsize=24)
    ax1.tick_params(axis='both', which='major', labelsize=20)
    ax1.legend(loc='best', fontsize=20)
    ax1.grid(True)
    # ax1.set_ylim((0, 60))

    
    ax2 = plt.subplot(122)
    ax2.plot(metric_tr, '-o', label='train', lw=5)
    ax2.set_ylabel(f'{metric_name_tr}', fontsize=24)
    ax2.set_xlabel('Epoch', fontsize=24)
    ax2.tick_params(axis='both', which='major', labelsize=20)
    ax2.grid(True)
    ax2.legend(loc='best', fontsize=20)
    # ax2.set_ylim((0, 10))
    plt.suptitle(f'fold {fold_idx+1} Train History', fontsize=26)
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    plt.show()
    plt.close()

class cross_validate:
    def __init__(self, x, y, qualityKind, normalized):
        self.qualityKind = qualityKind
        self.normalized = normalized
        self.x, self.y = cleanOutlier(x, y)
        
        if self.normalized == 'xy':
            self.x, self.xMin, self.xMax = normalizationX(self.x)
            self.y, self.yMin, self.yMax = normalizationY(self.y)
            self.xTrain, self.yTrain, self.xTest, self.yTest = datasetCreating(self.x, self.y)

        elif self.normalized == 'x':
            self.x, self.xMin, self.xMax = normalizationX(self.x)
            self.xTrain, self.yTrain, self.xTest, self.yTest = datasetCreating(self.x, self.y)

        else:
            self.xTrain, self.yTrain, self.xTest, self.yTest = datasetCreating(self.x, self.y)

        
        self.kfold_num = 5
    
    def show_train_history(self, history_, category, fold_idx):
        ylim = [-0.03, 0.32]
        plt.figure(figsize=(16, 6))
        ax1 = plt.subplot(121)
        # category[0]=mape
        ax1.plot(history_['validation_0'][category[0]], lw=4, label='train')
        ax1.plot(history_['validation_1'][category[0]], lw=4, label='val')
        ax1.set_ylabel(f'{category[0]}', fontsize=24)
        ax1.set_xlabel('Epoch', fontsize=24)
        ax1.tick_params(axis='both', which='major', labelsize=20)
        ax1.legend(loc='best', fontsize=20)
        ax1.grid(True)
        # ax1.set_ylim(-0.03, 0.32)

        
        ax2 = plt.subplot(122)
        ax2.plot(history_['validation_0'][category[1]], lw=4, label='train')
        ax2.plot(history_['validation_1'][category[1]], lw=4, label='val')
        ax2.set_ylabel(f'{category[1]}', fontsize=24)
        ax2.set_xlabel('Epoch', fontsize=24)
        ax2.tick_params(axis='both', which='major', labelsize=20)
        ax2.legend(loc='best', fontsize=20)
        ax2.grid(True)
        # ax2.set_ylim(-0.03, 0.52)

        plt.suptitle(f'fold {fold_idx+1} Train History', fontsize=26)
        plt.tight_layout()
        plt.subplots_adjust(top=0.88)
        plt.show()
        plt.close()
    
    def plot_metrics_folds(self, train_lst, val_lst):
        x = np.arange(1, self.kfold_num+1, 1)
        train_lst, val_lst = train_lst.T, val_lst.T
        metrics = ['MAPE (%)', 'R2'] 
        plt.figure(figsize=(16, 6))
        ax1 = plt.subplot(121)
        ax1.plot(x, train_lst[0], '-o', label='train', lw=5, color='seagreen')
        ax1.plot(x, val_lst[0], '-o', label='val', lw=5, color='brown')
        ax1.set_ylabel(f'{metrics[0]}', fontsize=24)
        ax1.set_xlabel('Fold', fontsize=24)
        ax1.tick_params(axis='both', which='major', labelsize=20)
        ax1.legend(loc='best', fontsize=20)
        # ax1.set_title(f'{metrics[0]}', fontsize=26)
        ax1.grid(True)
        ax1.set_ylim((0, 40))
        
        ax2 = plt.subplot(122)
        ax2.plot(x, train_lst[1], '-o', label='train', lw=5, color='seagreen')
        ax2.plot(x, val_lst[1], '-o', label='val', lw=5, color='brown')
        ax2.set_ylabel(f'{metrics[1]}', fontsize=24)
        ax2.set_xlabel('Fold', fontsize=24)
        ax2.tick_params(axis='both', which='major', labelsize=20)
        ax2.legend(loc='best', fontsize=20)
        # ax2.set_title(f'{metrics[1]}', fontsize=26)
        ax2.grid(True)
        ax2.set_ylim((0, 1.1))
        # ax2.set_ylim((0, 1.1))
        plt.suptitle(f'Cross Validation', fontsize=26)
    
    def cross_validate_XGB(self):
        xTrain, yTrain = shuffle(self.xTrain, self.yTrain, random_state=75)
        kf = KFold(n_splits=self.kfold_num)
        skf = StratifiedKFold(n_splits=self.kfold_num)
        fitness_lst = []
        train_metric_lst = np.zeros((self.kfold_num, 2))
        val_metric_lst = np.zeros((self.kfold_num, 2))
        model_lst = []
        for idx, (train_idx, val_idx) in enumerate(kf.split(xTrain)):
            
            metric = 'mape'
            metrics = ['mape', 'rmse']
            # metrics = [mean_absolute_percentage_error, r2_score]
            model = XGBRegressor(eval_metric=metrics, importance_type='total_gain', disable_default_eval_metric=True)
            x_train = xTrain[train_idx]
            y_train = yTrain[train_idx]
            x_val = xTrain[val_idx]
            y_val = yTrain[val_idx]
            evalset = [(x_train, y_train), (x_val, y_val)]
            model.fit(x_train, y_train, eval_set=evalset, verbose=False)
            model_lst.append(model)
            yValPredicted = model.predict(x_val)
            results = model.evals_result()
            self.show_train_history(results, metrics, idx)
            yTrainPredicted = model.predict(x_train)
            r2_train = r2_score(y_train, yTrainPredicted)
            mape_train = mean_absolute_percentage_error(y_train, yTrainPredicted) * 100
            train_metric_lst[idx] = (np.array([mape_train, r2_train]))
    
            r2_val = r2_score(y_val, yValPredicted)
            mape_val = mean_absolute_percentage_error(y_val, yValPredicted) * 100
            val_metric_lst[idx] = np.array([mape_val, r2_val])
            draw_histo(y_val, f'Histogram of Output in Fold {idx+1}', 'seagreen', 0)
        self.plot_metrics_folds(train_metric_lst, val_metric_lst)
        try:
            highest_valR2_idx = np.where(val_metric_lst[:, 1] == np.max(val_metric_lst[:, 1]))[0][0]
        except:
            print(val_metric_lst[:, 1])
            highest_valR2_idx = 0
        best_model = model_lst[highest_valR2_idx]
        return best_model
    
    def cross_validate_kNN(self):
        xTrain, yTrain = shuffle(self.xTrain, self.yTrain, random_state=75)
        kf = KFold(n_splits=self.kfold_num)
        fitness_lst = []
        train_metric_lst = np.zeros((self.kfold_num, 2))
        val_metric_lst = np.zeros((self.kfold_num, 2))
        model_lst = []
        for idx, (train_idx, val_idx) in enumerate(kf.split(xTrain)):
            metric = 'mape'
            metrics = ['mape', 'rmse']
            # metrics = [mean_absolute_percentage_error, r2_score]
            model = KNeighborsRegressor(n_neighbors=3)
            x_train = xTrain[train_idx]
            y_train = yTrain[train_idx]
            x_val = xTrain[val_idx]
            y_val = yTrain[val_idx]
            evalset = [(x_train, y_train), (x_val, y_val)]
            model.fit(x_train, y_train)
            model_lst.append(model)
            yValPredicted = model.predict(x_val)
            # results = model.evals_result()
            # self.show_train_history(results, metrics, idx)
            yTrainPredicted = model.predict(x_train)
            r2_train = r2_score(y_train, yTrainPredicted)
            mape_train = mean_absolute_percentage_error(y_train, yTrainPredicted) * 100
            train_metric_lst[idx] = (np.array([mape_train, r2_train]))
    
            r2_val = r2_score(y_val, yValPredicted)
            mape_val = mean_absolute_percentage_error(y_val, yValPredicted) * 100
            val_metric_lst[idx] = np.array([mape_val, r2_val])
            # fitness_lst.append(1 - r2_val)
            # fitness_lst.append(mape_val)
            # print(f'\tTrain MAPE: {mape_train:.2f} Val. MAPE: {mape_val:.2f}')
            # print(f'\tTrain R2:   {r2_train:.2f}   Val. R2:   {r2_val:.2f}\n')
        self.plot_metrics_folds(train_metric_lst, val_metric_lst)
        highest_valR2_idx = np.where(val_metric_lst[:, 1] == np.max(val_metric_lst[:, 1]))[0][0]
        best_model = model_lst[highest_valR2_idx]
        return best_model

    def build_ANN(self, loss):
        optimizer = opti.Adam(learning_rate=0.0035)
        model = Sequential()
        model.add(Dense(units=10, input_dim = self.xTrain.shape[1], activation=('relu')))
        model.add(Dense(1, activation='linear'))
        model.compile(loss=loss,
                      optimizer=optimizer,
                      metrics=[r_square.RSquare()])
        return model

    def build_DNN(self, loss):
        # initializer = keras.initializers.GlorotNormal(seed=7)
        optimizer = opti.Adam(learning_rate=0.0035)
        model = Sequential()
        model.add(Dense(units=10, input_dim = self.xTrain.shape[1], activation=('relu')))
        model.add(Dense(units=15, activation=('relu')))
        model.add(Dense(units=1, activation=('linear')))
        model.compile(loss=loss,
                      optimizer=optimizer,
                      metrics=[r_square.RSquare()])
        return model

    def cross_validate_ANN(self):
        xTrain, yTrain = shuffle(self.xTrain, self.yTrain, random_state=79)
        kf = KFold(n_splits=self.kfold_num)
        fitness_lst = []
        train_metric_lst = np.zeros((self.kfold_num, 2))
        val_metric_lst = np.zeros((self.kfold_num, 2))
        loss = "mean_absolute_error"
        model = self.build_ANN(loss)
        model.save_weights('./modelWeights/ANN_initial.h5') 
        for idx, (train_idx, val_idx) in enumerate(kf.split(xTrain)):
            metric = 'mape'
            optimizer = opti.Adam(learning_rate=0.0035)
            callback = EarlyStopping(monitor="loss", patience=30, verbose=0, mode="auto")
            
            x_train = xTrain[train_idx]
            y_train = yTrain[train_idx]
            x_val = xTrain[val_idx]
            y_val = yTrain[val_idx]
            history = model.fit(x_train, y_train, validation_data = (x_val, y_val),
                                epochs=100, batch_size=30, verbose=0)
            model.save_weights(f'./modelWeights/ANN{idx}.h5')  
            show_train_history_NN(history, loss, 'r_square', 'val_r_square', idx)
            yTrainPredicted = model.predict(x_train)
            r2_train = r2_score(y_train, yTrainPredicted)
            mape_train = mean_absolute_percentage_error(y_train, yTrainPredicted) * 100
            train_metric_lst[idx] = (np.array([mape_train, r2_train]))
            yValPredicted = model.predict(x_val)
            r2_val = r2_score(y_val, yValPredicted)
            mape_val = mean_absolute_percentage_error(y_val, yValPredicted) * 100
            val_metric_lst[idx] = np.array([mape_val, r2_val])
            # fitness_lst.append(1 - r2_val)
            fitness_lst.append(mape_val)
            model.load_weights('./modelWeights/ANN_initial.h5')
            
        self.plot_metrics_folds(train_metric_lst, val_metric_lst)
        highest_valR2_idx = np.where(val_metric_lst[:, 1] == np.max(val_metric_lst[:, 1]))[0][0]
        model.load_weights(f'./modelWeights/ANN{highest_valR2_idx}.h5')
        return model
    
    def cross_validate_DNN(self):
        xTrain, yTrain = shuffle(self.xTrain, self.yTrain, random_state=79)
        kf = KFold(n_splits=self.kfold_num)
        fitness_lst = []
        train_metric_lst = np.zeros((self.kfold_num, 2))
        val_metric_lst = np.zeros((self.kfold_num, 2))
        loss = "mean_absolute_error"
        model = self.build_DNN(loss)
        model.save_weights('./modelWeights/DNN_initial.h5') 
        for idx, (train_idx, val_idx) in enumerate(kf.split(xTrain)):
            metric = 'mape'
            optimizer = opti.Adam(learning_rate=0.0005)
            callback = EarlyStopping(monitor="loss", patience=30, verbose=0, mode="auto")
            
            x_train = xTrain[train_idx]
            y_train = yTrain[train_idx]
            x_val = xTrain[val_idx]
            y_val = yTrain[val_idx]
            history = model.fit(x_train, y_train, validation_data = (x_val, y_val),
                                epochs=100, batch_size=30, verbose=0)
            model.save_weights(f'./modelWeights/DNN{idx}.h5')  
            show_train_history_NN(history, loss, 'r_square', 'val_r_square', idx)
            yTrainPredicted = model.predict(x_train)
            r2_train = r2_score(y_train, yTrainPredicted)
            mape_train = mean_absolute_percentage_error(y_train, yTrainPredicted) * 100
            train_metric_lst[idx] = (np.array([mape_train, r2_train]))
            yValPredicted = model.predict(x_val)
            r2_val = r2_score(y_val, yValPredicted)
            mape_val = mean_absolute_percentage_error(y_val, yValPredicted) * 100
            val_metric_lst[idx] = np.array([mape_val, r2_val])
            # fitness_lst.append(1 - r2_val)
            fitness_lst.append(mape_val)
            model.load_weights('./modelWeights/DNN_initial.h5')
        self.plot_metrics_folds(train_metric_lst, val_metric_lst)
        highest_valR2_idx = np.where(val_metric_lst[:, 1] == np.max(val_metric_lst[:, 1]))[0][0]
        model.load_weights(f'./modelWeights/DNN{highest_valR2_idx}.h5')
        return model
    
    
    def model_testing(self, model_, category):
        model = model_
        model.fit(self.xTrain, self.yTrain)
        yTestPredicted = model.predict(self.xTest)
        draw_histo(self.yTest, 'Test', 'royalblue', range_std=2)
        self.plotTrueAndPredicted(self.xTest, self.yTest, yTestPredicted, f"({category}) [Test]")
        
    def plotTrueAndPredicted(self, x, YT, YP, category):
        plot = True
        if self.normalized == 'xy':
            YT = (self.yMax - self.yMin) * YT + self.yMin
            YP = (self.yMax - self.yMin) * YP + self.yMin
        rmse = np.sqrt(mean_squared_error(YT, YP))
        r2 = r2_score(YT, YP)
        mape = mean_absolute_percentage_error(YT, YP) * 100
        mae = mean_absolute_error(YT, YP)
        color1 = ['slateblue', 'orange', 'firebrick', 'steelblue', 'purple', 'green']
        if plot:
            plt.figure(figsize=(12, 9))
            plt.plot(YT, YP, 'o', color='forestgreen', lw=5)
            plt.axline((0, 0), slope=1, color='black', linestyle = '--', transform=plt.gca().transAxes)
            topValue = (max(YT) if max(YT) > max(YP) else max(YP))
            topValue = topValue * 1.1 if topValue > 0 else topValue * 0.9
            bottomValue = (min(YT) if min(YT) < min(YP) else min(YP))
            bottomValue = bottomValue * 0.9 if topValue > 0 else topValue * 1.1
            bottomValue = 0
            topValue = 2.7
            plt.ylabel("Predicted Value", fontsize=24)
            plt.xlabel("True Value", fontsize=24)
            plt.ylim([bottomValue, topValue])
            plt.xlim([bottomValue, topValue])
            plt.xticks(np.linspace(bottomValue, topValue, 5), fontsize=22)
            plt.yticks(np.linspace(bottomValue, topValue, 5), fontsize=22)
            plt.title(f"{self.qualityKind} {category} \n MAPE={mape:.2f} | R^2={r2:.2f} | MAE={mae:.2f}"
                      , fontsize=26)
            plt.axhline(y=1, color=color1[0])
            plt.axhline(y=1.2, color=color1[1])
            plt.axhline(y=1.5, color=color1[2])
            plt.axhline(y=2, color=color1[3])
            plt.axvline(x=1, color=color1[0])
            plt.axvline(x=1.2, color=color1[1])
            plt.axvline(x=1.5, color=color1[2])
            plt.axvline(x=2, color=color1[3])
            plt.grid()
            plt.show()
        print(f"{self.qualityKind} {category} {mape:.2f} {r2:.2f} {mae:.2f}")

class cross_validate_signal:
    def __init__(self, x, y, qualityKind, normalized):
        self.qualityKind = qualityKind
        self.normalized = normalized
        self.x, self.y = cleanOutlier(x, y)
        
        if self.normalized == 'xy':
            self.x, self.xMin, self.xMax = normalization_signal(self.x)
            self.y, self.yMin, self.yMax = normalizationY(self.y)
            self.xTrain, self.yTrain, self.xTest, self.yTest = datasetCreating(self.x, self.y)
    
        elif self.normalized == 'x':
            self.x, self.xMin, self.xMax = normalization_signal(self.x)
            self.xTrain, self.yTrain, self.xTest, self.yTest = datasetCreating(self.x, self.y)
    
        else:
            self.xTrain, self.yTrain, self.xTest, self.yTest = datasetCreating(self.x, self.y)
    
        
        self.kfold_num = 5      

    def build_1DCNN(self, loss):
        optimizer = opti.Adam(learning_rate=0.0035)
        model = Sequential()
        model.add(Convolution1D(filters=32, kernel_size = 29,
                                strides = 9,
                                data_format='channels_last', padding = 'same',
                                input_shape=(self.xTrain.shape[1], 1),
                                activation = 'relu'))
        # model.add(BatchNormalization())
        model.add(Flatten())
        model.add(Dense(round(self.xTrain.shape[1]/4), activation='relu'))
        model.add(Dense(round(self.xTrain.shape[1]/8), activation='relu'))
        model.add(Dense(round(self.xTrain.shape[1]/8), activation='relu'))
        model.add(Dense(1, activation='linear'))
        model.compile(loss=loss,
                      optimizer=optimizer,
                      metrics=[r_square.RSquare()])
        return model   
    
 

    def cross_validate_1DCNN(self):
        xTrain, yTrain = shuffle(self.xTrain, self.yTrain, random_state=75)
        kf = KFold(n_splits=self.kfold_num)
        fitness_lst = []
        train_metric_lst = np.zeros((self.kfold_num, 2))
        val_metric_lst = np.zeros((self.kfold_num, 2))
        metric = "mean_absolute_error"
        loss = "mean_absolute_percentage_error"
        model = self.build_1DCNN(loss, metric)
        model.save_weights('./modelWeights/1DCNN_initial.h5') 
        for idx, (train_idx, val_idx) in enumerate(kf.split(xTrain)):
            
            #  model.summary()
            callback = EarlyStopping(monitor="loss", patience=30, verbose=1, mode="auto")
            x_train = xTrain[train_idx]
            y_train = yTrain[train_idx]
            x_val = xTrain[val_idx]
            y_val = yTrain[val_idx]
            history = model.fit(x_train, y_train, validation_data = (x_val, y_val),
                                epochs=1000, batch_size=5, verbose=1, callbacks=[callback])
            model.save_weights(f'./modelWeights/1DCNN{idx}.h5')  
            yTrainPredicted = model.predict(x_train, verbose=0)
            r2_train = r2_score(y_train, yTrainPredicted)
            mape_train = mean_absolute_percentage_error(y_train, yTrainPredicted) * 100
            train_metric_lst[idx] = (np.array([mape_train, r2_train]))
            yValPredicted = model.predict(x_val)
            r2_val = r2_score(y_val, yValPredicted)
            mape_val = mean_absolute_percentage_error(y_val, yValPredicted) * 100
            val_metric_lst[idx] = np.array([mape_val, r2_val])
            # fitness_lst.append(1 - r2_val)
            fitness_lst.append(mape_val)
            show_train_history_NN(history, loss, metric, 'val_'+metric, idx)
            model.load_weights('./modelWeights/1DCNN_initial.h5')

            
        self.plot_metrics_folds(train_metric_lst, val_metric_lst)
        highest_valR2_idx = np.where(val_metric_lst[:, 1] == np.max(val_metric_lst[:, 1]))[0][0]
        model.load_weights(f'./modelWeights/1DCNN{highest_valR2_idx}.h5')
        return model
    
    def build_LSTM(self, loss, metrics):
        optimizer = opti.Adam(learning_rate=0.005)
        # input of LSTM should be [n_samples, n_length, n_channels] 
        model = Sequential()
        model.add(LSTM(units=1, return_sequences=False,
                       input_length=self.xTrain.shape[1],
                       input_dim=self.xTrain.shape[2], activation='linear'))
        # model.add(Dense(1, activation='relu'))
        model.summary()
        model.compile(loss=loss,
              optimizer=optimizer,
              metrics=[metrics])
        return model 
    
    def cross_validate_LSTM(self):
        xTrain, yTrain = shuffle(self.xTrain, self.yTrain, random_state=75)
        kf = KFold(n_splits=self.kfold_num)
        fitness_lst = []
        train_metric_lst = np.zeros((self.kfold_num, 2))
        val_metric_lst = np.zeros((self.kfold_num, 2))
        # loss = "mean_squared_error"
        # loss = "mean_absolute_error"
        loss = "mean_absolute_percentage_error"
        # metric = "mean_absolute_percentage_error"
        metric = "mean_absolute_error"
        
        model = self.build_LSTM(loss, metric)
        model.save_weights('./modelWeights/LSTM_initial.h5') 
        for idx, (train_idx, val_idx) in enumerate(kf.split(xTrain)):
            
            #  model.summary()
            callback = EarlyStopping(monitor="loss", patience=10, verbose=1, mode="auto")
            x_train = xTrain[train_idx]
            y_train = yTrain[train_idx]
            x_val = xTrain[val_idx]
            y_val = yTrain[val_idx]
            history = model.fit(x_train, y_train, validation_data = (x_val, y_val),
                                epochs=1000, batch_size=10, verbose=1, callbacks=[callback])
            model.save_weights(f'./modelWeights/LSTM{idx}.h5')  
            yTrainPredicted = model.predict(x_train, verbose=0)
            r2_train = r2_score(y_train, yTrainPredicted)
            mape_train = mean_absolute_percentage_error(y_train, yTrainPredicted) * 100
            train_metric_lst[idx] = (np.array([mape_train, r2_train]))
            yValPredicted = model.predict(x_val)
            self.plotTrueAndPredicted(x_train, y_train, yTrainPredicted, "(LSTM) [Train]")
            self.plotTrueAndPredicted(x_val, y_val, yValPredicted, "(LSTM) [Validate]")
            r2_val = r2_score(y_val, yValPredicted)
            mape_val = mean_absolute_percentage_error(y_val, yValPredicted) * 100
            val_metric_lst[idx] = np.array([mape_val, r2_val])
            # fitness_lst.append(1 - r2_val)
            fitness_lst.append(mape_val)
            show_train_history_NN(history, loss, metric, 'val_'+metric, idx)
            model.load_weights('./modelWeights/LSTM_initial.h5')

            
        self.plot_metrics_folds(train_metric_lst, val_metric_lst)
        highest_valR2_idx = np.where(val_metric_lst[:, 1] == np.max(val_metric_lst[:, 1]))[0][0]
        model.load_weights(f'./modelWeights/LSTM{highest_valR2_idx}.h5')
        return model
    
    def model_testing(self, model_, category):
        model = model_
        model.fit(self.xTrain, self.yTrain)
        yTestPredicted = model.predict(self.xTest)
        self.plotTrueAndPredicted(self.xTest, self.yTest, yTestPredicted, f"({category}) [Test]")
    
    def plot_metrics_folds(self, train_lst, val_lst):
        x = np.arange(1, self.kfold_num+1, 1)
        train_lst, val_lst = train_lst.T, val_lst.T
        metrics = ['MAPE (%)', 'R2'] 
        plt.figure(figsize=(16, 6))
        ax1 = plt.subplot(121)
        ax1.plot(x, train_lst[0], '-o', label='train', lw=5, color='seagreen')
        ax1.plot(x, val_lst[0], '-o', label='val', lw=5, color='brown')
        ax1.set_ylabel(f'{metrics[0]}', fontsize=24)
        ax1.set_xlabel('Fold', fontsize=24)
        ax1.tick_params(axis='both', which='major', labelsize=20)
        ax1.legend(loc='best', fontsize=20)
        # ax1.set_title(f'{metrics[0]}', fontsize=26)
        ax1.grid(True)
        ax1.set_ylim((0, 40))
        
        ax2 = plt.subplot(122)
        ax2.plot(x, train_lst[1], '-o', label='train', lw=5, color='seagreen')
        ax2.plot(x, val_lst[1], '-o', label='val', lw=5, color='brown')
        ax2.set_ylabel(f'{metrics[1]}', fontsize=24)
        ax2.set_xlabel('Fold', fontsize=24)
        ax2.tick_params(axis='both', which='major', labelsize=20)
        ax2.legend(loc='best', fontsize=20)
        # ax2.set_title(f'{metrics[1]}', fontsize=26)
        ax2.grid(True)
        ax2.set_ylim((0, 1.1))
        # ax2.set_ylim((0, 1.1))
        plt.suptitle(f'Cross Validation', fontsize=26)    
    
    def plotTrueAndPredicted(self, x, YT, YP, category):
        bottomValue = 0
        topValue = 2.7
        plot = True
        if self.normalized == 'xy':
            YT = (self.yMax - self.yMin) * YT + self.yMin
            YP = (self.yMax - self.yMin) * YP + self.yMin
        rmse = np.sqrt(mean_squared_error(YT, YP))
        r2 = r2_score(YT, YP)
        mape = mean_absolute_percentage_error(YT, YP) * 100
        mae = mean_absolute_error(YT, YP)
        if plot:
            plt.figure(figsize=(12, 9))
            plt.plot(YT, YP, 'o', color='forestgreen', lw=5)
            plt.axline((0, 0), slope=1, color='black', linestyle = '--', transform=plt.gca().transAxes)
            # topValue = (max(YT) if max(YT) > max(YP) else max(YP))
            # topValue = topValue * 1.1 if topValue > 0 else topValue * 0.9
            # bottomValue = (min(YT) if min(YT) < min(YP) else min(YP))
            # bottomValue = bottomValue * 0.9 if topValue > 0 else topValue * 1.1
            plt.ylabel("Predicted Value", fontsize=24)
            plt.xlabel("True Value", fontsize=24)
            plt.ylim([bottomValue, topValue])
            plt.xlim([bottomValue, topValue])
            plt.xticks(np.linspace(bottomValue, topValue, 5), fontsize=22)
            plt.yticks(np.linspace(bottomValue, topValue, 5), fontsize=22)
            plt.title(f"{self.qualityKind} {category} \n MAPE={mape:.2f} | R^2={r2:.2f} | MAE={mae:.2f}"
                      , fontsize=26)
            plt.grid()
            plt.show()
        print(f"{self.qualityKind} {category} {mape:.2f} {r2:.2f} {mae:.2f}")
        
class cross_validate_image:
    def __init__(self, x, y, qualityKind, normalized):
        self.qualityKind = qualityKind
        self.normalized = normalized
        self.x, self.y = cleanOutlier(x, y)
        
        if self.normalized == 'xy':
            self.x, self.xMin, self.xMax = normalization_signal(self.x)
            self.y, self.yMin, self.yMax = normalizationY(self.y)
            self.xTrain, self.yTrain, self.xTest, self.yTest = datasetCreating(self.x, self.y)
    
        elif self.normalized == 'x':
            self.x, self.xMin, self.xMax = normalization_signal(self.x)
            self.xTrain, self.yTrain, self.xTest, self.yTest = datasetCreating(self.x, self.y)
    
        else:
            self.xTrain, self.yTrain, self.xTest, self.yTest = datasetCreating(self.x, self.y)
    
        
        self.kfold_num = 5      
    
    def build_2DCNN(self, loss):
        optimizer = opti.Adam(learning_rate=0.0035)
        model = Sequential()
        model.add(Conv2D(filters=16, kernel_size=(5, 5), strides=(3, 3)
                 ,padding='valid', input_shape=(self.xTrain.shape[1], self.xTrain.shape[2], self.xTrain.shape[3])
                 ,activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(filters=8, kernel_size=(3, 3), strides=(1, 1)
                 ,padding='valid'
                 ,activation='relu'))
        model.add(BatchNormalization())
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Flatten())
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(1, activation='linear'))
        
        model.compile(loss=loss,
                      optimizer=optimizer,
                      metrics=[r_square.RSquare()])
        return model
    
    def cross_validate_2DCNN(self):
        xTrain, yTrain = shuffle(self.xTrain, self.yTrain, random_state=75)
        # xTrain = tf.cast(xTrain, tf.int64)
        # yTrain = tf.cast(yTrain, tf.int64)
        kf = KFold(n_splits=self.kfold_num)
        fitness_lst = []
        train_metric_lst = np.zeros((self.kfold_num, 2))
        val_metric_lst = np.zeros((self.kfold_num, 2))
        loss = "mean_absolute_error"
        model = self.build_2DCNN(loss)
        model.save_weights('./modelWeights/2DCNN_initial.h5') 
        for idx, (train_idx, val_idx) in enumerate(kf.split(xTrain)):
        
            callback = EarlyStopping(monitor="loss", patience=30, verbose=0, mode="auto")
            x_train = xTrain[train_idx]
            y_train = yTrain[train_idx]
            x_val = xTrain[val_idx]
            y_val = yTrain[val_idx]
            history = model.fit(x_train, y_train, validation_data = (x_val, y_val),
                                epochs=1000, batch_size=5, verbose=1, callbacks=[callback])
            model.save_weights(f'./modelWeights/2DCNN{idx}.h5')           
            yTrainPredicted = model.predict(x_train, verbose=0)
            r2_train = r2_score(y_train, yTrainPredicted)
            mape_train = mean_absolute_percentage_error(y_train, yTrainPredicted) * 100
            train_metric_lst[idx] = (np.array([mape_train, r2_train]))
            yValPredicted = model.predict(x_val)
            r2_val = r2_score(y_val, yValPredicted)
            mape_val = mean_absolute_percentage_error(y_val, yValPredicted) * 100
            val_metric_lst[idx] = np.array([mape_val, r2_val])
            # fitness_lst.append(1 - r2_val)
            fitness_lst.append(mape_val)
            show_train_history_NN(history, loss, 'r_square', 'val_r_square', idx)
            # keras.backend.clear_session()
            model.load_weights('./modelWeights/2DCNN_initial.h5')
            
        self.plot_metrics_folds(train_metric_lst, val_metric_lst)
        highest_valR2_idx = np.where(val_metric_lst[:, 1] == np.max(val_metric_lst[:, 1]))[0][0]
        model.load_weights(f'./modelWeights/2DCNN{highest_valR2_idx}.h5')
        return model
    
    
    def model_testing(self, model_, category):
        model = model_
        model.fit(self.xTrain, self.yTrain)
        yTestPredicted = model.predict(self.xTest)
        self.plotTrueAndPredicted(self.xTest, self.yTest, yTestPredicted, f"({category}) [Test]")
        keras.backend.clear_session()
    
    def plot_metrics_folds(self, train_lst, val_lst):
        x = np.arange(1, self.kfold_num+1, 1)
        train_lst, val_lst = train_lst.T, val_lst.T
        metrics = ['MAPE (%)', 'R2'] 
        plt.figure(figsize=(16, 6))
        ax1 = plt.subplot(121)
        ax1.plot(x, train_lst[0], '-o', label='train', lw=5, color='seagreen')
        ax1.plot(x, val_lst[0], '-o', label='val', lw=5, color='brown')
        ax1.set_ylabel(f'{metrics[0]}', fontsize=24)
        ax1.set_xlabel('Fold', fontsize=24)
        ax1.tick_params(axis='both', which='major', labelsize=20)
        ax1.legend(loc='best', fontsize=20)
        # ax1.set_title(f'{metrics[0]}', fontsize=26)
        ax1.grid(True)
        ax1.set_ylim((0, 40))
        
        ax2 = plt.subplot(122)
        ax2.plot(x, train_lst[1], '-o', label='train', lw=5, color='seagreen')
        ax2.plot(x, val_lst[1], '-o', label='val', lw=5, color='brown')
        ax2.set_ylabel(f'{metrics[1]}', fontsize=24)
        ax2.set_xlabel('Fold', fontsize=24)
        ax2.tick_params(axis='both', which='major', labelsize=20)
        ax2.legend(loc='best', fontsize=20)
        # ax2.set_title(f'{metrics[1]}', fontsize=26)
        ax2.grid(True)
        ax2.set_ylim((0, 1.1))
        # ax2.set_ylim((0, 1.1))
        plt.suptitle(f'Cross Validation', fontsize=26)    
    
    def plotTrueAndPredicted(self, x, YT, YP, category):
        bottomValue = 0
        topValue = 2.7
        plot = True
        if self.normalized == 'xy':
            YT = (self.yMax - self.yMin) * YT + self.yMin
            YP = (self.yMax - self.yMin) * YP + self.yMin
        rmse = np.sqrt(mean_squared_error(YT, YP))
        r2 = r2_score(YT, YP)
        mape = mean_absolute_percentage_error(YT, YP) * 100
        mae = mean_absolute_error(YT, YP)
        if plot:
            plt.figure(figsize=(12, 9))
            plt.plot(YT, YP, 'o', color='forestgreen', lw=5)
            plt.axline((0, 0), slope=1, color='black', linestyle = '--', transform=plt.gca().transAxes)
            # topValue = (max(YT) if max(YT) > max(YP) else max(YP))
            # topValue = topValue * 1.1 if topValue > 0 else topValue * 0.9
            # bottomValue = (min(YT) if min(YT) < min(YP) else min(YP))
            # bottomValue = bottomValue * 0.9 if topValue > 0 else topValue * 1.1
            plt.ylabel("Predicted Value", fontsize=24)
            plt.xlabel("True Value", fontsize=24)
            plt.ylim([bottomValue, topValue])
            plt.xlim([bottomValue, topValue])
            plt.xticks(np.linspace(bottomValue, topValue, 5), fontsize=22)
            plt.yticks(np.linspace(bottomValue, topValue, 5), fontsize=22)
            plt.title(f"{self.qualityKind} {category} \n MAPE={mape:.2f} | R^2={r2:.2f} | MAE={mae:.2f}"
                      , fontsize=26)
            plt.grid()
            plt.show()
        print(f"{self.qualityKind} {category} {mape:.2f} {r2:.2f} {mae:.2f}")
    