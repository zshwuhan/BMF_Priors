"""
Bayesian Matrix Factorisation with Gaussian likelihood and Laplace priors, and 
hierarchical Inverse Gaussian prior.

Rij ~ N(Ui*Vj,tau^-1), tau ~ Gamma(alpha,beta), 
Uik ~ L(0, etaUik), etaUik ~ GIG(gamma=-1/2, a, b)
Vjk ~ L(0, etaVjk), etaVjk ~ GIG(gamma=-1/2, a, b)

Random variables: U, V, tau.
Hyperparameters: alpha, beta, a, b.
"""

from bmf import BMF
from Gibbs.updates import update_tau_gaussian
from Gibbs.updates import update_U_gaussian_laplace
from Gibbs.updates import update_V_gaussian_laplace
from Gibbs.updates import update_lambdaU_gaussian_laplace
from Gibbs.updates import update_lambdaV_gaussian_laplace
from Gibbs.updates import update_etaU_gaussian_laplace
from Gibbs.updates import update_etaV_gaussian_laplace
from Gibbs.initialise import initialise_tau_gamma
from Gibbs.initialise import initialise_U_laplace
from Gibbs.initialise import initialise_lambdaU_laplace
from Gibbs.initialise import initialise_etaU_laplace

import numpy
import time

METRICS = ['MSE', 'R^2', 'Rp']
OPTIONS_INIT = ['random', 'exp']
DEFAULT_HYPERPARAMETERS = {
    'alpha': 1.,
    'beta': 1.,
    'eta': 0.1,
    #'a': 1./K,
    #'b': K,
}

class BMF_Gaussian_Laplace_IG(BMF):
    def __init__(self,R,M,K,hyperparameters={}):
        """ Set up the class. """
        super(BMF_Gaussian_Laplace_IG, self).__init__(R, M, K)
        self.alpha = hyperparameters.get('alpha', DEFAULT_HYPERPARAMETERS['alpha'])
        self.beta =  hyperparameters.get('beta',  DEFAULT_HYPERPARAMETERS['beta'])   
        self.eta =   hyperparameters.get('eta',   DEFAULT_HYPERPARAMETERS['eta']) 
        self.a =     hyperparameters.get('a',     1. / K) 
        self.b =     hyperparameters.get('b',     K) 
        
        
    def initialise(self,init):
        """ Initialise the values of the random variables in this model. """
        assert init in OPTIONS_INIT, \
            "Unknown initialisation option: %s. Should be one of %s." % (init, OPTIONS_INIT)
        self.etaU = initialise_etaU_laplace(init=init, I=self.I, K=self.K, a=self.a, b=self.b)
        self.etaV = initialise_etaU_laplace(init=init, I=self.J, K=self.K, a=self.a, b=self.b)
        self.U = initialise_U_laplace(init=init, I=self.I, K=self.K, etaU=self.etaU)
        self.V = initialise_U_laplace(init=init, I=self.J, K=self.K, etaU=self.etaV)
        self.lambdaU = initialise_lambdaU_laplace(init=init, I=self.I, K=self.K, etaU=self.etaU)
        self.lambdaV = initialise_lambdaU_laplace(init=init, I=self.J, K=self.K, etaU=self.etaV)
        self.tau = initialise_tau_gamma(
            alpha=self.alpha, beta=self.beta, R=self.R, M=self.M, U=self.U, V=self.V)
        
        
    def run(self,iterations):
        """ Run the Gibbs sampler for the specified number of iterations. """
        self.all_U = numpy.zeros((iterations,self.I,self.K))  
        self.all_V = numpy.zeros((iterations,self.J,self.K))   
        self.all_tau = numpy.zeros(iterations) 
        self.all_times = []
        self.all_performances = { metric: [] for metric in METRICS } 
        
        time_start = time.time()
        for it in range(iterations):
            # Update the random variables
            self.lambdaU = update_lambdaU_gaussian_laplace(U=self.U, etaU=self.eta)
            self.etaU = update_etaU_gaussian_laplace(lambdaU=self.lambdaU, a=self.a, b=self.b)
            self.U = update_U_gaussian_laplace(
                R=self.R, M=self.M, V=self.V, lambdaU=self.lambdaU, tau=self.tau) 
            self.lambdaV = update_lambdaV_gaussian_laplace(V=self.V, etaV=self.eta)
            self.etaV = update_etaV_gaussian_laplace(lambdaV=self.lambdaV, a=self.a, b=self.b)
            self.V = update_V_gaussian_laplace(
                R=self.R, M=self.M, U=self.U, lambdaV=self.lambdaV, tau=self.tau)
            self.tau = update_tau_gaussian(
                alpha=self.alpha, beta=self.beta, R=self.R, M=self.M, U=self.U, V=self.V)
            
            # Store the draws
            self.all_U[it], self.all_V[it] = numpy.copy(self.U), numpy.copy(self.V)
            self.all_tau[it] = self.tau
            
            # Print the performance, store performance and time
            perf = self.predict_while_running()
            for metric in METRICS:
                self.all_performances[metric].append(perf[metric])
            time_iteration = time.time()
            self.all_times.append(time_iteration-time_start)   
            print "Iteration %s. MSE: %s. R^2: %s. Rp: %s." % (it+1,perf['MSE'],perf['R^2'],perf['Rp'])