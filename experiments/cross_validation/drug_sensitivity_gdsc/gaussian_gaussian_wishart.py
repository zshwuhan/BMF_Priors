'''
Run nested cross-validation experiment on the GDSC drug sensitivity dataset, with 
the All Gaussian model (multivariate posterior) and Wishart prior.
'''

project_location = "/Users/thomasbrouwer/Documents/Projects/libraries/"
import sys
sys.path.append(project_location)

from BMF_Priors.code.models.bmf_gaussian_gaussian_wishart import BMF_Gaussian_Gaussian_Wishart
from BMF_Priors.code.cross_validation.nested_matrix_cross_validation import MatrixNestedCrossValidation
from BMF_Priors.data.drug_sensitivity.load_data import load_gdsc_ic50_integer


''' Settings BMF model. '''
method = BMF_Gaussian_Gaussian_Wishart
R, M = load_gdsc_ic50_integer()
hyperparameters = { 'alpha':1., 'beta':1., 'mu0':0., 'beta0':1., 'W0':1. }
train_config = {
    'iterations' : 200,
    'init' : 'random',
}
predict_config = {
    'burn_in' : 180,
    'thinning' : 2,
}


''' Settings nested cross-validation. '''
K_range = [5,6,7,8,9]
no_folds = 10
no_threads = 5
parallel = False
folder_results = './results/gaussian_gaussian_wishart/'
output_file = folder_results+'results.txt'
files_nested_performances = [folder_results+'fold_%s.txt'%(fold+1) for fold in range(no_folds)]


''' Construct the parameter search. '''
parameter_search = [{'K':K, 'hyperparameters':hyperparameters} for K in K_range]


''' Run the cross-validation framework. '''
nested_crossval = MatrixNestedCrossValidation(
    method=method,
    R=R,
    M=M,
    K=no_folds,
    P=no_threads,
    parameter_search=parameter_search,
    train_config=train_config,
    predict_config=predict_config,
    file_performance=output_file,
    files_nested_performances=files_nested_performances,
)
nested_crossval.run(parallel=parallel)