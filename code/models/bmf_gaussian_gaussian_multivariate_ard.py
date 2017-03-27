"""
Bayesian Matrix Factorisation with Gaussian likelihood and Gaussian priors
(multivariate posterior) and ARD.

Rij ~ N(Ui*Vj,tau^-1),   Ui ~ N(0,I/lamb),             Vj ~ N(0,I/lamb), 
tau ~ Gamma(alpha,beta), lamb_k ~ Gamma(alpha0,beta0)

Random variables: U, V, tau.
Hyperparameters: alpha, beta, lamb.
"""

from bmf import BMF
from Gibbs.updates import update_tau_gaussian
from Gibbs.updates import update_U_gaussian_gaussian_multivariate_ard
from Gibbs.updates import update_V_gaussian_gaussian_multivariate_ard
from Gibbs.updates import update_lambda_gaussian_gaussian_ard
from Gibbs.initialise import initialise_tau_gamma
from Gibbs.initialise import initialise_U_gaussian
from Gibbs.initialise import initialise_lamb_ard

import numpy
import time

METRICS = ['MSE', 'R^2', 'Rp']
OPTIONS_INIT = ['random', 'exp']
DEFAULT_HYPERPARAMETERS = {
    'alpha': 1.,
    'beta': 1.,
    'alpha0': 1.,
    'beta0': 1.,
}

class BMF_Gaussian_Gaussian_multivariate_ARD(BMF):
    def __init__(self,R,M,K,hyperparameters={}):
        """ Set up the class. """
        self.R = numpy.array(R,dtype=float)
        self.M = numpy.array(M,dtype=float)
        self.K = K
        
        assert len(self.R.shape) == 2, "Input matrix R is not a two-dimensional array, " \
            "but instead %s-dimensional." % len(self.R.shape)
        assert self.R.shape == self.M.shape, "Input matrix R is not of the same size as " \
            "the indicator matrix M: %s and %s respectively." % (self.R.shape,self.M.shape)
            
        (self.I,self.J) = self.R.shape
        self.size_Omega = self.M.sum()
        self.check_empty_rows_columns()      
        
        self.alpha =   hyperparameters.get('alpha',  DEFAULT_HYPERPARAMETERS['alpha'])
        self.beta =    hyperparameters.get('beta',   DEFAULT_HYPERPARAMETERS['beta'])   
        self.alpha0 =  hyperparameters.get('alpha0', DEFAULT_HYPERPARAMETERS['alpha0']) 
        self.beta0 =   hyperparameters.get('beta0',  DEFAULT_HYPERPARAMETERS['beta0'])  
        
        
    def initialise(self,init):
        """ Initialise the values of the random variables in this model. """
        assert init in OPTIONS_INIT, \
            "Unknown initialisation option: %s. Should be one of %s." % (init, OPTIONS_INIT)
        self.lamb = initialise_lamb_ard(
            init=init, K=self.K, alpha0=self.alpha0, beta0=self.beta0)
        self.U = initialise_U_gaussian(init=init, I=self.I, K=self.K, lamb=self.lamb)
        self.V = initialise_U_gaussian(init=init, I=self.J, K=self.K, lamb=self.lamb)
        self.tau = initialise_tau_gamma(
            alpha=self.alpha, beta=self.beta, R=self.R, M=self.M, U=self.U, V=self.V)
        
        
    def run(self,iterations):
        """ Run the Gibbs sampler for the specified number of iterations. """
        self.all_U = numpy.zeros((iterations,self.I,self.K))  
        self.all_V = numpy.zeros((iterations,self.J,self.K))   
        self.all_lamb = numpy.zeros((iterations,self.K))
        self.all_tau = numpy.zeros(iterations) 
        self.all_times = []
        self.all_performances = { metric: [] for metric in METRICS } 
        
        time_start = time.time()
        for it in range(iterations):
            # Update the random variables
            self.U = update_U_gaussian_gaussian_multivariate_ard(
                lamb=self.lamb, R=self.R, M=self.M, V=self.V, tau=self.tau) 
            self.V = update_V_gaussian_gaussian_multivariate_ard(
                lamb=self.lamb, R=self.R, M=self.M, U=self.U, tau=self.tau)
            self.lamb = update_lambda_gaussian_gaussian_ard(
                alpha0=self.alpha0, beta0=self.beta0, U=self.U, V=self.V)
            self.tau = update_tau_gaussian(
                alpha=self.alpha, beta=self.beta, R=self.R, M=self.M, U=self.U, V=self.V)
            
            # Store the draws
            self.all_U[it], self.all_V[it] = numpy.copy(self.U), numpy.copy(self.V)
            self.all_lamb[it] = numpy.copy(self.lamb)
            self.all_tau[it] = self.tau
            
            # Print the performance, store performance and time
            perf = self.predict_while_running()
            for metric in METRICS:
                self.all_performances[metric].append(perf[metric])
            time_iteration = time.time()
            self.all_times.append(time_iteration-time_start)   
            print "Iteration %s. MSE: %s. R^2: %s. Rp: %s." % (it+1,perf['MSE'],perf['R^2'],perf['Rp'])
