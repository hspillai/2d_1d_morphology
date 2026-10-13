from dolfinx import fem
from SolverModule import ElectrolyteSolver
from KineticsModule import KineticSolver
import numpy as np

def calc_error_l2(conc_new, conc_old):
    return np.linalg.norm(conc_new - conc_old) / np.linalg.norm(conc_new)

def refine_concentration_range(conc_values, min_index, scale=0.5, num_points=20):
    if min_index == 0:
        return np.linspace(conc_values[0] * (1 - scale), conc_values[1], num_points)
    elif min_index == len(conc_values) - 1:
        return np.linspace(conc_values[-1], conc_values[-1] * (1 + scale), num_points)
    else:
        return np.linspace(conc_values[min_index - 1], conc_values[min_index + 1], num_points)

def evaluate_guess(c_values, surface_dofs, flux_func, solver,
                   kinetic_mapper, error_fn, **kwargs):
    errors = []
    rho_val = kwargs.pop("rho", None)  # remove rho from kwargs if it exists    
    for c_val in c_values:
        c_array = np.full_like(flux_func.x.array[surface_dofs], c_val)
        flux_active = kinetic_mapper(c_array, **kwargs)        
        # Apply rho scaling only for 1D simulations
        if rho_val is not None and getattr(solver, "mesh_dim", None) == "1D":
            flux_active = rho_val * flux_active
            print('Going into RHO', rho_val)
        elif rho_val is not None and verbose:
            print("[Warning] rho was passed but solver is not 1D → ignoring rho.")

        flux_func.x.array[surface_dofs] = flux_active
#        flux_func.x.array[surface_dofs] = kinetic_mapper(c_array, **kwargs)
        solver.solve(flux_func)
        solver.get_surface_conc()
        conc_new = solver.surface_concentrations
        error = error_fn(conc_new, c_array)
        errors.append(error)
    return np.array(errors)

def screen_initial_guess(solver,
                         kinetic_mapper,
                         initial_conc_range,
                         error_fn,
                         tol=1e-3,
                         max_iter=5,
                         verbose=False,
                         **kwargs):
    
    flux_func = fem.Function(solver.V)
    conc_values = np.array(initial_conc_range)
    surface_dofs = solver.dofs_dict[solver.active_inxs[0]][1]
    for iteration in range(max_iter):
        errors = evaluate_guess(conc_values, surface_dofs, flux_func, solver, kinetic_mapper, error_fn, **kwargs)
        min_index = np.argmin(errors)
        best_c = conc_values[min_index]
        best_error = errors[min_index]

        if verbose:
            print(f"[Iteration {iteration}] Best c = {best_c:.4f}, Error = {best_error:.3e}")

        if best_error < tol:
            break
        
        conc_values = refine_concentration_range(conc_values, min_index)

    return best_c, best_error

def converge_concentration(solver,
                           kinetics_mapper, 
                           max_iter=250, tol=1e-3, mixing=0.05,
                           conc_old = None, verbose=True, return_converge_bool = False,
                           adapt = False,  save = False,
                           **kwargs):
    """
    Iteratively solve for surface concentrations coupling
    mass transport and kinetics until convergence.

    Parameters
    ----------
    solver : ElectrolyteSolver or ElectrolyteSolver1D
        The PDE solver object.
    kinetics_mapper : callable
        Function that takes concentration array and optional parameters, returns flux array.
    max_iter : int
        Maximum number of iterations.
    tol : float
        Relative tolerance for convergence.
    mixing : float
        Under-relaxation factor.
    verbose : bool
        Print progress.
    conc_old : bool
        This is the initial concentration.
    kwargs : dict
        Extra arguments like rho for 1D solver.

    Returns
    -------
    surface_conc : np.ndarray
        Converged surface concentrations.
    """

    surface_dofs = solver.dofs_dict[solver.active_inxs[0]][1]
    n_surface = len(surface_dofs)
    if conc_old is None:
        conc_old = np.full(n_surface, 1e-3, dtype=float)
    elif isinstance(conc_old, (float, int)):
        conc_old = np.full(n_surface, float(conc_old), dtype=float)
    elif isinstance(conc_old, np.ndarray):
        if conc_old.shape[0] != n_surface:
            raise ValueError(f"Expected {n_surface} entries in conc_old, got shape {conc_old.shape}")
        conc_old = conc_old.astype(float)
    else:
        raise TypeError(f"Invalid type for conc_old: {type(conc_old)}")

    error = np.inf
    converge_bool = False

    if save:
        return_array = np.zeros([max_iter, 2]) #conc, error
    for it in range(max_iter):
        # Evaluate flux from kinetics, pass extra params if needed
        rho_val = kwargs.pop("rho", None)  # remove rho from kwargs if it exists
        flux_active = kinetics_mapper(conc_old, **kwargs)        

        # Apply rho scaling only for 1D simulations
        if rho_val is not None and getattr(solver, "mesh_dim", None) == "1D":
            flux_active = rho_val * flux_active
            print('Going into RHO', rho_val)
        elif rho_val is not None and verbose:
            print("[Warning] rho was passed but solver is not 1D → ignoring rho.")
    
        flux_func = fem.Function(solver.V)
        flux_func.x.array[surface_dofs] = flux_active

        solver.solve(flux_func)
        solver.get_surface_conc()
        conc_new = solver.surface_concentrations

        error = calc_error_l2(conc_new, conc_old)
        if verbose:
            print(f"Iteration {it+1}: relative change = {error:.3e}")

        if error < tol:
            converge_bool = True
            if verbose:
                print("Convergence reached.")
            break

        if adapt is True and it > 5:
            mixing = 0.075

        conc_old = mixing * conc_new + (1 - mixing) * conc_old
