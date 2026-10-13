import numpy as np
import matplotlib.pyplot as plt

import ufl
from pathlib import Path
from mpi4py import MPI
from dolfinx import fem, mesh, default_scalar_type
from dolfinx.fem.petsc import NonlinearProblem, LinearProblem
from dolfinx.io import gmsh, XDMFFile
from basix.ufl import element
from petsc4py.PETSc import ScalarType
from petsc4py import PETSc

class ElectrolyteSolver:
    def __init__(self, mesh_dim: str = "1D",
                 coordinate_system: str = 'cartesian',
                 mesh_file: str = None,
                 active_tags: list = [1],
                 inactive_tags: list = [None],
                 dirichlet_tags: list = [2],
                 dirichlet_bcs: list = [0.0],
                 l_diff: float = 25e-6,
                 n_cells: int = 100,
                 solver_write: bool = False):
        """
        Electrolyte mass transport solver wrapper for 1D or 2D.
        """
        self.coordinate_system = coordinate_system.lower()
        self.active_inxs = active_tags
        self.inactive_inxs = inactive_tags
        self.dirichlet_inxs = dirichlet_tags
        self.dirichlet_bcs = dirichlet_bcs
        self.solver_write = solver_write
        self.mesh_dim = mesh_dim
        self.bcs = []
        
        if self.mesh_dim == "1D":
            self.mesh = mesh.create_interval(MPI.COMM_WORLD, n_cells, [0, l_diff])
            self.mesh.topology.create_connectivity(0, self.mesh.topology.dim) # for some reason we need this... not sure why            
            self.fdim = 0
            boundaries = [(active_tags[0], lambda x: np.isclose(x[0], 0, atol = l_diff/1000)),
                          (dirichlet_tags[0], lambda x: np.isclose(x[0], l_diff, atol = l_diff/1000))]
            facet_indices, facet_markers = [], []
            for marker, locator in boundaries:
                facets = mesh.locate_entities(self.mesh, self.fdim, locator)
                facet_indices.append(facets)
                facet_markers.append(np.full_like(facets, marker))
            self.ft = mesh.meshtags(self.mesh, self.fdim, np.concatenate(facet_indices), np.concatenate(facet_markers))

        elif self.mesh_dim == "2D":
            assert mesh_file is not None, "2D geometry requires a mesh file."
            mesh_io = gmsh.read_from_msh(mesh_file, MPI.COMM_WORLD, 0, gdim=2)
            self.mesh = mesh_io.mesh
            self.ft = mesh_io.facet_tags
            
