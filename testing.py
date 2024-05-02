import numpy as np
import os, glob
from matplotlib import pyplot as plt
import featureExtraction as feaext
import signal_processing as sigpro
import qualityExtractionLoc as QEL
# from classImportance_single_output import importanceAnalysis

from locIntegration import locIntegrate
from classPSO_XGB import psoXGB
# import pandas as pd
from correlation_analysis import corr_features_vs_quality, corr_filter
from sklearn.metrics import mean_absolute_percentage_error, r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
from cross_validation import cross_validate, cross_validate_signal, cross_validate_image
from classPSO_kNN import psokNN
from classPSO_RF_importance_detection import psoRF


def quick_check_extremes(signal_lst, alarm_values):
    for signal in signal_lst:
        if signal.min() < alarm_values[0]:
            print(f'min: {signal.min()}')
        if signal.max() > alarm_values[1]:
            print(f'max: {signal.max()}')

if __name__ == '__main__':
    isDifferentParamSets = True
    paramSet_num = 2
    isLoc = True
    differencing = False
    differencing = True
    isEnveCombined = False
    isEnveCombined = True
    # resample_size = 10
    
    """
    Signal
    """
    signals = sigpro.get_signals('.\\datasetB', param_idx_lst=np.arange(0, 56, 1))
    og_num_run = len(signals)
    param_set = sigpro.get_parameter_set(signals)
    methodIdx_lst = [np.where(param_set == 1)[0], np.where(param_set == 2)[0]]
    signals = sigpro.pick_run_data(signals, methodIdx_lst[paramSet_num-1])
    # signals = time_series_resample(signals, dt_original=10, dt_final=60)
    progress = sigpro.pick_one_signal(signals, signal_idx=0)
    valid_run_idx = sigpro.non_discontinuous_runs(progress, 0, 306, 1)
    signals = sigpro.pick_run_data(signals, valid_run_idx)
    shortest_length = min([run.shape[1] for run in signals])
    signals_resize = sigpro.time_series_resize(signals, shortest_length)

    """
    Quality
    """
    ttv = QEL.pick_certain_qualities(".\\quality_2022_B.csv", ['TTV'], methodIdx_lst[paramSet_num-1], isDifferentParamSets)
    warp = QEL.pick_certain_qualities(".\\quality_2022_B.csv", ['Warp'], methodIdx_lst[paramSet_num-1], isDifferentParamSets)
    waviness = QEL.pick_certain_qualities(".\\quality_2022_B.csv", ['Wav ind'], methodIdx_lst[paramSet_num-1], isDifferentParamSets)
    bow = QEL.pick_certain_qualities(".\\quality_2022_B.csv", ['Bow'], methodIdx_lst[paramSet_num-1], isDifferentParamSets) 
    position = QEL.get_wafer_position(".\\quality_2022_B.csv", methodIdx_lst[paramSet_num-1], isDifferentParamSets)
    lot = QEL.get_lot(".\\quality_2022_B.csv", methodIdx_lst[paramSet_num-1], isDifferentParamSets)
    waviness_3 = QEL.pick_certain_qualities(".\\quality_2022_B.csv", ['Wav ind', 'Entry wav', 'Exit wav'], methodIdx_lst[paramSet_num-1], isDifferentParamSets)
    
    
    
    ttv = sigpro.pick_run_data(ttv, valid_run_idx)
    warp = sigpro.pick_run_data(warp, valid_run_idx)
    waviness = sigpro.pick_run_data(waviness, valid_run_idx)
    bow = sigpro.pick_run_data(bow, valid_run_idx)
    position = sigpro.pick_run_data(position, valid_run_idx)
    lot = sigpro.pick_run_data(lot, valid_run_idx)
    waviness_3 = sigpro.pick_run_data(waviness_3, valid_run_idx)
    
    general_run_idx = QEL.high_similarity_runs(waviness, lot)
    ttv = sigpro.pick_run_data(ttv, general_run_idx)
    warp = sigpro.pick_run_data(warp, general_run_idx)
    waviness = sigpro.pick_run_data(waviness, general_run_idx)
    bow = sigpro.pick_run_data(bow, general_run_idx)
    position = sigpro.pick_run_data(position, general_run_idx)
    lot = sigpro.pick_run_data(lot, general_run_idx)
    waviness_3 = sigpro.pick_run_data(waviness_3, general_run_idx)
    
    ingot_len = QEL.get_ingot_length(".\\quality_2022_B.csv", methodIdx_lst[paramSet_num-1], isDifferentParamSets)
    ingot_len = np.array(ingot_len).reshape(-1, 1)
    ingot_len = sigpro.pick_run_data(ingot_len, valid_run_idx)
    ingot_len = sigpro.pick_run_data(ingot_len, general_run_idx)
    
    """
    Feature extraction
    """
    signals = sigpro.pick_run_data(signals, general_run_idx)
    feature_file_completed = False
    file_location = '.\\signal_features_for_importance_analysis'
    features_total = []
    for run_idx, run_signals in enumerate(signals):
        if not feature_file_completed:
            features_run = feaext.TimeFeatures(run_signals, gau_sig=2, gau_rad=4, w_size=3).features_all_signals
            for signal_idx, signal_features in enumerate(features_run):
                for feature_idx, value in enumerate(signal_features):
                    if np.isnan(value):
                        features_run[signal_idx, feature_idx] = 0
            np.savetxt(f'{file_location}\\{run_idx}.csv', features_run, delimiter=",")
            features_run = np.hstack(features_run)
        else:
            features_run = np.hstack(np.genfromtxt(f'{file_location}\\{run_idx}.csv', delimiter=','))
        features_total.append(features_run)
    features_total = np.array(features_total)

