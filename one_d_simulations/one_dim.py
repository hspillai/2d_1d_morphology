import sys
sys.path.append('/../catmap/')
sys.path.append('../libs/')

import os
from os import system as shell
from functools import partial

import numpy as np
from ReadData import CustomData
from Kineticmodule import KineticSolver

def transport_model(L, D, flux, C_bulk, rho):
    flux = max(flux, 0)
    c_surf = rho * flux * (L/D) + C_bulk
    return c_surf

def refine_concentration_range(conc_values, min_index, scale = 0.5,
                               num_points = 5):
    if min_index == 0:
        return np.linspace(conc_values[0] * (1 - scale), conc_values[1], num_points)
    elif min_index == len(conc_values) - 1:
        return np.linspace(conc_values[-1], conc_values[-1] * (1 + scale), num_points)
    else:
        return np.linspace(conc_values[min_index - 1], conc_values[min_index + 1], num_points)

def evaluate_guess(c_values, kinetic_solver, transport_solver):             
    errors = []
    prev_f = None
    for c_val in c_values:
        flux = kinetic_solver._run_mkm_raw([c_val])
        C_A = transport_solver(flux = flux)
        f_val = C_A  - c_val                                                                                                                                                                      
        error = abs(f_val)/c_val
        errors.append(error)                                                                                                                                                                                 

        if prev_f is not None: # transport response is decreasing
            if prev_f < 0 and f_val < prev_f:                                                                                                                                                
                print("Stopping: f(c) moving monotonically away from zero")
                break                                                                                                                                      
                                                                                                                                                                                              
        prev_f = f_val
    return errors

def screen_initial_guess(kinetic_mapper,
                         transport_mapper,
                         initial_conc_range,
                         tol = 1e-3,
                         max_iter = 5,
                         rho = 1.0, 
                         verbose = False):
    conc_values = np.array(initial_conc_range)
    for iteration in range(max_iter):

        errors = evaluate_guess(conc_values,
                                kinetic_mapper,
                                transport_mapper)
        min_index = np.argmin(errors)
        best_c = conc_values[min_index]
        best_error = errors[min_index]

        conc_values = refine_concentration_range(conc_values, min_index)

    return best_c, best_error

def secant_method(kinetic_solver, transport_solver,
                  c_init1, c_init2,
                  max_iter=50, tol=1e-4, verbose=True):
    """
    Secant method: approximates derivative using two points.
    Solves: F(c) = T(K(c)) - c = 0
    """
    
    def eval_F(c):
        """Evaluate F(c) = T(K(c)) - c"""
        flux = kinetic_solver._run_mkm_raw([float(c)])
        c_transport = transport_solver(flux=flux)
        return c_transport - c
    
    # Initialize with two guesses
    c_old = c_init1
    c_current = c_init2
    
    F_old = eval_F(c_old)
    F_current = eval_F(c_current)
    
    for it in range(max_iter):
        error = abs(F_current) / max(abs(c_current), 1e-20)
        
        if verbose:
            print(f"Iteration {it+1}: error = {round(error, 3)}, c = {round(c_current, 3)}")                  
        # Check convergence
        if error < tol:
            if verbose:
                print("secant converged!")
            return c_current, True
        
        # Secant approximation of derivative
        if abs(c_current - c_old) < 1e-20:
            if verbose:
                print("Warning: points too close, perturbing")
            c_old = c_current * 0.99
            F_old = eval_F(c_old)
            continue
        
        dF_dc = (F_current - F_old) / (c_current - c_old)
        
        if abs(dF_dc) < 1e-20:
            if verbose:
                print("Warning: derivative near zero")
            c_next = c_current - 0.1 * F_current
        else:
            # Secant step
            delta_c = -F_current / dF_dc
            
            # Limit step size
            max_step = 0.5 * abs(c_current)
            if abs(delta_c) > max_step:
                delta_c = np.sign(delta_c) * max_step
            
            c_next = c_current + delta_c
        
        # Keep positive
        c_next = max(c_next, 1e-25)
        
        # Update for next iteration
        c_old = c_current
        F_old = F_current
        c_current = c_next
        F_current = eval_F(c_current)
    
    if verbose:
        print(f"Secant did not converge after {max_iter} iterations")
    return c_current, False