#            self.mesh, _, self.ft = gmshio.read_from_msh(mesh_file, MPI.COMM_WORLD, 0, gdim=2)
            self.fdim = 1
        else:
            raise ValueError("Geometry must be either '1D' or '2D'.")

        P1 = element('P', self.mesh.basix_cell(), 1)        
        self.V = fem.functionspace(self.mesh, P1)
        self.c = ufl.TrialFunction(self.V)
        self.v = ufl.TestFunction(self.V)
        self.ds = ufl.Measure('ds', domain=self.mesh, subdomain_data=self.ft)
        self.map_ft_dofs()

    def _coord_weight(self):
        if self.coordinate_system == "cylindrical":
            x = ufl.SpatialCoordinate(self.mesh)
            return x[0]  # radial coordinate r
        elif self.coordinate_system == "cartesian":
            return 1.0
        else:
            raise ValueError(f"Unknown coordinate system: {self.coordinate_system}, only have cylindrical and cartesian.")

    def map_ft_dofs(self, plot=False):
        self.dofs_dict = {}
        self.coords = self.mesh.geometry.x
        inxs = self.active_inxs + self.inactive_inxs + self.dirichlet_inxs

        if plot:
            fig, ax = plt.subplots()

        for i in inxs:
            if i is None:
                continue
            dofs = fem.locate_dofs_topological(self.V, self.fdim, self.ft.find(i))
            coord_vals = self.coords[dofs]
            self.dofs_dict[i] = [coord_vals, dofs]

            if plot:
                ax.scatter(coord_vals[:, 0], coord_vals[:, 1] if coord_vals.shape[1] > 1 else 0, label=f"Tag {i}", s=10)

        if plot:
            ax.legend()
            fig.savefig('dofs.pdf')
            plt.close(fig)

    def visualize_geometry_dofs(self, save_as='dofs.pdf'):
        self.map_ft_dofs(plot=True)

    def create_dirchlet(self):
        for count, value in enumerate(self.dirichlet_bcs):
            tag = self.dirichlet_inxs[count]
            dofs = self.dofs_dict[tag][1]
            bc_value = ScalarType(value)
            self.bcs.append(fem.dirichletbc(bc_value, dofs, self.V))

    def update_L(self, g_inactive, g_active):
        weight = self._coord_weight()        
        self.L = 0
        for i in self.inactive_inxs:
            if i is None:
                continue
            self.L -= ufl.inner(g_inactive, self.v) * weight * self.ds(i)

        for i in self.active_inxs:
            self.L -= ufl.inner(g_active, self.v) * weight * self.ds(i)
        return self.L

    def solve(self, g_active, stable = True):
        weight = self._coord_weight()
        a = ufl.inner(ufl.grad(self.v), ufl.grad(self.c)) * weight * ufl.dx
        g_zero = fem.Constant(self.mesh, default_scalar_type(0.0))
        self.update_L(g_zero, g_active)
        if stable == True:  # this is a direct solver 
            problem = LinearProblem(a, self.L, bcs=self.bcs,
                                    petsc_options={"ksp_type": "preonly",
                                                   "pc_type": "lu"},
                                    petsc_options_prefix="Poisson")
        else: # from testing this solver is faster but also can lead to wierd solutions. 
            problem = LinearProblem(a, self.L, bcs=self.bcs,
                                    petsc_options = {"ksp_type": "cg", "ksp_rtol": 1e-12,
                                                     "ksp_atol": 1e-12, "ksp_max_it": 10000},
                                    petsc_options_prefix="Poisson")
        self.concs = problem.solve()
        if self.solver_write == True:
            cg_solver = problem.solver
            viewer = PETSc.Viewer().createASCII("cg_output.txt")
            cg_solver.view(viewer)
            solver_output = open("cg_output.txt", "r")
            for line in solver_output.readlines():
                print(line)

        self.concs.name = "concentration"
        
    def get_surface_conc(self):
        for i in self.active_inxs:
            self.surface_concentrations = self.concs.x.array[self.dofs_dict[i][1]]
            self.surface_coordinates = self.coords[self.dofs_dict[i][1]]

    def write_solution_to_file(self, filename="surface_conc.npy", full_field=False):
        np.save(filename, self.surface_concentrations)
        if full_field:
            np.save(filename.replace(".npy", "_full.npy"), self.concs.x.array)

    def postprocess_results(self, dof_plot="dofs.pdf", result_file="surface_conc.npy"):
        self.visualize_geometry_dofs(save_as=dof_plot)
        self.write_solution_to_file(filename=result_file, full_field=True)

    def get_selectivity(self, kinetic_mapper_inter, kinetic_mapper_prod,
                        get_flux=False, kinetic_mapper_bc=None):
        '''
        rate_int = \int r_mkm(c) dS_cat
        '''
        weight = self._coord_weight()
        rate_intermediate = fem.Function(self.V)
        rate_product = fem.Function(self.V)

        rate_intermediate.x.array[self.dofs_dict[self.active_inxs[0]][1]] = kinetic_mapper_inter(self.surface_concentrations)
        rate_product.x.array[self.dofs_dict[self.active_inxs[0]][1]] = kinetic_mapper_prod(self.surface_concentrations)

        rate_intermediate_total = 0
        rate_product_total = 0
        active_area = []
        for i in self.active_inxs:
            rate_intermediate_total += fem.assemble_scalar(fem.form(rate_intermediate * weight * self.ds(i)))
            rate_product_total += fem.assemble_scalar(fem.form(rate_product * weight * self.ds(i)))
            active_area.append(fem.assemble_scalar(fem.form(1 * self.ds(i))))
            
        sel = rate_intermediate_total/(rate_intermediate_total + rate_product_total)

        if get_flux is True:
            flux = fem.Function(self.V)
            if kinetic_mapper_bc is not None:
                flux.x.array[self.dofs_dict[self.active_inxs[0]][1]] = (-1 * kinetic_mapper_bc(self.surface_concentrations))/self.surface_concentrations
                flux_total = 0
                for i in self.active_inxs:
                    flux_total += fem.assemble_scalar(fem.form(flux * weight * self.ds(i)))
                return sel, flux_total
            else:
                print("Mapper_BC is None! Can't get the bc.")
        return sel

    def writeOutput(self, outdir_path_name, xdmf_file_name = 'concentrations.xdmf'):

        numpy_file_name = xdmf_file_name.replace('xdmf', 'npy')
        numpy_cord_file_name = numpy_file_name.replace('.npy', '_cords.npy')
        if not xdmf_file_name.endswith('.xdmf'):
            xdmf_file_name = xdmf_file_name + '.xdmf'

        outdir = Path(outdir_path_name)
        outdir.mkdir(exist_ok=True, parents=True)
        outfile = XDMFFile(self.mesh.comm, outdir / xdmf_file_name, "w")

        outfile.write_mesh(self.mesh)
        outfile.write_function(self.concs)

        cords = self.mesh.geometry.x
#        np.save(outdir / 'cords.npy', cords)
        np.save(outdir / numpy_cord_file_name, cords)        
        np.save(outdir / numpy_file_name, self.concs.x.array)
    
