import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_percentage_error, r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
import random
import copy
from xgboost import XGBRegressor
from sklearn.model_selection import KFold
from sklearn.utils import shuffle
from plot_histogram import draw_histo

# edit the part below when model is changed
class psoXGB:
    def __init__(self, x, y, qualityKind, normalized=None, y_boundary=[]):
        self.qualityKind = qualityKind
        # self.isMultiStacking = True
        self.normalized = normalized
        self.dna_amount = 6+1  # hyper_parameter num. + random seed
        self.x = x
        self.y = y
        self.x, self.y = self.cleanOutlier(x, y)
        self.kfold_num = 5
        self.optimized_param = ['eta','gamma', 'max_depth', 'subsample', 'lambda', 'random_state', 'RSN']
        
        if len(y_boundary) == 0:
            self.y_boundary = [min(y)-1, max(y)+1]
        else:
            self.y_boundary = y_boundary
        
        if self.normalized == 'xy':
            self.x, self.xMin, self.xMax = self.normalizationX(self.x)
            self.y, self.yMin, self.yMax = self.normalizationY(self.y)
            self.xTrain, self.yTrain, self.xTest, self.yTest = self.datasetCreating(self.x, self.y)

        elif self.normalized == 'x':
            self.x, self.xMin, self.xMax = self.normalizationX(self.x)
            self.xTrain, self.yTrain, self.xTest, self.yTest = self.datasetCreating(self.x, self.y)

        else:
            self.xTrain, self.yTrain, self.xTest, self.yTest = self.datasetCreating(self.x, self.y)

    def class_labeling(self, y_thresholds):
        y_class = np.copy(self.y)
        for sample_idx, sample_value in enumerate(self.y):
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

    def cleanOutlier(self, x, y):
        # Gid rid of y values exceeding 2 std value
        y_std = np.std(y)
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
        
    def normalizationX(self, array_):
        # array should be 2-D array
        # array.shape[0]: amount of samples
        # array.shape[1]: amount of features
        array_feature = np.copy(array_).T # array_feature: [n_feature, n_sample]
        minValue = []
        maxValue = []
        new_array_ = []
        for featureIdx, feature in enumerate(array_feature):
            mini = np.amin(feature)
            maxi = np.amax(feature)
            minValue.append(mini)
            maxValue.append(maxi)
            new_array_.append((feature - mini) / (maxi - mini))
        new_array_ = np.array(new_array_).T # [n_feature, n_sample] => [n_sample, n_feature]
        return new_array_, np.array(minValue), np.array(maxValue)
    
    def normalizationY(self, array_):
        # array should be 1-D array
        # array.shape: amount of samples
        array = np.copy(array_)
        minValue = []
        maxValue = []
        mini = min(array)
        maxi = max(array)
        minValue.append(mini)
        maxValue.append(maxi)
        array = (array - mini) / (maxi - mini)
        
        return array, np.array(minValue), np.array(maxValue)
    
    def datasetCreating(self, x_, y_):
        xTrain, xTest, yTrain, yTest = train_test_split(x_, y_, test_size=0.1, random_state=75)
        return xTrain, yTrain, xTest, yTest
                
    def plotTrueAndPredicted(self, x, YT, YP, category):
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
            plt.ylabel("Predicted Value", fontsize=24)
            plt.xlabel("True Value", fontsize=24)
            bottomValue = self.y_boundary[0]
            topValue = self.y_boundary[1]
            plt.ylim([bottomValue, topValue])
            plt.xlim([bottomValue, topValue])
            plt.xticks(np.linspace(bottomValue, topValue, 5), fontsize=22)
            plt.yticks(np.linspace(bottomValue, topValue, 5), fontsize=22)
            plt.title(f"{self.qualityKind} {category} \n MAPE={mape:.2f} | R^2={r2:.2f} | MAE={mae:.2f}"
                      , fontsize=26)
            plt.grid()
            plt.show()
        print(f"{self.qualityKind} {category} {mape:.2f} {r2:.2f} {mae:.2f}")
        
    def show_train_history(self, history_, category, fold_idx=0, isValidated=True):
        plt.figure(figsize=(16, 6))
        if isValidated:
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
            plt.suptitle(f'Fold {fold_idx+1} Train History', fontsize=26)

        
        else: # result of fine tune
            ax1 = plt.subplot(121)
            # category[0]=mape
            ax1.plot(history_['validation_0'][category[0]], lw=4, label='train')
            ax1.set_ylabel(f'{category[0]}', fontsize=24)
            ax1.set_xlabel('Epoch', fontsize=24)
            ax1.tick_params(axis='both', which='major', labelsize=20)
            ax1.legend(loc='best', fontsize=20)
            ax1.grid(True)
            # ax1.set_ylim(-0.03, 0.32)
    
            
            ax2 = plt.subplot(122)
            ax2.plot(history_['validation_0'][category[1]], lw=4, label='train')
            ax2.set_ylabel(f'{category[1]}', fontsize=24)
            ax2.set_xlabel('Epoch', fontsize=24)
            ax2.tick_params(axis='both', which='major', labelsize=20)
            ax2.legend(loc='best', fontsize=20)
            ax2.grid(True)
            plt.suptitle('Fining Tuning Train History', fontsize=26)
            
        plt.tight_layout()
        plt.subplots_adjust(top=0.88)
        plt.show()
        plt.close()
    
    def plot_metrics_folds(self, train_lst, val_lst, iter_idx=0, particle_idx=0):
        train_lst, val_lst = train_lst.T, val_lst.T
        x = np.arange(1, self.kfold_num+1, 1)
        plt.figure(figsize=(16, 6))
        ax1 = plt.subplot(121)
        ax1.plot(x, train_lst[0], '-o', label='train', lw=5, color='seagreen')
        ax1.plot(x, val_lst[0], '-o', label='val', lw=5, color='brown')
        ax1.set_ylabel('MAPE (%)', fontsize=24)
        ax1.set_xlabel('Fold', fontsize=24)
        ax1.tick_params(axis='both', which='major', labelsize=20)
        ax1.legend(loc='best', fontsize=20)
        ax1.grid(True)
        ax1.set_ylim((0, 40))
        
        ax2 = plt.subplot(122)
        ax2.plot(x, train_lst[1], '-o', label='train', lw=5, color='seagreen')
        ax2.plot(x, val_lst[1], '-o', label='val', lw=5, color='brown')
        ax2.set_ylabel('R2', fontsize=24)
        ax2.set_xlabel('Fold', fontsize=24)
        ax2.tick_params(axis='both', which='major', labelsize=20)
        ax2.grid(True)
        ax2.legend(loc='best', fontsize=20)
        ax2.set_ylim((0, 1.1))
        plt.suptitle(f'Iteration: {iter_idx} | Particle: {particle_idx}', fontsize=26)
        plt.tight_layout()
        plt.subplots_adjust(top=0.88)
        plt.show()
        plt.close()

    
    # edit the part below when model is changed
    def modelTraining(self, particle, iter_idx=0, particle_idx=0, show_result_each_fold=False):
        # [eta, gamma, max_depth, subsample, lambda_, random_state, RSN]
        # model building
        param_setting = {'eta':particle[0], 'gamma':int(particle[1]), 'max_depth':int(particle[2]),
                         'subsample':particle[3], 'lambda':int(particle[4]), 'random_state':int(particle[5])}
        xTrain, yTrain = shuffle(self.xTrain, self.yTrain, random_state=int(particle[6]))
        kf = KFold(n_splits=self.kfold_num)
        fitness_lst = []
        train_metric_lst = np.zeros((self.kfold_num, 2))
        val_metric_lst = np.zeros((self.kfold_num, 2))
        metrics = ['mape', 'rmse']
        model = XGBRegressor(eval_metric=metrics).set_params(**param_setting)
        for idx, (train_idx, val_idx) in enumerate(kf.split(xTrain)):
            x_train = xTrain[train_idx]
            y_train = yTrain[train_idx]
            x_val = xTrain[val_idx]
            y_val = yTrain[val_idx]
            evalset = [(x_train, y_train), (x_val, y_val)]
            model.fit(x_train, y_train, eval_set=evalset, verbose=False)
            yValPredicted = model.predict(x_val)
            r2_val = r2_score(y_val, yValPredicted)
            mape_val = mean_absolute_percentage_error(y_val, yValPredicted) * 100
            val_metric_lst[idx] = np.array([mape_val, r2_val])
            # fitness_lst.append(1 - r2_val)
            fitness_lst.append(mape_val)
            
            if show_result_each_fold:
                results = model.evals_result()
                self.show_train_history(results, metrics, iter_idx, particle_idx)
                r2_train = r2_score(y_train, model.predict(x_train))
                mape_train = mean_absolute_percentage_error(y_train, model.predict(x_train)) * 100
                train_metric_lst[idx] = (np.array([mape_train, r2_train]))
                print(f'\tTrain MAPE: {mape_train:.2f} Val. MAPE: {mape_val:.2f}')
                print(f'\tTrain R2:   {r2_train:.2f}   Val. R2:   {r2_val:.2f}\n')
                
        if show_result_each_fold:       
            self.plot_metrics_folds(train_metric_lst, val_metric_lst, iter_idx, particle_idx)
            
        fitness = np.array(fitness_lst).mean()

        return fitness
    
    """
    Handling position of particle population
    """
    def roundUpInt(self, x, prec=0, base=1):
        return int(round(base * round(x/base), prec))
    
    def roundUpFloat(self, x, prec=2, base=0.01):
        return round(base * round(x/base), prec)

    def particlePopulationInitialize(self, particleAmount):
        """
        eta: learning rate
        gamma: similarity penalty rate, higher gamma makes model more conservative
        max_depth: max depth of gradient tree
        subsample: how many training points chosen to fit model
        lambda: regularization param., higher lambda makes model more conservative
        random state: coefficient to initialize model
        RSN: random seed number to shuffle dataset
        
        optimized_param = ['eta','gamma', 'max_depth', 'subsample', 'lambda', 'random_state', 'RSN']
        """
        # edit the part below when model is changed
        initialPosition = np.zeros((particleAmount, self.dna_amount)) 
        eta_min = 0.0
        eta_max = 1.0
        gamma_min = 0
        gamma_max = 20
        depth_min = 4
        depth_max = 30
        sample_min = 0.6
        sample_max = 1.0
        lambda_min = 0
        lambda_max = 5
        random_state_min = 0
        random_state_max = 5
        RSN_min = 0
        RSN_max = 10
        param_min_lst = [eta_min, gamma_min, depth_min, sample_min, lambda_min, random_state_min, RSN_min]
        param_max_lst = [eta_max, gamma_max, depth_max, sample_max, lambda_max, random_state_max, RSN_max]
        for particleIdx in range(particleAmount):
            for dnaIdx in range(self.dna_amount):
                if self.optimized_param[dnaIdx] in ['gamma', 'max_depth', 'lambda', 'random_state', 'RSN']:
                    initialPosition[particleIdx, dnaIdx] = self.roundUpInt(param_min_lst[dnaIdx] + random.uniform(0, 1)*(param_max_lst[dnaIdx] - param_min_lst[dnaIdx]))
                else:
                    initialPosition[particleIdx, dnaIdx] = self.roundUpFloat(param_min_lst[dnaIdx] + random.uniform(0, 1)*(param_max_lst[dnaIdx] - param_min_lst[dnaIdx]))

        return initialPosition
    
    # edit the part below when model is changed
    def particleBoundary(self, particlePopulation):
        eta_min = 0.0
        eta_max = 1.0
        gamma_min = 0
        gamma_max = 20
        depth_min = 4
        depth_max = 30
        sample_min = 0.6
        sample_max = 1.0
        lambda_min = 0
        lambda_max = 5
        random_state_min = 0
        random_state_max = 5
        RSN_min = 0
        RSN_max = 10
        param_min_lst = [eta_min, gamma_min, depth_min, sample_min, lambda_min, random_state_min, RSN_min]
        param_max_lst = [eta_max, gamma_max, depth_max, sample_max, lambda_max, random_state_max, RSN_max]
        # test = particlePopulation
        for particleIdx, particle in enumerate(particlePopulation):
            for dnaIdx, dnaData in enumerate(particle):
                if particlePopulation[particleIdx, dnaIdx] < param_min_lst[dnaIdx]:
                    if self.optimized_param[dnaIdx] in ['gamma', 'max_depth', 'lambda', 'random_state', 'RSN']:
                        particlePopulation[particleIdx, dnaIdx] = self.roundUpInt(param_min_lst[dnaIdx] + random.uniform(0, 1)*(param_max_lst[dnaIdx] - param_min_lst[dnaIdx]))
                    else:
                        particlePopulation[particleIdx, dnaIdx] = self.roundUpFloat(param_min_lst[dnaIdx] + random.uniform(0, 1)*(param_max_lst[dnaIdx] - param_min_lst[dnaIdx]))
                elif particlePopulation[particleIdx, dnaIdx] > param_max_lst[dnaIdx]:
                    if self.optimized_param[dnaIdx] in ['gamma', 'max_depth', 'lambda', 'random_state', 'RSN']:
                        particlePopulation[particleIdx, dnaIdx] = self.roundUpInt(param_min_lst[dnaIdx] + random.uniform(0, 1)*(param_max_lst[dnaIdx] - param_min_lst[dnaIdx]))
                    else:
                        particlePopulation[particleIdx, dnaIdx] = self.roundUpFloat(param_min_lst[dnaIdx] + random.uniform(0, 1)*(param_max_lst[dnaIdx] - param_min_lst[dnaIdx]))

        
        return particlePopulation
    
    """
    find best fitness
    """
    def findIdxOfBestParticle(self, bestPopulationFitness):
        bestParticleIdx = 0
        while bestParticleIdx < len(bestPopulationFitness):
            if bestPopulationFitness[bestParticleIdx] == min(bestPopulationFitness):
                break
                bestParticleIdx = bestParticleIdx
            else:
                bestParticleIdx += 1
        return bestParticleIdx
    
    def model_testing(self, model_, category):
        yTestPredicted = model_.predict(self.xTest)
        self.plotTrueAndPredicted(self.xTest, self.yTest, yTestPredicted, f"({category}) [Test]")
        
    def bestModel(self, Gbest):    # See the performance of the best model
        # [eta, gamma, max_depth, subsample, lambda_, random_state, RSN]
        # edit the part below when model is changed
        param_setting = {'eta':Gbest[0], 'gamma':int(Gbest[1]), 'max_depth':int(Gbest[2]),
                         'subsample':Gbest[3], 'lambda':int(Gbest[4]), 'random_state':int(Gbest[5])}
        xTrain, yTrain = shuffle(self.xTrain, self.yTrain, random_state=int(Gbest[6]))
        kf = KFold(n_splits=self.kfold_num)
        train_metric_lst = np.zeros((self.kfold_num, 2))
        val_metric_lst = np.zeros((self.kfold_num, 2))
        metrics = ['mape', 'rmse']
        model = XGBRegressor(eval_metric=metrics).set_params(**param_setting)
        for idx, (train_idx, val_idx) in enumerate(kf.split(xTrain)):
            x_train = xTrain[train_idx]
            y_train = yTrain[train_idx]
            x_val = xTrain[val_idx]
            y_val = yTrain[val_idx]
            evalset = [(x_train, y_train), (x_val, y_val)]
            model.fit(x_train, y_train, eval_set=evalset, verbose=False)
            model.save_model(f".//modelWeights//xgb_{idx}.json")
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
            # draw_histo(y_val, f'Histogram of Output in Fold {idx+1}', 'seagreen', 0)
                    
        self.plot_metrics_folds(train_metric_lst, val_metric_lst, 'last', 'best')
        highest_valR2_idx = np.where(val_metric_lst[:, 1] == np.max(val_metric_lst[:, 1]))[0][0]
        best_model = XGBRegressor()
        best_model.load_model(f".//modelWeights//xgb_{highest_valR2_idx}.json")
        new_model = XGBRegressor(eval_metric=metrics, importance_type='total_gain',
                                 disable_default_eval_metric=True, n_estimators=100, random_state=75).set_params(**param_setting)
        new_model.fit(self.xTrain, self.yTrain, xgb_model=best_model, eval_set=[(self.xTrain, self.yTrain)], verbose=False)
        results_tune = new_model.evals_result()
        self.show_train_history(results_tune, metrics, isValidated=False)
        self.model_testing(best_model, 'XGB_PSO')
        return best_model
    
    """
    pso
    use this function only when performing pso
    """
    def pso(self, particleAmount, maxIterTime):
        DNA_amount = self.dna_amount
        fitnessHistory0 = []
        fitnessHistory1 = []
        
        # set up initial particle population
        particlePopulation = self.particlePopulationInitialize(particleAmount)   # Initial population
        newPopulation = np.zeros((particleAmount, DNA_amount))          
        velocity = 0.1 * particlePopulation # Initial velocity
        newVelocity = np.zeros((particleAmount, DNA_amount))
        
        c1 = 2
        c2 = 2
        IterTime = 0
        # iteration for best particle
        while IterTime < maxIterTime:
            # print(f'Iter. time: {IterTime}')
            newFitness = np.zeros(len(particlePopulation))
            for particleIdx in range(len(particlePopulation)):
                
                newFitness[particleIdx] = self.modelTraining(particlePopulation[particleIdx],
                                                             IterTime, particleIdx,
                                                             show_result_each_fold=False)
            # first iteration
            if IterTime == 0:
                particlePopulation = particlePopulation
                velocity = velocity
                bestPopulation = copy.deepcopy(particlePopulation)
                bestPopulationFitness = copy.deepcopy(newFitness)
                bestParticleIdx = self.findIdxOfBestParticle(bestPopulationFitness)
                bestParticle = bestPopulation[bestParticleIdx,:]
            
            # rest iteration
            else:
                for particleIdx in range(particleAmount):   # memory saving
                    if newFitness[particleIdx] < bestPopulationFitness[particleIdx]:
                        bestPopulation[particleIdx,:] = copy.deepcopy(particlePopulation[particleIdx,:])
                        bestPopulationFitness[particleIdx] = copy.deepcopy(newFitness[particleIdx])
                    else:
                        bestPopulation[particleIdx,:] = copy.deepcopy(bestPopulation[particleIdx,:])
                        bestPopulationFitness[particleIdx] = copy.deepcopy(bestPopulationFitness[particleIdx])
            
            bestParticleIdx = self.findIdxOfBestParticle(bestPopulationFitness)   
            bestParticle = bestPopulation[bestParticleIdx,:]
            
            fitnessHistory0.append(min(bestPopulationFitness))
            fitnessHistory1.append(np.mean(bestPopulationFitness))
            # print(f'Iteration {IterTime + 1}:')
            # print(f'minimum fitness: {min(bestPopulationFitness)}')
            # print(f'average fitness: {np.mean(bestPopulationFitness)}\n')
    
            if abs(np.mean(bestPopulationFitness)-min(bestPopulationFitness)) < 0.01: #convergent criterion
                break
    
            r1 = np.zeros((particleAmount, DNA_amount))
            r2 = np.zeros((particleAmount, DNA_amount))
            for particleIdx in range(particleAmount):
                for dnaIdx in range(DNA_amount):
                    r1[particleIdx, dnaIdx] = random.uniform(0, 1)
                    r2[particleIdx, dnaIdx] = random.uniform(0, 1)
                    
            bestParticle = bestParticle.reshape(1, -1)
            
            # making new population
            for particleIdx in range(particleAmount):
                for dnaIdx in range(DNA_amount):
                    w_max = 0.9
                    w_min = 0.4
                    w = (w_max - w_min)*(maxIterTime - IterTime) / maxIterTime + w_min
                    newVelocity[particleIdx, dnaIdx] = w * velocity[particleIdx, dnaIdx] + c1 * r1[particleIdx, dnaIdx] * (bestPopulation[particleIdx, dnaIdx] - particlePopulation[particleIdx, dnaIdx]) + c2*r2[particleIdx, dnaIdx] * (bestParticle[0, dnaIdx] - particlePopulation[particleIdx, dnaIdx])
                    newPopulation[particleIdx, dnaIdx] = particlePopulation[particleIdx, dnaIdx] + newVelocity[particleIdx, dnaIdx]
            
            particlePopulation = copy.deepcopy(newPopulation)
            velocity = copy.deepcopy(newVelocity)
            
            particlePopulation = self.particleBoundary(particlePopulation)

            for particleIdx in range(particleAmount):
                for dnaIdx in range(DNA_amount):
                    particlePopulation[particleIdx, dnaIdx] = self.roundUpInt(particlePopulation[particleIdx, dnaIdx])


                
            IterTime += 1
            
        # final iteration
        newFitness = np.zeros(len(particlePopulation))
        for particleIdx in range(len(particlePopulation)):

            newFitness[particleIdx] = self.modelTraining(particlePopulation[particleIdx],
                                                                        IterTime, particleIdx,
                                                                        show_result_each_fold=False)
  
        for particleIdx in range(particleAmount):
            if newFitness[particleIdx] < bestPopulationFitness[particleIdx]:
                bestPopulation[particleIdx, :] = copy.deepcopy(particlePopulation[particleIdx, :])
                bestPopulationFitness[particleIdx] = copy.deepcopy(newFitness[particleIdx])
            else:
                bestPopulation[particleIdx,:] = copy.deepcopy(bestPopulation[particleIdx,:])
                bestPopulationFitness[particleIdx] = copy.deepcopy(bestPopulationFitness[particleIdx])
                
        bestParticleIdx = self.findIdxOfBestParticle(bestPopulationFitness)                
        bestParticle = bestPopulation[bestParticleIdx,:]
                
        fitnessHistory0.append(min(bestPopulationFitness))
        fitnessHistory1.append(np.mean(bestPopulationFitness))
        fitnessHistory0 = np.array(fitnessHistory0)
        fitnessHistory1 = np.array(fitnessHistory1)
        fitnestHistory = np.hstack((fitnessHistory0, fitnessHistory1))
        ll = float(len(fitnestHistory))/2
        fitnestHistory = fitnestHistory.reshape(int(ll), 2, order='F')
        optimal_model = self.bestModel(bestParticle)
        
        return optimal_model, fitnestHistory
