'''
This file contains methods for initialising random variables, such as U, V, tau, etc.
We either use the expectation or random draws of the prior distributions.
'''

from updates import update_tau_gaussian
from distributions.normal import normal_draw
from distributions.exponential import exponential_draw
from distributions.exponential import truncated_normal_draw
from distributions.exponential import half_normal_draw

import itertools
import numpy


def initialise_tau_gamma(alpha, beta, R, M, U, V):
    """ Initialise tau using the model updates. """
    return update_tau_gaussian(alpha=alpha, beta=beta, R=R, M=M, U=U, V=V)

def initialise_Z_multinomial():
    #TODO:
    pass

def initialise_U_gaussian(init, I, K, lamb):
    """ Initialise U, with prior Ui ~ N(0,I/lamb). """
    U = numpy.zeros((I,K))
    for i,k in itertools.product(range(I),range(K)):
        U[i,k] = ( normal_draw(mu=0, tau=lamb) if init == 'random' else 0. )
    return U

def initialise_U_exponential(init, I, K, lamb):
    """ Initialise U, with prior Uik ~ Exp(lamb). """
    U = numpy.zeros((I,K))
    for i,k in itertools.product(range(I),range(K)):
        U[i,k] = ( exponential_draw(lambdax=lamb) if init == 'random' else 1./lamb )
    return U

def initialise_U_truncated_normal(init, I, K, mu, tau):
    """ Initialise U, with prior Uik ~ TruncatedNormal(mu,tau). """
    U = numpy.zeros((I,K))
    for i,k in itertools.product(range(I),range(K)):
        U[i,k] = ( truncated_normal_draw(mu=mu, tau=tau) if init == 'random' else TODO )
    return U

def initialise_U_half_normal(init, I, K, sigma):
    """ Initialise U, with prior Uik ~ HalfNormal(sigma). """
    U = numpy.zeros((I,K))
    for i,k in itertools.product(range(I),range(K)):
        U[i,k] = ( half_normal_draw(sigma=sigma) if init == 'random' else TODO )
    return U

#TODO: many more