# we will run one d simulations for all the 3D simulations from results. 
data_path = '../cylinderical/hemisphere/realL/Heatmap_4/results/' # for L = 25
data = CustomData(pandas_path=data_path).scale_column('sel', 100).sort_by('rho').add_ratio_column('r/L', 'r', 'L')
data.df['L'] = data.df['L'].round(10)

isolated_data_path = '/home/pillai/morphology_2d_1d/cylinderical/hemisphere/realL/Heatmap_4/figure4_b/isolated_particle/results/'
isolated_data = CustomData(pandas_path=isolated_data_path).scale_column('sel', 100).sort_by('rho').add_ratio_column('r/L', 'r', 'L')

L_values = np.unique(np.append(data.df['L'].unique() * 1e6, isolated_data.df['L'].unique() * 1e6))# data.df['L'].unique() * 1e6#np.array([1, 5, 25, 50]) # in \mu m
D = 20.3E-10 # m2/s
k_henry = 8.972E-6 * 101325  # mol/m3 atm
p_bulk = 0 # atm
C_bulk = p_bulk * k_henry

# initial guesses for concentration 
C_inits = 10**np.linspace(-15, 1, 25)

u  = -1.55
rhos = np.concatenate([data.df['rho'].unique(),
                       isolated_data.df['rho'].unique() * 0.9,
#                       isolated_data.df['rho'].unique() * 0.75
                       ])

# np.append(data.df['rho'].unique(),
# #                  isolated_data.df['rho'].unique() * 0.10,                  
#                   isolated_data.df['rho'].unique() * 0.05,
#                   isolated_data.df['rho'].unique() * 0.025)  #
# # 0.20
# # 0.025, 0.05

if os.path.exists('results.npy'):
    results = np.load('results.npy',
                      allow_pickle = True)
    print(f"Loaded {len(results)} existing results")
else:
    results = np.zeros([len(rhos) * len(L_values), 5])
#    results = np.zeros((0, 5))
    print("Starting fresh")    

# Convert to list for easier appending
results_list = results.tolist()

for L_ in L_values:
    L = L_ * 1e-6
    for rho in rhos:
        skip = False
        if len(results) > 0:
            for row in results:
#                if (np.isclose(row[1], L) and
                if (np.isclose(row[1] * 1e6, L_) and # easier to compare in micrometers for the smaller numbers
                    np.isclose(row[0], rho)):
                    print(f'Already done: L={L:.2e}, rho={rho}')
                    skip = True
                    break
        if skip:
            continue
        
        # setup transport model
        transportsolver = partial(transport_model, L = L,
                                  D = D, C_bulk = C_bulk,
                                  rho = rho)

        kineticsolver = KineticSolver(potential = u,
                                      catmap_mkm_path = './',
                                      catmap_template_path = './',
                                      species = ['CO'],
                                      K_henry = k_henry,
                                      replace_energies = True) 
    

        errors = evaluate_guess(C_inits,
                                kineticsolver,
                                transportsolver)
    
        C_inits = np.linspace(0.5 * C_inits[np.argmin(errors)],                                       
                              1.5 * C_inits[np.argmin(errors)],     
                              20)
    
        best_c, best_error = screen_initial_guess(kineticsolver,
                                                  transportsolver,
                                                  C_inits,
                                                  max_iter = 10)

        # Use two nearby points to the best guess
        c_init1 = best_c * 0.99
        c_init2 = best_c * 1.01
    
        converged_conc, success = secant_method(
            kineticsolver,
            transportsolver,
            c_init1=c_init1,
            c_init2=c_init2,
            max_iter=50,
            tol=1e-4,
            verbose=False
        )

        kineticsolver.species.append('CHOH_g')

        # we run a catmap model once with the converged concentration so if needed can save additional info i.e. coverages (maybe drcs..)
        catmap_flux = kineticsolver._run_mkm_raw([converged_conc])
        catmap_conc = transportsolver(flux = catmap_flux['CO_g'][0])
        
        sel = catmap_flux['CO_g'][0]/(catmap_flux['CO_g'][0] + catmap_flux['CHOH_g'][0])
        results_list.append([rho, L, catmap_flux['CO_g'][0], catmap_flux['CHOH_g'][0], sel])

results = np.array(results_list)
results = results.astype(float)
np.save('results.npy', results)
