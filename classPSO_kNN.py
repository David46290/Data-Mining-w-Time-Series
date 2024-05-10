import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_percentage_error, r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
import random
import copy
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import KFold
from sklearn.utils import shuffle
from plot_histogram import draw_histo

# edit the part below when model is changed
class psokNN:
    def __init__(self, x, y, qualityKind, normalized=None, y_boundary=[]):
        self.qualityKind = qualityKind
        # self.isMultiStacking = True
        self.normalized = normalized
        self.dna_amount = 2  # hyper_parameter num. + random seed
        self.x = x
        self.y = y
        self.x, self.y = self.cleanOutlier(x, y)
        self.kfold_num = 5
        
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
        y_median = np.median(y)
        # quartile_1 = np.round(np.quantile(y, 0.25), 2)
        # quartile_3 = np.round(np.quantile(y, 0.75), 2)
        # # Interquartile range
        # iqr = np.round(quartile_3 - quartile_1, 2)
        range_ = 2
        up_boundary = np.mean(y) + range_ * y_std 
        # up_boundary = 1.5
        # up_boundary = 1.38
        low_boundary = np.mean(y) - range_ * y_std 
        
        remaining = np.where(y < up_boundary)[0]
        # remaining = np.where(y < 1.5)[0]
        y_new = y[remaining]
        x_new = x[remaining]
        remaining2 = np.where(y_new > low_boundary)[0]
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
        # array should be 1-D array: [n_samples,]
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
            color1 = ['slateblue', 'orange', 'firebrick', 'steelblue', 'purple', 'green']
            plt.figure(figsize=(12, 9))
            plt.plot(YT, YP, 'o', color='forestgreen', lw=5)
            plt.axline((0, 0), slope=1, color='black', linestyle = '--', transform=plt.gca().transAxes)
            topValue = (max(YT) if max(YT) > max(YP) else max(YP))
            topValue = topValue * 1.1 if topValue > 0 else topValue * 0.9
            bottomValue = (min(YT) if min(YT) < min(YP) else min(YP))
            bottomValue = bottomValue * 0.9 if topValue > 0 else topValue * 1.1
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
        
    def show_train_history(self, history_, category, fold_idx):
        plt.figure(figsize=(16, 6))
        ax1 = plt.subplot(121)
        # category[0] = mape
        ax1.plot(history_['validation_0'][category[0]], lw=4, label='train')
        ax1.plot(history_['validation_1'][category[0]], lw=4, label='val')
        ax1.set_ylabel(f'{category[0]}', fontsize=24)
        ax1.set_xlabel('Epoch', fontsize=24)
        ax1.tick_params(axis='both', which='major', labelsize=20)
        ax1.legend(loc='best', fontsize=20)
        ax1.grid(True)
        ax1.set_ylim(-0.03, 0.32)

        
        ax2 = plt.subplot(122)
        ax2.plot(history_['validation_0'][category[1]], lw=4, label='train')
        ax2.plot(history_['validation_1'][category[1]], lw=4, label='val')
        ax2.set_ylabel(f'{category[1]}', fontsize=24)
        ax2.set_xlabel('Epoch', fontsize=24)
        ax2.tick_params(axis='both', which='major', labelsize=20)
        ax2.legend(loc='best', fontsize=20)
        ax2.grid(True)
        ax2.set_ylim(-0.03, 0.52)

        plt.suptitle(f'fold {fold_idx+1} Train History', fontsize=26)
        plt.tight_layout()
        plt.subplots_adjust(top=0.88)
        plt.show()
        plt.close() 
    
    def plot_metrics_folds(self, train_lst, val_lst, iter_idx, particle_idx):
        train_lst, val_lst = train_lst.T, val_lst.T
        x = np.arange(1, self.kfold_num+1, 1)
        plt.figure(figsize=(16, 6))
        ax1 = plt.subplot(121)
        ax1.plot(x, train_lst[0], '-o', label='train', lw=5, color='seagreen')
        ax1.plot(x, val_lst[0], '-o', label='val', lw=5, color='brown')
        ax1.set_ylabel('MAPE (%)', fontsize=24)
        ax1.set_xlabel('Fold', fontsize=24)
        ax1.tick_params(axis='both', which='major', labelsize=20)
        # ax1.set_xticks(np.arange(1, self.kfold_num+1, 1), fontsize=22)
        # ax1.set_title(f'Iter. time: {iter_idx} of Particle {particle_idx}', fontsize=26)
        ax1.legend(loc='best', fontsize=20)
        ax1.grid(True)
        ax1.set_ylim((0, 40))
        
        ax2 = plt.subplot(122)
        ax2.plot(x, train_lst[1], '-o', label='train', lw=5, color='seagreen')
        ax2.plot(x, val_lst[1], '-o', label='val', lw=5, color='brown')
        ax2.set_ylabel('R2', fontsize=24)
        ax2.set_xlabel('Fold', fontsize=24)
        ax2.tick_params(axis='both', which='major', labelsize=20)
        # ax2.set_xticks(np.arange(1, self.kfold_num+1, 1), fontsize=22)
        # ax2.set_title(f'Iter. time: {iter_idx} of Particle {particle_idx}', fontsize=26)
        ax2.grid(True)
        ax2.legend(loc='best', fontsize=20)
        ax2.set_ylim((0, 1.1))
        # ax2.set_ylim((0, 1.1))
        plt.suptitle(f'Iteration: {iter_idx} | Particle: {particle_idx}', fontsize=26)
        plt.tight_layout()
        plt.subplots_adjust(top=0.88)
        plt.show()
        plt.close()

    
    # edit the part below when model is changed
    def modelTraining(self, k, RSN, metricHistory, iter_idx, particle_idx):
        # model building
        k = int(k)
        RSN = int(RSN)
        xTrain, yTrain = shuffle(self.xTrain, self.yTrain, random_state=RSN)
        kf = KFold(n_splits=self.kfold_num)
        fitness_lst = []
        train_metric_lst = np.zeros((self.kfold_num, 2))
        val_metric_lst = np.zeros((self.kfold_num, 2))
        for idx, (train_idx, val_idx) in enumerate(kf.split(xTrain)):
            model = KNeighborsRegressor(n_neighbors=k)
            x_train = xTrain[train_idx]
            y_train = yTrain[train_idx]
            x_val = xTrain[val_idx]
            y_val = yTrain[val_idx]
            model.fit(x_train, y_train)
            try:
                yValPredicted = model.predict(x_val)
            except: # if n_samples < k
                model = KNeighborsRegressor(n_neighbors=x_val.shape[0])
                model.fit(x_train, y_train)
                yValPredicted = model.predict(x_val)
                
            # results = model.evals_result()
            # if particle_idx == 0:
            #     self.show_train_history(results, 'mape', iter_idx, particle_idx)
            r2_train = r2_score(y_train, model.predict(x_train))
            mape_train = mean_absolute_percentage_error(y_train, model.predict(x_train)) * 100
            train_metric_lst[idx] = (np.array([mape_train, r2_train]))
    
            r2_val = r2_score(y_val, yValPredicted)
            mape_val = mean_absolute_percentage_error(y_val, yValPredicted) * 100
            val_metric_lst[idx] = np.array([mape_val, r2_val])
            # fitness_lst.append(1 - r2_val)
            fitness_lst.append(mape_val)
            # print(f'\tTrain MAPE: {mape_train:.2f} Val. MAPE: {mape_val:.2f}')
            # print(f'\tTrain R2:   {r2_train:.2f}   Val. R2:   {r2_val:.2f}\n')
        # self.plot_metrics_folds(train_metric_lst, val_metric_lst, iter_idx, particle_idx)
        fitness = np.array(fitness_lst).mean()
        
        if fitness < min(metricHistory):
            metricHistory.append(fitness)

        return fitness, metricHistory
    
    """
    Handling position of particle population
    """
    def roundUpInt(self, x, prec=0, base=1):
        return int(round(base * round(x/base), prec))
    
    def roundUpFloat(self, x, prec=2, base=0.01):
        return round(base * round(x/base), prec)
    
    # def roundUpRSN(self, x, prec=2, base=0.01):
    #     return round(base * round(float(x)/base), prec)   

    def population_currentInitialize(self, particleAmount):
        """
        # step size shrinkage (learning rate)
        eta = [round(x, 2) for x in np.linspace(0, 1, num = 11)]
        # Maximum number of levels in tree
        max_depth = [6, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        # sampling rate of the training data (prevent overfitting)
        subsample = [round(x, 2) for x in np.linspace(0.1, 1, num = 10)]
        """
        initialPosition = np.zeros((particleAmount, self.dna_amount)) 
        k_min = 1
        k_max = 50
        RSN_min = 0
        RSN_max = 100
        param_min_lst = [k_min, RSN_min]
        param_max_lst = [k_max, RSN_max]
        # DO_min = 0
        # DO_max = 0.5
        # edit the part below when model is changed
        for particleIdx in range(particleAmount):
            for dnaIdx in range(self.dna_amount):
                initialPosition[particleIdx, dnaIdx] = self.roundUpInt(param_min_lst[dnaIdx] + random.uniform(0, 1)*(param_max_lst[dnaIdx] - param_min_lst[dnaIdx]))

        return initialPosition
    
    def particleBoundary(self, population_current):
        # edit the part below when model is changed
        # particleAmount = len(population_current)
        k_min = 1
        k_max = 50
        RSN_min = 0
        RSN_max = 100
        param_min_lst = [k_min, RSN_min]
        param_max_lst = [k_max, RSN_max]
        # test = population_current
        for particleIdx, particle in enumerate(population_current):
            for dnaIdx, dnaData in enumerate(particle):
                if population_current[particleIdx, dnaIdx] < param_min_lst[dnaIdx]:
                    population_current[particleIdx, dnaIdx] = self.roundUpFloat(param_min_lst[dnaIdx] + random.uniform(0, 1)*(param_max_lst[dnaIdx] - param_min_lst[dnaIdx]))
                elif population_current[particleIdx, dnaIdx] > param_max_lst[dnaIdx]:
                    population_current[particleIdx, dnaIdx] = self.roundUpFloat(param_min_lst[dnaIdx] + random.uniform(0, 1)*(param_max_lst[dnaIdx] - param_min_lst[dnaIdx]))

        
        return population_current
    
    """
    find best fitness
    """
    def findIdxOfparticle_best(self, fitness_best_population):
        for idx, best_particle_fitness in enumerate(fitness_best_population):
            if best_particle_fitness == min(fitness_best_population):
                break
        return idx
    
    def model_testing(self, model_, category):
        model = model_
        model.fit(self.xTrain, self.yTrain)
        yTestPredicted = model.predict(self.xTest)
        draw_histo(self.yTest, 'Histogram of Output in Test', 'royalblue', 0)
        self.plotTrueAndPredicted(self.xTest, self.yTest, yTestPredicted, f"({category}) [Test]")
        
    def bestModel(self, metricHistory, Gbest):    # To see the performance of the best model
        for i in range(len(metricHistory)):
            if metricHistory[i] == min(metricHistory):
                # edit the part below when model is changed
                RSN = int(Gbest[-1])
                k = int(Gbest[0])
                xTrain, yTrain = shuffle(self.xTrain, self.yTrain, random_state=RSN)
                kf = KFold(n_splits=self.kfold_num)
                train_metric_lst = np.zeros((self.kfold_num, 2))
                val_metric_lst = np.zeros((self.kfold_num, 2))
                model_lst = []
                for idx, (train_idx, val_idx) in enumerate(kf.split(xTrain)):
                    metric = 'mape'
                    metrics = ['mape', 'rmse']
                    # metrics = [mean_absolute_percentage_error, r2_score]
                    model = KNeighborsRegressor(n_neighbors=k)
                    x_train = xTrain[train_idx]
                    y_train = yTrain[train_idx]
                    x_val = xTrain[val_idx]
                    y_val = yTrain[val_idx]
                    evalset = [(x_train, y_train), (x_val, y_val)]
                    model.fit(x_train, y_train)
                    try:
                        yValPredicted = model.predict(x_val)
                        model_lst.append(model)
                    except:
                        # when k > n_val
                        model = KNeighborsRegressor(n_neighbors=x_val.shape[0])
                        model.fit(x_train, y_train)
                        yValPredicted = model.predict(x_val)
                        model_lst.append(model)
                    # self.show_train_history(results, metrics, idx)
                    yTrainPredicted = model.predict(x_train)
                    r2_train = r2_score(y_train, yTrainPredicted)
                    mape_train = mean_absolute_percentage_error(y_train, yTrainPredicted) * 100
                    train_metric_lst[idx] = (np.array([mape_train, r2_train]))
            
                    r2_val = r2_score(y_val, yValPredicted)
                    mape_val = mean_absolute_percentage_error(y_val, yValPredicted) * 100
                    val_metric_lst[idx] = np.array([mape_val, r2_val])
                    # draw_histo(y_val, f'Histogram of Output in Fold {idx+1}', 'seagreen', 0)
                    
        self.plot_metrics_folds(train_metric_lst, val_metric_lst, 'last', 'best')
        try:
            highest_valR2_idx = np.where(val_metric_lst[:, 1] == np.max(val_metric_lst[:, 1]))[0][0]
        except:
            print(val_metric_lst[:, 1])
            highest_valR2_idx = 0
        best_model = model_lst[highest_valR2_idx]
        self.model_testing(best_model, 'kNN_PSO')
        
        return best_model
    
    def plot_fitness(self, fit_history):
        plt.figure(figsize=(10, 7), dpi=300)
        x_axis = np.arange(1, fit_history.shape[0]+1, 1)
        plt.plot(x_axis, fit_history[:, 0], '-o', lw=2)
        plt.plot(x_axis, fit_history[:, 1], '-o', lw=2)
        plt.grid()
        plt.xlabel('Iteration', fontsize=24)
        plt.ylabel('Fitness', fontsize=24)
        plt.xticks(x_axis, fontsize=22)
        plt.yticks(fontsize=22)
        plt.legend(['Min. fitness', 'Average fitness'], fontsize=20)
    
    """
    pso
    use this function only when performing pso
    """
    def pso(self, particleAmount=10, maxIterTime=10):
        metricHistory = []
        metricHistory.append(1000)

        DNA_amount = self.dna_amount
        fitnessHistory0 = []
        fitnessHistory1 = []
        
        # set up initial particle population
        population_current = self.population_currentInitialize(particleAmount)   # Initial population
        population_new = np.zeros((particleAmount, DNA_amount))          
        velocity = 0 * population_current # Initial velocity
        velocity_new = np.zeros((particleAmount, DNA_amount))
        
        
        IterTime = 0
        
        # edit the part below when model is changed
        dna_kind = ['k', 'RandomSeedNum']
        # iteration for best particle
        while IterTime < maxIterTime:
            # print(f'Iter. time: {IterTime}')
            # print('iteration: ', IterTime)
            fitness_current_population = np.zeros(len(population_current))
            for particleIdx, particle in enumerate(population_current):
                # print(f'Particle: {particleIdx}')
                for dnaIdx, dna in enumerate(dna_kind):
                    locals()[dna] = particle[dnaIdx]

                # training result of current particle
                # edit the part below when model is changed
                fitness_current_population[particleIdx], metricHistory = self.modelTraining(locals()[dna_kind[0]], locals()[dna_kind[1]], metricHistory, IterTime, particleIdx)
            
            # first iteration
            if IterTime == 0:
                population_current = population_current
                velocity = velocity
                population_best = copy.deepcopy(population_current)
                fitness_best_population = copy.deepcopy(fitness_current_population)
                
            
            # rest iteration
            else:
                for particleIdx in range(particleAmount):   # recycling same fitness/population array
                    if fitness_current_population[particleIdx] < fitness_best_population[particleIdx]:
                        population_best[particleIdx,:] = copy.deepcopy(population_current[particleIdx,:])
                        fitness_best_population[particleIdx] = copy.deepcopy(fitness_current_population[particleIdx])
                    else:
                        population_best[particleIdx,:] = copy.deepcopy(population_best[particleIdx,:])
                        fitness_best_population[particleIdx] = copy.deepcopy(fitness_best_population[particleIdx])
            
            idx_best_particle = self.findIdxOfparticle_best(fitness_best_population)   
            particle_best = population_best[idx_best_particle,:]
            
            fitnessHistory0.append(min(fitness_best_population))
            fitnessHistory1.append(np.mean(fitness_best_population))
            
            if abs(np.mean(fitness_best_population)-min(fitness_best_population)) < 0.05: #convergent criterion
                print('PSO is ended because of convergence')
                break
            # https://towardsdatascience.com/particle-swarm-optimization-visually-explained-46289eeb2e14
            w = 0.4*(IterTime-particleAmount)/particleAmount**2 + 0.4
            c1 = 3.5 - 3*(IterTime/particleAmount)
            c2 = 3.5 + 3*(IterTime/particleAmount)
            r1 = np.zeros((particleAmount, DNA_amount))
            r2 = np.zeros((particleAmount, DNA_amount))
            for particleIdx in range(particleAmount):
                for dnaIdx in range(DNA_amount):
                    r1[particleIdx, dnaIdx] = random.uniform(0, 1)
                    r2[particleIdx, dnaIdx] = random.uniform(0, 1)
                    
            particle_best = particle_best.reshape(1, -1)
            
            # making new population
            for particleIdx in range(particleAmount):
                for dnaIdx in range(DNA_amount):
                    # w_max = 0.9
                    # w_min = 0.4
                    # w = (w_max - w_min)*(maxIterTime - IterTime) / maxIterTime + w_min
                    velocity_new[particleIdx, dnaIdx] = w * velocity[particleIdx, dnaIdx] + c1 * r1[particleIdx, dnaIdx] * (population_best[particleIdx, dnaIdx] - population_current[particleIdx, dnaIdx]) + c2*r2[particleIdx, dnaIdx] * (particle_best[0, dnaIdx] - population_current[particleIdx, dnaIdx])
                    population_new[particleIdx, dnaIdx] = population_current[particleIdx, dnaIdx] + velocity_new[particleIdx, dnaIdx]
            
            population_current = copy.deepcopy(population_new)
            velocity = copy.deepcopy(velocity_new)
            
            population_current = self.particleBoundary(population_current)

            for particleIdx in range(particleAmount):
                for dnaIdx in range(DNA_amount):
                    population_current[particleIdx, dnaIdx] = self.roundUpInt(population_current[particleIdx, dnaIdx])


                
            IterTime += 1
            
        # final iteration
        # edit the part below when model is changed
        fitness_current_population = np.zeros(len(population_current))
        for particleIdx in range(len(population_current)):
            for dnaIdx, dna in enumerate(dna_kind):
                locals()[dna] = population_current[particleIdx, dnaIdx]
                fitness_current_population[particleIdx], metricHistory = self.modelTraining(locals()[dna_kind[0]], locals()[dna_kind[1]], metricHistory, '(Last)', 'Best')
                
        for particleIdx in range(particleAmount):
            if fitness_current_population[particleIdx] < fitness_best_population[particleIdx]:
                population_best[particleIdx, :] = copy.deepcopy(population_current[particleIdx, :])
                fitness_best_population[particleIdx] = copy.deepcopy(fitness_current_population[particleIdx])
            else:
                population_best[particleIdx,:] = copy.deepcopy(population_best[particleIdx,:])
                fitness_best_population[particleIdx] = copy.deepcopy(fitness_best_population[particleIdx])
                
        idx_best_particle = self.findIdxOfparticle_best(fitness_best_population)                
        particle_best = population_best[idx_best_particle,:]
                
        fitnessHistory0.append(min(fitness_best_population))
        fitnessHistory1.append(np.mean(fitness_best_population))
        fitnessHistory0 = np.array(fitnessHistory0)
        fitnessHistory1 = np.array(fitnessHistory1)
        fitnessHistory = np.hstack((fitnessHistory0, fitnessHistory1))
        ll = float(len(fitnessHistory))/2
        fitnessHistory = fitnessHistory.reshape(int(ll), 2, order='F')
        
        history1 = []
        
        for i in range(len(metricHistory)):
            if metricHistory[i] < 1000 and metricHistory[i] > min(metricHistory):
                history1.append(metricHistory[i])

        
        optimal_model = self.bestModel(metricHistory, particle_best)
        self.plot_fitness(fitnessHistory)
        return optimal_model, fitnessHistory
