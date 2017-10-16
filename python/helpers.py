import json
import numpy as np
import matplotlib.pylab as plt
import seaborn as sns
from palettable.colorbrewer.qualitative import Dark2_8
from scipy.stats import gaussian_kde

def buildPhiMatrix(observations, order, inputs = False):
    noObservations = len(observations)
    if isinstance(inputs, bool):
        Phi = np.zeros((noObservations, order + 1))
        for i in range(order, noObservations):
            Phi[i, :] = observations[range(i, i - order - 1, -1)]
        return Phi[order:, :]
    else:
        Phi = np.zeros((noObservations, order[0] + order[1]))
        for i in range(int(np.max(order)), noObservations):
            Phi[i, :] = np.hstack((-observations[range(i-1, i - order[0] - 1, -1)], inputs[range(i, i - order[1], -1)]))
        return Phi[int(np.max(order)):, :]

# From https://stackoverflow.com/questions/36200913/generate-n-random-numbers-from-a-skew-normal-distribution-using-numpy
def randn_skew_fast(N, alpha=0.0, loc=0.0, scale=1.0):
    sigma = alpha / np.sqrt(1.0 + alpha**2) 
    u0 = np.random.randn(N)
    v = np.random.randn(N)
    u1 = (sigma*u0 + np.sqrt(1.0 - sigma**2)*v) * scale
    u1[u0 < 0] *= -1
    u1 = u1 + loc
    return u1

def plotResultsMixtures(model, observations, gridPoints, name):
    fig1 = plt.figure(1)
    plt.subplot(3, 2, (1, 2))
    kernelDensityEstimator = gaussian_kde(observations)
    trueMixtureDensity = kernelDensityEstimator(gridPoints)
    estMixtureDensity = np.mean(np.exp(model.extract("log_p_y_tilde")['log_p_y_tilde']), axis=0)
    plt.plot(gridPoints, trueMixtureDensity, 'b', gridPoints, estMixtureDensity ,'g')
    sns.despine(left=False, bottom=False, right=True)
    plt.xlabel("x")
    plt.ylabel("p(x)")

    plt.subplot(3, 2, 3)
    for i in range(5):
            sns.distplot(model.extract("mu")['mu'][:, i], color = Dark2_8.mpl_colors[i])
    sns.despine(left=False, bottom=False, right=True)
    plt.xlabel("mu")
    plt.ylabel("posterior estimate")

    plt.subplot(3, 2, 4)
    for i in range(5):
            sns.distplot(model.extract("sigma")['sigma'][:, i], color = Dark2_8.mpl_colors[i])
    sns.despine(left=False, bottom=False, right=True)
    plt.xlabel("sigma")
    plt.ylabel("posterior estimate")

    plt.subplot(3, 2, 5)
    sns.distplot(model.extract("sigma0")['sigma0'], color = Dark2_8.mpl_colors[6])
    sns.despine(left=False, bottom=False, right=True)
    plt.xlabel("sigma0")
    plt.ylabel("posterior estimate")

    plt.subplot(3, 2, 6)
    sns.distplot(model.extract("e0")['e0'], color = Dark2_8.mpl_colors[7])
    sns.despine(left=False, bottom=False, right=True)
    plt.xlabel("e0")
    plt.ylabel("posterior estimate")
    plt.show(fig1)
    fig1.savefig(name + '_posteriors.png')
    plt.close(fig1)

    fig2 = plt.figure(2)
    for i in range(5):
            plt.subplot(5, 2, 2*i + 1)
            plt.plot(model.extract("mu")['mu'][:, i], color = Dark2_8.mpl_colors[i])
            plt.xlabel("mu")
            plt.ylabel("Trace")
            plt.subplot(5, 2, 2*i + 2)
            plt.plot(model.extract("sigma")['sigma'][:, i], color = Dark2_8.mpl_colors[i])
            plt.xlabel("sigma")
            plt.ylabel("Trace")
    plt.show(fig2)
    fig2.savefig(name + '_traces.png')
    plt.close(fig2)