#        print(conc_new, error)
        if save:
            return_array[it] = [conc_new[0], error]
        
    if error > tol and not converge_bool:
        converge_bool = False
        if verbose:
            print('Convergence was not REACHED, After the maximum no_iterations!')

    if save:
        return conc_new, return_array
    if return_converge_bool:
        return conc_new, converge_bool
    else:
        return conc_new


def run_full_convergence(
    solver: ElectrolyteSolver,
    kinetic_solver: KineticSolver,
    initial_concentration: float | np.ndarray| None = None,
    verbose: bool = False,
    mixing_1: float =0.05,
    mixing_2: float =0.05,
    max_iter_1: int=1,
    max_iter_2: int=250,
    max_iter_3: int=10,
    n_refit_points: int=25,
    return_converge_bool: bool = True,
    rho: float | None = None,
    tol: float=1e-5
) -> np.ndarray:
    """
    Full convergence workflow:
    1. Refit spline using CatMAP around initial guess.
    2. Run a short initial convergence to generate surface concentration.
    3. Refit spline using surface concentration.
    4. Run full convergence.
    5. Optional: Final refinement and short re-convergence.

    Parameters
    ----------
    solver : ElectrolyteSolver
        The FEM-based solver for the electrolyte domain.

    kinetic_solver : KineticSolver
        Contains the CatMAP-based kinetic logic and spline fitters.

    initial_concentration : float or np.ndarray
        Initial guess for the concentration.

    verbose : bool
        Whether to print convergence info.

    Returns
    -------
    np.ndarray
        Final surface concentration after convergence.
    """

    # Step 2: Short initial iteration to get surface concentrations
    surface_conc_1 = converge_concentration(
        solver,
        kinetic_solver.spline_bc,
        max_iter=max_iter_1,
        mixing=mixing_1,
        tol = tol,
        conc_old=initial_concentration,
        verbose=verbose,
        rho = rho
    )

    # Step 3: Refit spline using surface concentrations
    kinetic_solver.refit_from_surface_concentrations(surface_conc_1, n_new_points=n_refit_points)
#    print('after iteration 1', surface_conc_1)
    # Step 4: Full convergence
    surface_conc_2 = converge_concentration(
        solver,
        kinetic_solver.spline_bc,
        max_iter=max_iter_2,
        mixing=mixing_2,
        tol = tol,
        conc_old=initial_concentration,
        verbose=verbose,
        rho = rho
    )

    # Step 5: Final refit and short convergence
    kinetic_solver.refit_from_surface_concentrations(surface_conc_2, n_new_points=n_refit_points)
#    print('after iteration 2', surface_conc_2)
#    solver.solver_write = True # set the solver write to be True
    surface_conc_final = converge_concentration(
        solver,
        kinetic_solver.spline_bc,
        max_iter=max_iter_3,
        mixing=mixing_2,
        tol = tol, 
        conc_old=surface_conc_2,
        verbose=verbose,
        return_converge_bool = return_converge_bool,
        adapt = False,
        rho = rho
    )

    if return_converge_bool is True:
        return surface_conc_final[0], surface_conc_final[1]
    else:
        return surface_conc_final, None
