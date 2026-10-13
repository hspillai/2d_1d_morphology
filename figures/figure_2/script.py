from mpi4py import MPI

import sys
sys.path.append('../../catmap/')
sys.path.append('./../../libs/')

import csv
import numpy as np
import pandas as pd
from functools import partial
from dolfinx import fem, geometry
from scipy.interpolate import CubicSpline

from catmap import ReactionModel

from SolverModule import ElectrolyteSolver
from KineticsModule import KineticSolver
from ConvergenceModule import (screen_initial_guess,
                               calc_error_l2,
                               converge_concentration,
                               run_full_convergence)
from ReadData import CustomData

def get_oned_results(rho, L, U, diff_CO, K_henry, initial_range = np.array([0.98 * 0.04185574,
                                                                            0.04185574,
                                                                            1.02 * 0.04185574])):

    oned_solver = ElectrolyteSolver(mesh_dim = '1D',
                                    coordinate_system = 'cartesian',
                                    active_tags = [1],
                                    dirichlet_tags = [2],\
                                    dirichlet_bcs = [0.0],
                                    l_diff = L,
                                    n_cells = 200)
    
    oned_solver.create_dirchlet()

    kineticSolver = KineticSolver(potential = U,
                                  catmap_mkm_path = '../../kinetic_data/rates.npy',
                                  Dab = diff_CO,
                                  K_henry = K_henry)

    mkm_roughness = lambda c: kineticSolver.run_mkm_roughness(c, rho = rho)
    mkm_roughness_intermediate = lambda c: kineticSolver.run_mkm_roughness_intermediate(c, rho = rho)
    mkm_roughness_product = lambda c: kineticSolver.run_mkm_roughness_product(c, rho = rho)

    initial_c, final_error = screen_initial_guess(solver=oned_solver,
                                                  kinetic_mapper=mkm_roughness,     
                                                  initial_conc_range=initial_range,
                                                  error_fn=calc_error_l2,
                                                  tol=1e-7,
                                                  max_iter=10,
                                                  verbose=True)

    final_conc, return_array = converge_concentration(solver = oned_solver,
                                                      kinetics_mapper=mkm_roughness,
                                                      max_iter = 1000,
                                                      mixing = 0.05,
                                                      tol = 1e-5, # just a rough value for the initial guess for the next step.
                                                      conc_old = initial_c,
                                                      verbose = True,
                                                      save = True)
    
    selectivity= oned_solver.get_selectivity(mkm_roughness_intermediate,
                                             mkm_roughness_product)
    
    return final_conc, selectivity, return_array

def build_spline(x, y):
    sort_idx = np.argsort(x)
    return CubicSpline(x[sort_idx],
                       y[sort_idx])

L = 25 * 1e-6#25e-6
r = 2.5 * 1e-6
U = -1.55

K_henry = 8.972E-6 * 101325  # mol/m3 atm
diff_CO = 20.3e-10

with open('mesh_list.csv', newline='') as f:
    reader = csv.reader(f)
    meshes = list(reader)

meshes = meshes[0]
mesh_df = pd.read_csv('../../meshes/mesh.csv')  # Adjust path as needed
run_meshes = mesh_df[mesh_df['file_name'].isin(meshes)]

data_path = '../../results/'  # or wherever you want to save
custom_data = CustomData(pandas_path=data_path)

i = 0
for _, row in run_meshes.iterrows():    

    mesh_name = row.file_name    
    mesh_path = '../../meshes/' + mesh_name
    rho = row['rho']
    L = row['L']
    print(mesh_name)
    if custom_data.entry_exists(mesh_name):# and mesh_name not in unconverged_meshes:
        print('Exists!')
        continue
    
    if i == 1:
        break

    final_conc_oned, sel_1d, return_array = get_oned_results(row['rho'],
                                                             row['L'],
                                                             U, diff_CO, K_henry)    

    kineticSolver = KineticSolver(potential = U,
                                  catmap_mkm_path = '../../kinetic_data/rates.npy',
                                  Dab = diff_CO,
                                  K_henry = K_henry)
    kineticSolver.load_data()
    kineticSolver.fit_splines()

    print(f"\nRunning geometry {i+1} - mesh: {mesh_path}")
    try:
        solver = ElectrolyteSolver(
            mesh_dim='2D',
            coordinate_system = 'cylindrical',
            mesh_file=mesh_path,
            active_tags=[2],
            inactive_tags=[1],
            dirichlet_tags=[4],
            dirichlet_bcs=[0]
        )
        solver.create_dirchlet()
        
        initial_c, final_error = screen_initial_guess(
            solver=solver,
            kinetic_mapper=kineticSolver.spline_bc,
            initial_conc_range=np.array([0.98, 1.0, 1.02]) * final_conc_oned,
            error_fn=calc_error_l2,
            tol=1e-3,
            max_iter=7,
            verbose=True)
        
        spread = np.linspace(0.9 * initial_c, 1.1 * initial_c, 7)
        kineticSolver.refit_from_catmap(spread)
        concs, converged = run_full_convergence(solver, kineticSolver,
                                                initial_c, verbose = True,
                                                max_iter_2 = 800,
                                                max_iter_3 = 500,
                                                tol = 1e-6)

        tmp_spline = build_spline(solver.surface_coordinates[:, 0],
                                  solver.surface_concentrations)
        selectivity, flux = solver.get_selectivity(kineticSolver.spline_inter_flux,
                                                   kineticSolver.spline_product_flux,
                                                   get_flux = True,
                                                   kinetic_mapper_bc = kineticSolver.spline_bc)
        
        result = {
            'mesh': mesh_name,
            'rho': rho,
            'R': row.R,
            'ipd': row.ipd,
            'r': row.r,
            'L': row.L,
            'sel': selectivity,
            'Selectivity_1d': sel_1d, 
            'Flux/C' : flux,
            'converged': converged,
            'resolution': 'fine'}

        print(selectivity, sel_1d)
        custom_data.add_entry(result)
        custom_data.save_all()
        
        i += 1    

    except Exception as e:
        print(f"Error processing mesh {mesh_name}: {e}")
        break