def saveResultsMixtures(gridPoints, observations, model, name):
    
    kernelDensityEstimator = gaussian_kde(observations)
    trueMixtureDensity = kernelDensityEstimator(gridPoints)
    estMixtureDensity = np.mean(np.exp(model.extract("log_p_y_tilde")['log_p_y_tilde']), axis=0)

    results = {}
    results.update({'kernelDensityEstimate': trueMixtureDensity.tolist()})
    results.update({'MCMCDensityEstimate': estMixtureDensity.tolist()})
    results.update({'sigma0': model.extract("sigma0")['sigma0'].tolist()})
    results.update({'e0': model.extract("e0")['e0'].tolist()})
    results.update({'weights': model.extract("weights")['weights'].tolist()})
    results.update({'mu': model.extract("mu")['mu'].tolist()})
    results.update({'sigma': model.extract("sigma")['sigma'].tolist()})
    results.update({'observations': observations.tolist()})
    results.update({'gridPoints': gridPoints.tolist()})
    results.update({'name': name})

    with open('example2_' + name + '.json', 'w') as f:
        json.dump(results, f, ensure_ascii=False)


def saveResultsFIR(observations, inputs, model, name):
    
    results = {}
    results.update({'mu': model.extract("mu")['mu'].tolist()})
    results.update({'b': model.extract("b")['b'].tolist()})
    results.update({'sigma': model.extract("sigma")['sigma'].tolist()})
    results.update({'sigma0': model.extract("sigma0")['sigma0'].tolist()})
    results.update({'observations': observations.tolist()})
    results.update({'inputs': inputs.tolist()})
    results.update({'name': name})

    with open('example1_' + name + '.json', 'w') as f:
        json.dump(results, f, ensure_ascii=False)

def saveResultsChebyData(data, model, name, scaleModelCoefficients = True):

    predictiveMeanTrace = model.extract("predictiveMean")['predictiveMean'][:, data['systemOrder']:]
    predictiveMean = np.mean(predictiveMeanTrace, axis=0)
    predictiveMeanVariance = np.var(predictiveMeanTrace, axis=0)

    results = {}
    results.update({'modelCoefficients': model.extract("modelCoefficients")['modelCoefficients'].tolist()})
    results.update({'observationNoiseVariance': model.extract("observationNoiseVariance")['observationNoiseVariance'].tolist()})

    if scaleModelCoefficients:
        results.update({'scaleModelCoefficients': model.extract("scaleModelCoefficients")['scaleModelCoefficients'].tolist()})
        
    results.update({'predictiveMean': predictiveMean.tolist()})
    results.update({'predictiveMeanVariance': predictiveMeanVariance.tolist()})
    results.update({'trainingData': data['yEstimation'].tolist()})
    results.update({'evaluationData': data['yValidation'].tolist()})
    results.update({'trueOrder': np.array(data['trueOrder']).tolist()})    
    results.update({'guessedOrder': np.array(data['guessedOrder']).tolist()})        
    results.update({'coefficientsA': data['coefficientsA'].tolist()})
    results.update({'coefficientsB': data['coefficientsB'].tolist()})
    results.update({'name': name})

    with open('example0_' + name + '.json', 'w') as f:
        json.dump(results, f, ensure_ascii=False)

def saveResultsARXMixture(data, model, name):

    gridPoints = data['gridPoints']
    trainingData = data['trainingData']
    evaluationData = data['evaluationData']

    kernelDensityEstimator = gaussian_kde(trainingData)
    trueMixtureDensity = kernelDensityEstimator(gridPoints)
    estMixtureDensity = np.mean(np.exp(model.extract("mixtureOnGrid")['mixtureOnGrid']), axis=0)
    predictiveMeanTrace = model.extract("predictiveMean")['predictiveMean'][:, data['maxLag']:]
    predictiveMean = np.mean(predictiveMeanTrace, axis=0)
    predictiveMeanVariance = np.var(predictiveMeanTrace, axis=0)
    predictiveVariance = np.mean(model.extract("predictiveVariance")['predictiveVariance'][:, data['maxLag']:], axis=0)

    results = {}
    results.update({'kernelDensityEstimate': trueMixtureDensity.tolist()})
    results.update({'MCMCDensityEstimate': estMixtureDensity.tolist()})
    results.update({'predictiveMean': predictiveMean.tolist()})
    results.update({'predictiveMeanVariance': predictiveMeanVariance.tolist()})
    results.update({'predictiveVariance': predictiveVariance.tolist()})
    results.update({'filterCoefficient': model.extract("filterCoefficient")['filterCoefficient'].tolist()})
    results.update({'mixtureWeightsPrior': model.extract("mixtureWeightsPrior")['mixtureWeightsPrior'].tolist()})
    results.update({'filterCoefficientPrior': model.extract("filterCoefficientPrior")['filterCoefficientPrior'].tolist()})
    results.update({'mixtureMeanPrior': model.extract("mixtureMeanPrior")['mixtureMeanPrior'].tolist()})
    results.update({'mixtureWeights': model.extract("mixtureWeights")['mixtureWeights'].tolist()})
    results.update({'mixtureMean': model.extract("mixtureMean")['mixtureMean'].tolist()})
    results.update({'mixtureVariance': model.extract("mixtureVariance")['mixtureVariance'].tolist()})
    results.update({'trainingData': trainingData.tolist()})
    results.update({'evaluationData': evaluationData.tolist()})
    results.update({'gridPoints': gridPoints.tolist()})
    results.update({'name': name})

    with open('example4_' + name + '.json', 'w') as f:
        json.dump(results, f, ensure_ascii=False)

