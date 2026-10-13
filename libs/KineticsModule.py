import sys
sys.path.append('/home/hspillai/catmap_fhi/catmap-ec/')

from os import system as shell
from catmap import ReactionModel
from ase.units import _Nav
from ase.build import fcc100

from scipy.interpolate import CubicSpline
import numpy as np

class KineticSolver:
    def __init__(self, potential=None, catmap_mkm_path=None, Dab=None, K_henry=None):
        '''
        concs is an array of concentrations where we return the rate 
        '''
        self.potential = potential
        self.catmap_mkm_path = catmap_mkm_path 
        self.Dab = Dab
        self.K_henry = K_henry

        self._concentration_data = []
        self._intermediate_data = []
        self._product_data = []

        self.spline_bc = None
        self.spline_inter_flux = None
        self.spline_product_flux = None

    def load_data(self, path=None):
        """Load and filter precomputed CatMAP rate data."""
        if path is None:
            all_data = np.load(self.catmap_mkm_path)
        else:
            all_data = np.load(path)
        mask = np.isclose(all_data[:, 0], self.potential)

        if not np.any(mask):
            raise ValueError(f"No entries found at potential {self.potential} in {path}")

        filtered = all_data[mask]
        self._concentration_data = filtered[:, 1]
        self._intermediate_data = filtered[:, 2]
        self._product_data = filtered[:, 3] if filtered.shape[1] > 3 else None


    def fit_splines(self):
        """Fit splines from loaded data."""
        if len(self._concentration_data) == 0 or len(self._intermediate_data) == 0:
            raise ValueError("No data loaded for fitting. Run `load_data` or `add_rate_data` first.")

        # Remove values where there is no change in concentration
        id_non_zero = np.diff(self._concentration_data) != 0
        id_non_zero = np.append([True], [id_non_zero])
        
        self.spline_bc = CubicSpline(
            self._concentration_data[id_non_zero],
            -1 * np.array(self._intermediate_data[id_non_zero]) / self.Dab
        )

        self.spline_inter_flux = CubicSpline(
            self._concentration_data[id_non_zero],
            self._intermediate_data[id_non_zero]
        )

        if self._product_data is not None:
            self.spline_product_flux = CubicSpline(
                self._concentration_data[id_non_zero],
                self._product_data[id_non_zero]
            )

    def add_rate_data(self, concentrations, intermediate_fluxes,
                      product_fluxes=None):
        """Add new datapoints to fit, then refit splines."""
        self._concentration_data = np.concatenate([self._concentration_data, concentrations])
        self._intermediate_data = np.concatenate([self._intermediate_data, intermediate_fluxes])

        if product_fluxes is not None:
            if self._product_data is None:
                self._product_data = product_fluxes
            else:
                self._product_data = np.concatenate([self._product_data, product_fluxes])

        # Sort all by concentration
        sort_idx = np.argsort(self._concentration_data)

        self._concentration_data = self._concentration_data[sort_idx]
        self._intermediate_data = self._intermediate_data[sort_idx]

        # Remove values where there is no change in concentration
        id_non_zero = np.diff(self._concentration_data[sort_idx]) != 0
        id_non_zero = np.append([True], [id_non_zero])

        self._concentration_data = self._concentration_data[id_non_zero]
        self._intermediate_data = self._intermediate_data[id_non_zero]
        
        if self._product_data is not None:
            self._product_data = self._product_data[sort_idx]
            self._product_data = self._product_data[id_non_zero]            

        self.fit_splines()

    # def run_mkm_roughness(self, cs: list, rho = 1.0):
    #     intermediate_fluxs, product_fluxs = self.run_mkm(cs)
    #     return intermediate_fluxs * rho * -1 * 1/self.Dab

    def run_mkm_intermediate_flux(self, conc_array: np.ndarray) -> np.ndarray:
        inter_flux, _ = self._run_mkm_raw(conc_array)
        return inter_flux

    def run_mkm_product_flux(self, conc_array: np.ndarray) -> np.ndarray:
        _, prod_flux = self._run_mkm_raw(conc_array)
        return prod_flux
    
    def run_mkm_roughness(self, conc_array: np.ndarray, rho=1.0) -> np.ndarray:
        inter_flux, _ = self._run_mkm_raw(conc_array)
        return inter_flux * rho * -1 / self.Dab

    def run_mkm_roughness_intermediate(self, conc_array: np.ndarray, rho=1.0) -> np.ndarray:
        inter_flux, _ = self._run_mkm_raw(conc_array)
        return inter_flux

    def run_mkm_roughness_product(self, conc_array: np.ndarray, rho=1.0) -> np.ndarray:
        inter_flux, product_flux = self._run_mkm_raw(conc_array)
        return product_flux

    def _run_mkm_raw(self, cs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        if (
            hasattr(self, "_last_conc") and
            self._last_conc is not None and
            len(self._last_conc) == len(cs) and
            np.allclose(self._last_conc, cs)
        ):
            return self._last_inter_flux, self._last_prod_flux
    
        inter_flux_list = []
        product_flux_list = []

        for c in cs:
            a = c/self.K_henry
            mkm_file_name = self.modify(self.potential, a)
            model = ReactionModel(setup_file=mkm_file_name,
                                  max_log_line_length=0)
            model.output_variables += ['rate', 'production_rate']
            model.run()

            d1, rates = model.rate_map[0]
            u, T = d1
            inter_flux = max(self.rateToJ(rates[3]), 0)
            product_flux = self.rateToJ(rates[5])
            inter_flux_list.append(inter_flux)
            product_flux_list.append(product_flux)

        inter_flux_arr = np.array(inter_flux_list).flatten()
        prod_flux_arr = np.array(product_flux_list).flatten()

        self._last_conc = np.copy(cs)
        self._last_inter_flux = inter_flux_arr
        self._last_prod_flux = prod_flux_arr
        return inter_flux_arr, prod_flux_arr        

    def refit_from_catmap(self, conc_ranges):
        """
        Evaluates new CatMAP flux data at given concentrations and refits splines.
        
        Parameters
        ----------
        conc_ranges : array-like
        Concentrations (in mol/m³) at which to run CatMAP and refit the spline models.
        """
        conc_ranges = np.asarray(conc_ranges, dtype=float)
        catmap_intermediate, catmap_product = self._run_mkm_raw(conc_ranges)
        self.add_rate_data(conc_ranges, catmap_intermediate, catmap_product)
        self.fit_splines()

    def modify(self, U, a):
        mkm_file_name = 'catmap_{}.mkm'.format(U)
        shell("sed -e 's/UVAL/{}/g' -e 's/ACTIVITY/{}/g' catmap_template.mkm > {}".format(U, a, mkm_file_name))
        return mkm_file_name

    def rateToJ(self, rate):
        atoms = fcc100('Cu', a=3.6149, size=(1, 1, 5),
                       vacuum=10.0, orthogonal=True)
        site_density = atoms.get_volume()/atoms.cell[2, 2]  # A^2
        site_density *= (1e-10)**2  # m^2/site
        # convert rate to flux
        J = rate * (1/_Nav) * (1/site_density)  # mole/(m^2 s)
        return J

    def refit_from_surface_concentrations(self, surface_conc, n_new_points=50,
                                          threshold=None):
        """
        Refit the spline using new surface concentration values by selectively
        evaluating CatMAP
        on the most distant concentrations from existing spline data.

        Parameters
        ----------
        surface_conc : array-like
        Array of new surface concentrations from a simulation step.
        n_new_points : int
        Max number of nextw concentration points to evaluate with CatMAP.
        threshold : float, optional
        Only include surface concentrations whose distance from known points
        exceeds this value.
        If None, select the n most distant points unconditionally.
        """
        surface_conc = np.array(surface_conc)
        known_conc = np.array(self._concentration_data)

        # Compute min abs distance to known concentration values
        dists = np.min(np.abs(surface_conc[:, None] - known_conc[None, :]),
                       axis=1)

        # Optionally apply a threshold to filter points
        if threshold is not None:
            mask = dists > threshold
            surface_conc = surface_conc[mask]
            dists = dists[mask]

        # If no points pass threshold, return early
        if len(surface_conc) == 0:
            print("No new concentrations passed the threshold. Spline not updated.")
            return

        # Select indices of top-N furthest values
        idx = np.argsort(-dists)[:n_new_points]
        new_concs = surface_conc[idx]

        print(f"Refitting spline with {len(new_concs)} new CatMAP points...")

        # Run CatMAP on selected concentrations
        new_intermediate_flux, new_product_flux = self._run_mkm_raw(new_concs)

        # Add to training set
        self.add_rate_data(new_concs, new_intermediate_flux, new_product_flux)

        # Refit the spline
        self.fit_splines()
