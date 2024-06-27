import numpy as np
import featureExtraction as feaext
import signal_processing as sigpro
import qualityExtractionLoc as QEL
from locIntegration import locIntegrate
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_percentage_error, r2_score, mean_squared_error, mean_absolute_error
# import pandas as pd
import cross_validation as cv
from classPSO_kNN import psokNN 
from matplotlib import pyplot as plt
import scipy 

def datasetCreating(x_, y_):
    xTrain, xTest, yTrain, yTest = train_test_split(x_, y_, test_size=0.1, random_state=75)

    return xTrain, yTrain, xTest, yTest

def plot_feature_distribution(x_lst, y_lst, lst_inspected_feature=0, feature_name_lst=['Mean', 'Kurtosis', 'Skewness', 'Variance', 'Max. P2P'], num_kind_fea=5, num_segment_per_sig=4, num_fea_per_sig=20):
    ds_name = [f'A{paramSet_num}', f'B{paramSet_num}', f'C{paramSet_num}']
    
    for feature_idx in lst_inspected_feature:
        plt.figure(figsize=(10, 10))
        is_wafer_fea = False
        if feature_idx >= 60: # wafer feature
            is_wafer_fea = True
        if is_wafer_fea:
            feature_name = 'Ingot Length' if feature_idx<61 else 'Wafer Location'
        else:
            if feature_idx < num_fea_per_sig:
                kind_sig = 'Signal'
            elif feature_idx < num_fea_per_sig*2:
                kind_sig = 'Upper Envelope'
            else:
                kind_sig = 'Lower Envelope'
            kind_feature = feature_name_lst[feature_idx%num_kind_fea]
            kind_seg = (feature_idx//5)%num_segment_per_sig + 1
            feature_name = kind_feature + ' of ' + kind_sig + ' from Segment ' + str(kind_seg)
        
        
        for idx_ds, distri_ds in enumerate(x_lst):
            plt.plot(distri_ds[:, feature_idx], y_lst[idx_ds], 'o', lw=2, label=ds_name[idx_ds])
        plt.legend(fontsize=20)
        plt.title(f'{feature_name} v.s. {quality_lst[quality_idx]}', fontsize=24)
        plt.xlabel(f'{feature_name}', fontsize=20)
        plt.ylabel(f'{quality_lst[quality_idx]}', fontsize=20)
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        plt.grid()

def plot_test_different_dataset(x_test_lst, y_test_lst, model, involved_class, label_lst = ['A', 'B', 'C']):
    plt.figure(figsize=(12, 12), dpi=300)
    color_lst = ['royalblue', 'peru', 'deeppink']
    for idx_ds, x_test_ in enumerate(x_test_lst):
        y_test_ = y_test_lst[idx_ds]
        if 'x' in involved_class.normalized or 'X' in involved_class.normalized:
            x_test_ = (x_test_ - involved_class.xMin) / (involved_class.xMax - involved_class.xMin)
            
        if 'y' in involved_class.normalized or 'Y' in involved_class.normalized:
            y_test_ = (y_test_ - involved_class.yMin) / (involved_class.yMax - involved_class.yMin)
        y_test_pred_ = model.predict(x_test_)
        if involved_class.yMin != None and involved_class.yMax != None:
            y_test_pred_ = y_test_pred_ * (involved_class.yMax-involved_class.yMin) + involved_class.yMin
            y_test_ = y_test_ * (involved_class.yMax-involved_class.yMin) + involved_class.yMin
        r2 = r2_score(y_test_, y_test_pred_)
        mape = mean_absolute_percentage_error(y_test_, y_test_pred_) * 100
        mae = mean_absolute_error(y_test_, y_test_pred_)    
        label_ = f'{label_lst[idx_ds]}: MAPE={mape:.2f}% | $R^2={r2:.2f}$ | MAE={mae:.2f}'
        plt.plot(y_test_, y_test_pred_, 'o', color=color_lst[idx_ds], label=label_, lw=5)
        
        
    plt.axline((0, 0), slope=1, color='black', linestyle = '--', transform=plt.gca().transAxes)
    plt.ylabel("Predicted Value", fontsize=24)
    plt.xlabel("True Value", fontsize=24)
    bottomValue = involved_class.y_boundary[0]
    topValue = involved_class.y_boundary[1]
    plt.ylim([bottomValue, topValue])
    plt.xlim([bottomValue, topValue])
    plt.xticks(np.linspace(bottomValue, topValue, 5), fontsize=22)
    plt.yticks(np.linspace(bottomValue, topValue, 5), fontsize=22)

    # tesxt_box_x = bottomValue
    # plt.text(bottomValue+abs(bottomValue-topValue)*0.04, topValue-abs(bottomValue-topValue)*0.2,f'MAPE={mape:.2f}%\n$R^2={r2:.2f}$\nMAE={mae:.2f}',
    #          fontsize=24,
    #          bbox={'boxstyle':'square', 'facecolor':'white', 'edgecolor':'black', 'pad':0.3, 'linewidth':1})
    
    # plt.text(bottomValue+abs(bottomValue-topValue)*0.14, topValue-abs(bottomValue-topValue)*0.05, 'KNN', fontsize=24,
    #          bbox={'boxstyle':'round', 'facecolor':'wheat', 'edgecolor':'black', 'pad':0.3, 'linewidth':1, 'alpha':0.5})
    
    plt.axhline(y=0, color='red')
    plt.axvline(x=0, color='red')
    plt.grid()
    plt.legend(fontsize=22)
    plt.show()
    
        

if __name__ == '__main__':
    # paramSet_num = 1 
    # quality_idx = 2
    quality_lst = ['TTV', 'Warp', 'Waviness', 'Bow']
    y_boundary = {0:[5.5, 17], 1:[3, 18], 2:[0, 2.7], 3:[-5, 4]}
    
    # fA = np.pad(fA, (0, 1), 'constant', constant_values=(0, 1))
    # fB = np.pad(fB, (0, 1), 'constant', constant_values=(0, 2))
    # fC = np.pad(fC, (0, 1), 'constant', constant_values=(0, 3))
    for quality_idx in [2]:
        for paramSet_num in [2]:
            fA = np.genfromtxt(f'.//X_and_Y//f_A{paramSet_num}.csv', delimiter=',')
            fB = np.genfromtxt(f'.//X_and_Y//f_B{paramSet_num}.csv', delimiter=',')
            fC = np.genfromtxt(f'.//X_and_Y//f_C{paramSet_num}.csv', delimiter=',')
            
            yA = np.genfromtxt(f'.//X_and_Y//y_A{paramSet_num}.csv', delimiter=',')[:, quality_idx]
            yB = np.genfromtxt(f'.//X_and_Y//y_B{paramSet_num}.csv', delimiter=',')[:, quality_idx]
            yC = np.genfromtxt(f'.//X_and_Y//y_C{paramSet_num}.csv', delimiter=',')[:, quality_idx]
            
            x_3 = [fA, fB, fC]
            y_3 = [yA, yB, yC]
            
            xA, yA = cv.cleanOutlier(fA, yA)
            xB, yB = cv.cleanOutlier(fB, yB)
            xC, yC = cv.cleanOutlier(fC, yC)
            
            x = np.concatenate((xA, xB, xC), axis=0)
            y = np.concatenate((yA, yB, yC), axis=0)
            
            
            xA_train, yA_train, xA_test, yA_test = cv.datasetCreating(xA, yA)
            xB_train, yB_train, xB_test, yB_test = cv.datasetCreating(xB, yB)
            xC_train, yC_train, xC_test, yC_test = cv.datasetCreating(xC, yC)
            
            x_train = np.concatenate((xA_train, xB_train, xC_train), axis=0)
            y_train = np.concatenate((yA_train, yB_train, yC_train), axis=0)
            x_test = np.concatenate((xA_test, xB_test, xC_test), axis=0)
            y_test = np.concatenate((yA_test, yB_test, yC_test), axis=0) 
            
            # plot_feature_distribution([xA, xB, xC], [yA, yB, yC], lst_inspected_feature=np.arange(0, 62, 1))
            
            """
            Features of same location in different quality level
            """
            x_sorted_by_location = x[np.argsort(x[:, -1])]
            y_sorted_by_location = y[np.argsort(x[:, -1])]
            location_unique = np.vstack(np.unique(x[:, -1], return_counts=True))
            
            """
            Feature similarity of train and test
            Quality z-score of train and test
            """
            
            # ds_inspected = [np.concatenate((xC_train, yC_train.reshape(-1, 1)), axis=1), 
            #                 np.concatenate((xC_test, yC_test.reshape(-1, 1)), axis=1)]
            ds_inspected = [xC_train, xC_test]
            sample_simi_angle_lst = np.zeros((ds_inspected[1].shape[0], ds_inspected[0].shape[0]))
            sample_simi_angle = np.zeros(ds_inspected[1].shape[0])
            for idx_test_sample, sample_test in enumerate(ds_inspected[1]):
                for idx_train_sample, sample_train in enumerate(ds_inspected[0]):
                    sample_simi = np.dot(sample_test, sample_train)/(np.linalg.norm(sample_test)*np.linalg.norm(sample_train))
                    sample_simi_angle_lst[idx_test_sample, idx_train_sample] = np.arccos(sample_simi)
                    sample_simi_angle[idx_test_sample] = np.mean(sample_simi_angle_lst[idx_test_sample])
            ds_inspected_2 = [yC_train, yC_test]
            y_inspected_total = np.concatenate(ds_inspected_2)
            y_inspected_zscore = scipy.stats.zscore(y_inspected_total)
            sample_zscore = y_inspected_zscore[-ds_inspected_2[1].shape[0]:]
            
            """
            KNN PSO
            """
            # psoModel = psokNN(x, y, f'{quality_lst[quality_idx]} (Recipe_{paramSet_num})',
            #                         is_auto_split=False, normalized='xy', y_boundary=y_boundary[quality_idx])
            # model_pso, fitnessHistory, best_particle = psoModel.pso(x_train=x_train, y_train=y_train,
            #                                                         particleAmount=20, maxIterTime=10)
            # psoModel.model_testing(model_pso, 'kNN+PSO_A', x_test=xA_test, y_test=yA_test)
            # psoModel.model_testing(model_pso, 'kNN+PSO_B', x_test=xB_test, y_test=yB_test)
            # psoModel.model_testing(model_pso, 'kNN+PSO_C', x_test=xC_test, y_test=yC_test)
            # psoModel.model_testing(model_pso, 'kNN+PSO_Total', x_test=x_test, y_test=y_test)
            # plot_test_different_dataset([xA_test, xB_test, xC_test], [yA_test, yB_test, yC_test], model_pso, psoModel)
            
            """
            XGB XV
            """
            cv_prepare = cv.cross_validate(x, y, f'{quality_lst[quality_idx]} (Recipe_{paramSet_num})',
                                        normalized='xy', y_value_boundary=y_boundary[quality_idx], is_auto_split=False)
            param_setting = {'random_state':75}
            # model_cv = cv_prepare.cross_validate_XGB(x_train=x_train, y_train=y_train, param_setting=param_setting)
            # cv_prepare.model_testing(model_cv, 'XGB_A', x_test=xA_test, y_test=yA_test)
            # cv_prepare.model_testing(model_cv, 'XGB_B', x_test=xB_test, y_test=yB_test)
            # cv_prepare.model_testing(model_cv, 'XGB_C', x_test=xC_test, y_test=yC_test)
            # cv_prepare.model_testing(model_cv, 'XGB_Total', x_test=x_test, y_test=y_test)
            # plot_test_different_dataset([xA_test, xB_test, xC_test], [yA_test, yB_test, yC_test], model_cv, cv_prepare)
    
            """
            Individual
            """
            dataset_index = 2
            
            cv_prepare = cv.cross_validate(x_3[dataset_index], y_3[dataset_index], f'{quality_lst[quality_idx]} (Recipe_{paramSet_num})',
                                        normalized='xy', y_value_boundary=y_boundary[quality_idx])
            # for k in np.arange(1, 51, 1):
            #     param_setting_K = {'n_neighbors':k}
            #     knn = cv_prepare.cross_validate_kNN(param_setting=param_setting_K)
            #     cv_prepare.model_testing(knn, f'KNN (k={k})')
                
            param_setting_X = {'random_state':75}
            xgb = cv_prepare.cross_validate_XGB(param_setting=param_setting_X)
            cv_prepare.model_testing(xgb, 'XGBoost')
    