def saveResultsFIRMixture(data, model, name):
    gridPoints = data['gridPoints']
    yEstimation = data['yEstimation']
    yValidation = data['yValidation']
    regressorMatrixEstimation = data['regressorMatrixEstimation']
    regressorMatrixValidation = data['regressorMatrixValidation']

    kernelDensityEstimator = gaussian_kde(np.hstack((yEstimation, yValidation)))
    trueMixtureDensity = kernelDensityEstimator(gridPoints)
    estMixtureDensity = np.mean(model.extract("mixtureOnGrid")['mixtureOnGrid'], axis=0)
    predictiveMeanTrace = model.extract("predictiveMean")['predictiveMean']
    predictiveMean = np.mean(predictiveMeanTrace, axis=0)
    predictiveMeanVariance = np.var(predictiveMeanTrace, axis=0)
    predictiveVariance = np.mean(model.extract("predictiveVariance")['predictiveVariance'], axis=0)
    predictiveWeight = np.mean(model.extract("predictiveWeight")['predictiveWeight'], axis=0)

    results = {}
    results.update({'kernelDensityEstimate': trueMixtureDensity.tolist()})
    results.update({'MCMCDensityEstimate': estMixtureDensity.tolist()})
    results.update({'predictiveWeight': predictiveWeight.tolist()})
    results.update({'predictiveMean': predictiveMean.tolist()})
    results.update({'predictiveVariance': predictiveVariance.tolist()})
    results.update({'filterCoefficient': model.extract("filterCoefficient")['filterCoefficient'].tolist()})
    #results.update({'mixtureWeightsPrior': model.extract("mixtureWeightsPrior")['mixtureWeightsPrior'].tolist()})
    #results.update({'filterCoefficientPrior': model.extract("filterCoefficientPrior")['filterCoefficientPrior'].tolist()})
    #results.update({'mixtureMeanPrior': model.extract("mixtureMeanPrior")['mixtureMeanPrior'].tolist()})
    results.update({'mixtureWeights': model.extract("mixtureWeights")['mixtureWeights'].tolist()})
    results.update({'mixtureMean': model.extract("mixtureMean")['mixtureMean'].tolist()})
    #results.update({'mixtureVariance': model.extract("mixtureVariance")['mixtureVariance'].tolist()})
    results.update({'yValidation': yValidation.tolist()})
    results.update({'yEstimation': yEstimation.tolist()})
    results.update({'regressorMatrixEstimation': regressorMatrixEstimation.tolist()})
    results.update({'regressorMatrixValidation': regressorMatrixValidation.tolist()})    
    results.update({'gridPoints': gridPoints.tolist()})
    results.update({'name': name})
    results.update({'inputSignal': data['inputs'].tolist()})
    results.update({'outputSignal': data['observations'].tolist()})
    results.update({'trueOrder': np.array(data['trueOrder']).tolist()})    
    results.update({'guessedOrder': np.array(data['guessedOrder']).tolist()})        
    results.update({'coefficientsA': data['coefficientsA'].tolist()})
    results.update({'coefficientsB': data['coefficientsB'].tolist()})

    with open('example3_' + name + '.json', 'w') as f:
            json.dump(results, f, ensure_ascii=False)        

def generatePRBS(N, maxHold=10):
    randomSignal = np.random.choice((-1, 1), N)
    outputSignal = []

    j = 0
    while len(outputSignal) < N:
        outputSignal.append(np.ones(1 + np.random.choice(maxHold)) * randomSignal[j])
        j += 1

    return(np.concatenate(outputSignal, axis=0)[:N])