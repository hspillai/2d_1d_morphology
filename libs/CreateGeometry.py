import matplotlib.pyplot as plt
from scipy.integrate import quad
import numpy as np
import gmsh

import copy

import matplotlib.pyplot as plt
from scipy.integrate import quad
import numpy as np
import gmsh

import copy

class Hemisphere_complete_realL(object):
    '''
    Geometery code for a complete tunnel
    '''
    def __init__(self, length_box, radius,
                 ms_lw, ref= False, small_size = False):

        self.l_prime = length_box + radius        
        self.radius = radius

        self.lc = ms_lw
        self.refinement = ref

        if small_size == True:
            gmsh.option.setNumber("Geometry.Tolerance", 1-10)
        
        gmsh.initialize()
        gmsh.model.add('tunnel')


    def CreateGeometry(self):
        # p3>_________
        #   |         \   
        #   |          \  
        #   |           \ 
        #p4  --          \<-- c1  
        #      \<-c2      \
        #       \          \
        #        \----------
        #        ^p1      ^p2

        print('Creating Geometry!!')
        factory = gmsh.model.geo

        p1 = factory.addPoint(self.radius, 0, 0,
                              self.lc, 1)
        p2 = factory.addPoint(self.l_prime, 0, 0,
                              self.lc, 2)
        p3 = factory.addPoint(0, self.l_prime, 0,
                              self.lc, 3)
        p4 = factory.addPoint(0, self.radius, 0,
                              self.lc, 4)
        origin = factory.addPoint(0, 0,
                                  0, self.lc, 6)

        l1 = factory.addLine(p1, p2) 
        l2 = factory.addLine(p3, p4) # right wall

        c1 = factory.addCircleArc(p2, origin, p3) # semicircle
        c2 = factory.addCircleArc(p4, origin, p1) # semicircle        

        factory.addCurveLoop([l1, c1, l2, c2], 1) #[l1, l2, -c2, l4, c1], 1)
        factory.addPlaneSurface([1], 1)

        factory.synchronize()

        gmsh.model.addPhysicalGroup(1, [l1], name = 'inactive_area')
        gmsh.model.addPhysicalGroup(1, [c2], name = 'active_area')
        gmsh.model.addPhysicalGroup(1, [l2], name = 'side_boundary')
        gmsh.model.addPhysicalGroup(1, [c1], name = 'top_boundary')
        gmsh.model.addPhysicalGroup(2, [1], name = 'full_surface')

        if self.refinement == True:
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [c2]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 
    
            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", self.lc)
            
            gmsh.model.mesh.field.setNumber(3, "DistMin", 0.1 * self.radius)
            gmsh.model.mesh.field.setNumber(3, "DistMax", 0.2 * self.radius)
            
            gmsh.model.mesh.field.add("Min", 6)            
            gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3])            
            gmsh.model.mesh.field.setAsBackgroundMesh(6)
    
            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)
    
        gmsh.model.mesh.generate(2)
        self.model = gmsh.model
    def visualize(self):
        gmsh.fltk.run()
    def save(self,
             save_path = './',      
             mesh_name = 'default.msh'):
        if not save_path.endswith('/'):
            save_path += '/'
        
        if not mesh_name.endswith('.msh'):
            mesh_name += '.msh'
        gmsh.write(save_path + mesh_name)
        

class Hemisphere_complete(object):
    '''
    Geometery code for a complete tunnel
    '''
    def __init__(self, length_box, radius,
                 ms_lw, ref= False):
        
        self.l = length_box
        self.radius = radius

        self.lc = ms_lw
        self.refinement = ref

        gmsh.initialize()
        gmsh.model.add('tunnel')

    def CreateGeometry(self):
        # p3>_________
        #   |         \   
        #   |          \  
        #   |           \ 
        #p4  --          \<-- c1  
        #      \<-c2      \
        #       \          \
        #        \----------
        #        ^p1      ^p2

        print('Creating Geometry!!')
        factory = gmsh.model.geo

        p1 = factory.addPoint(self.radius, 0, 0,
                              self.lc, 1)
        p2 = factory.addPoint(self.l, 0, 0,
                              self.lc, 2)
        p3 = factory.addPoint(0, self.l, 0,
                              self.lc, 3)
        p4 = factory.addPoint(0, self.radius, 0,
                              self.lc, 4)
        origin = factory.addPoint(0, 0,
                                  0, self.lc, 6)

        l1 = factory.addLine(p1, p2) 
        l2 = factory.addLine(p3, p4) # right wall

        c1 = factory.addCircleArc(p2, origin, p3) # semicircle
        c2 = factory.addCircleArc(p4, origin, p1) # semicircle        

        factory.addCurveLoop([l1, c1, l2, c2], 1) #[l1, l2, -c2, l4, c1], 1)
        factory.addPlaneSurface([1], 1)

        factory.synchronize()

        gmsh.model.addPhysicalGroup(1, [l1], name = 'inactive_area')
        gmsh.model.addPhysicalGroup(1, [c2], name = 'active_area')
        gmsh.model.addPhysicalGroup(1, [l2], name = 'side_boundary')
        gmsh.model.addPhysicalGroup(1, [c1], name = 'top_boundary')
        gmsh.model.addPhysicalGroup(2, [1], name = 'full_surface')

        if self.refinement == True:
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [c2]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 
    
            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", self.lc)
            
            gmsh.model.mesh.field.setNumber(3, "DistMin", 0.1 * self.radius)
            gmsh.model.mesh.field.setNumber(3, "DistMax", 0.2 * self.radius)
            
            gmsh.model.mesh.field.add("Min", 6)            
            gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3])            
            gmsh.model.mesh.field.setAsBackgroundMesh(6)
    
            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)
    
        gmsh.model.mesh.generate(2)
        self.model = gmsh.model
    def visualize(self):
        gmsh.fltk.run()
    def save(self,
             save_path = './',      
             mesh_name = 'default.msh'):
        if not save_path.endswith('/'):
            save_path += '/'
        
        if not mesh_name.endswith('.msh'):
            mesh_name += '.msh'
        gmsh.write(save_path + mesh_name)
        
        
class Hemisphere_curved_cylinder(object):
    def __init__(self, width_box, length_box, radius,
                 ms_lw, ref= False, small_size = False):
        
        self.w = width_box
        self.l = length_box
        if (self.l**2 - self.w**2) < 0:
            print(f'This geometry is not possible since R {self.w} is larger than the diffusion length {self.l}!')
            self.l_side = False
        else:
            self.l_side = np.sqrt(self.l**2 - self.w**2)
        self.radius = radius

        self.lc = ms_lw
        self.refinement = ref

        gmsh.initialize()
        gmsh.model.add('tunnel')

        if small_size == True:
            gmsh.option.setNumber("Geometry.Tolerance", 1-10)
        
    def CreateGeometry(self):
        # p4>_________
        #   |         \   
        #   |          \  
        #   |           \ 
        #p5> --          \  <p3 (between p4 and p3 its a arc c2
        #      \          |
        #       \         |
        #        \---------
        #        ^p1      ^p2

        if self.l_side is False:
            print('CreateGeometry not possible!')
            return None
#            exit()

        print('Creating Geometry!!')
        factory = gmsh.model.geo

        p1 = factory.addPoint(self.radius, 0, 0,
                              self.lc, 1)
        p2 = factory.addPoint(self.w, 0, 0,
                              self.lc, 2)
        p3 = factory.addPoint(self.w, self.l_side, 0,
                              self.lc, 3)
        p4 = factory.addPoint(0, self.l, 0,
                              self.lc, 4)
        p5 = factory.addPoint(0, self.radius,
                              0, self.lc, 5)
        origin = factory.addPoint(0, 0,
                                  0, self.lc, 6)

        l1 = factory.addLine(1, 2) # right side of hemisphere
        l2 = factory.addLine(2, 3) # right wall
        l4 = factory.addLine(4, 5) # left wall

        c1 = factory.addCircleArc(p5, origin, p1) # semicircle
        c2 = factory.addCircleArc(p4, origin, p3) # semicircle

        factory.addCurveLoop([l1, l2, -c2, l4, c1], 1)
        
        factory.addPlaneSurface([1], 1)

        factory.synchronize()

        gmsh.model.addPhysicalGroup(1, [l1], name = 'inactive_area')
        gmsh.model.addPhysicalGroup(1, [c1], name = 'active_area')
        gmsh.model.addPhysicalGroup(1, [l2, l4], name = 'side_boundary')
        gmsh.model.addPhysicalGroup(1, [c2], name = 'top_boundary')
        gmsh.model.addPhysicalGroup(2, [1], name = 'full_surface')

        if self.refinement == True:
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [c1]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 
    
            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", self.lc)
            
            gmsh.model.mesh.field.setNumber(3, "DistMin", 0.1 * self.radius)
            gmsh.model.mesh.field.setNumber(3, "DistMax", 0.2 * self.radius)
            
            gmsh.model.mesh.field.add("Min", 6)            
            gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3])            
            gmsh.model.mesh.field.setAsBackgroundMesh(6)
    
            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)
    
        gmsh.model.mesh.generate(2)
        self.model = gmsh.model

    def visualize(self):
        gmsh.fltk.run()

    def save(self,
             save_path = './',      
             mesh_name = 'default.msh'):
        if not save_path.endswith('/'):
            save_path += '/'
        
        if not mesh_name.endswith('.msh'):
            mesh_name += '.msh'
        gmsh.write(save_path + mesh_name)

class Hemisphere_curved_cylinder_realL(object):
    def __init__(self, width_box, length_box, radius,
                 ms_lw, ref= False, small_size = False):
        
        self.w = width_box
        self.l = length_box        
        self.radius = radius
        self.l_prime = length_box + radius
        self.lc = ms_lw
        self.refinement = ref
        self.small_size = small_size
        
        if (self.l_prime**2 - self.w**2) < 0:
            print(f'This geometry is not possible since R {self.w} is larger than the diffusion length {self.l}!')
            self.l_side = False
        else:
            self.l_side = np.sqrt(self.l_prime**2 - self.w**2)
            
        gmsh.initialize()
        gmsh.model.add('tunnel')
        
        if self.small_size == True:
            print('reducing the tolerance!')
            gmsh.option.setNumber("Geometry.Tolerance", 1-10)
    
    def CreateGeometry(self):
        #    _  p4>_________
        #   |     |         \   
        # L |     |          \  
        #   |_    |           \ 
        #      p5> --          \  <p3 (between p4 and p3 its a arc c2
        #            \          |
        #             \         |
        #              \---------
        #        ^p1      ^p2

        if self.l_side is False:
            print('CreateGeometry not possible!')
            return None
#            exit()

        print('Creating Geometry!!')
        factory = gmsh.model.geo

        p1 = factory.addPoint(self.radius, 0, 0,
                              self.lc, 1)
        p2 = factory.addPoint(self.w, 0, 0,
                              self.lc, 2)
        p3 = factory.addPoint(self.w, self.l_side, 0,
                              self.lc, 3)
        p4 = factory.addPoint(0, self.l_prime, 0,
                              self.lc, 4)
        p5 = factory.addPoint(0, self.radius,
                              0, self.lc, 5)
        origin = factory.addPoint(0, 0,
                                  0, self.lc, 6)

        l1 = factory.addLine(1, 2) # right side of hemisphere
        l2 = factory.addLine(2, 3) # right wall
        l4 = factory.addLine(4, 5) # left wall

        c1 = factory.addCircleArc(p5, origin, p1) # semicircle
        c2 = factory.addCircleArc(p4, origin, p3) # semicircle

        factory.addCurveLoop([l1, l2, -c2, l4, c1], 1)
        
        factory.addPlaneSurface([1], 1)

        factory.synchronize()

        gmsh.model.addPhysicalGroup(1, [l1], name = 'inactive_area')
        gmsh.model.addPhysicalGroup(1, [c1], name = 'active_area')
        gmsh.model.addPhysicalGroup(1, [l2, l4], name = 'side_boundary')
        gmsh.model.addPhysicalGroup(1, [c2], name = 'top_boundary')
        gmsh.model.addPhysicalGroup(2, [1], name = 'full_surface')

        if self.refinement == True and self.small_size == True:
            print('Doing the refinement for the small.')
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [c1, l1]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 
            
            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 3500)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", self.lc)

            gmsh.model.mesh.field.setNumber(3, "DistMin", self.l * 1e-5)
            gmsh.model.mesh.field.setNumber(3, "DistMax", self.l * 50 * 1e-5)
            # gmsh.model.mesh.field.setNumber(3, "DistMin", 0.001 * self.l)
            # gmsh.model.mesh.field.setNumber(3, "DistMax", 0.005 * self.l)
            
            gmsh.model.mesh.field.add("Min", 6)            
            gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3])            
            gmsh.model.mesh.field.setAsBackgroundMesh(6)
            
            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)

        if self.refinement == True and self.small_size == False:
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [c1]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 
    
            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", self.lc)
            
            gmsh.model.mesh.field.setNumber(3, "DistMin", 0.1 * self.radius)
            gmsh.model.mesh.field.setNumber(3, "DistMax", 0.2 * self.radius)
            
            gmsh.model.mesh.field.add("Min", 6)            
            gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3])            
            gmsh.model.mesh.field.setAsBackgroundMesh(6)
    
            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)
    
        gmsh.model.mesh.generate(2)
        self.model = gmsh.model

    def visualize(self):
        gmsh.fltk.run()

    def save(self,
             save_path = './',      
             mesh_name = 'default.msh'):
        if not save_path.endswith('/'):
            save_path += '/'
        
        if not mesh_name.endswith('.msh'):
            mesh_name += '.msh'
        gmsh.write(save_path + mesh_name)

        
class Hemisphere_curved_cylinder_v2(object):
    def __init__(self, width_box, length_box, radius,
                 ms_lw, ref= False):
        
        self.w = width_box
        self.l = length_box
        self.l_side = np.sqrt(self.l**2 - self.w**2)
        self.radius = radius

        self.lc = ms_lw
        self.refinement = ref

        gmsh.initialize()
        gmsh.model.add('tunnel')
    
    def CreateGeometry(self):
        # p4>_________
        #   |         \   
        #   |          \  
        #   |           \ 
        #p5> --          \  <p3 (between p4 and p3 its a arc c2
        #      \          |
        #       \         |
        #        \---------
        #        ^p1      ^p2
        

        factory = gmsh.model.geo

        p1 = factory.addPoint(self.radius, 0, 0,
                              self.lc, 1)
        p2 = factory.addPoint(self.w, 0, 0,
                              self.lc, 2)
        p3 = factory.addPoint(self.w, self.l_side, 0,
                              self.lc, 3)
        p4 = factory.addPoint(0, self.l, 0,
                              self.lc, 4)
        p5 = factory.addPoint(0, self.radius,
                              0, self.lc, 5)
        origin = factory.addPoint(0, 0,
                                  0, self.lc, 6)

        l1 = factory.addLine(1, 2) # right side of hemisphere
        l2 = factory.addLine(2, 3) # right wall
        l4 = factory.addLine(4, 5) # left wall
        
        c1 = factory.addCircleArc(p5, origin, p1) # semicircle
        c2 = factory.addCircleArc(p4, origin, p3) # semicircle

        factory.addCurveLoop([l1, l2, -c2, l4, c1], 1)
        
        factory.addPlaneSurface([1], 1)

        factory.synchronize()

        gmsh.model.addPhysicalGroup(1, [l1], name = 'inactive_area')
        gmsh.model.addPhysicalGroup(1, [c1], name = 'active_area')
        gmsh.model.addPhysicalGroup(1, [l2, l4], name = 'side_boundary')
        gmsh.model.addPhysicalGroup(1, [c2], name = 'top_boundary')
        gmsh.model.addPhysicalGroup(2, [1], name = 'full_surface')

        if self.refinement == True:
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [p5, c1, p1]) # as we get closer to the bottom surface also import to near p1
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 
    
            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", self.lc)
            
            gmsh.model.mesh.field.setNumber(3, "DistMin", 0.1 * self.radius)
            gmsh.model.mesh.field.setNumber(3, "DistMax", 0.2 * self.radius)
            
            gmsh.model.mesh.field.add("Min", 6)            
            gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3])            
            gmsh.model.mesh.field.setAsBackgroundMesh(6)
    
            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)
    
        gmsh.model.mesh.generate(2)
        self.model = gmsh.model

    def visualize(self):
        gmsh.fltk.run()

    def save(self,
             save_path = './',      
             mesh_name = 'default.msh'):                                                                                                    
        if not mesh_name.endswith('.msh'):
            mesh_name += '.msh'
        gmsh.write(save_path + mesh_name)

class CompleteTunnel(object):
    '''
    create a geometry for an inhomgenous strip
    '''

    def __init__(self, length_box, radius,
                 ms_lw, ref= False):


        self.w = 2 * length_box
        self.l = length_box
        self.radius = radius

        self.lc = ms_lw
        self.refinement = ref

        gmsh.initialize()
        gmsh.model.add('tunnel')

        
    def CreateGeometry(self):
#
#          -------------------------------
#         /                               \
#        /             _____               \
#       /            /       \              \ 
#      /            /         \              \
#      p1----------p2          p3------------p4
#        ^l1             ^c1         ^l2

        factory = gmsh.model.geo

        p1 = factory.addPoint(0, 0, 0, self.lc, 1) 
        p2 = factory.addPoint((self.w * 0.5) - self.radius ,
                              0, 0, self.lc, 2)
        p3 = factory.addPoint((self.w * 0.5) + self.radius ,
                              0, 0, self.lc, 3)
        p4 = factory.addPoint(self.w * 0.5,
                              0, 0, self.lc, 4)
        p5 = factory.addPoint(self.w,
                              0, 0, self.lc, 5)

        l1 = factory.addLine(1, 2) # left half up to semi circle
        l2 = factory.addLine(3, 5) # right half from semi circle to box edge
        c1 = factory.addCircleArc(p3, p4, p2) # small semicircle
        c2 = factory.addCircleArc(p5, p4, p1) # large semicircle
        
        factory.addCurveLoop([l1, -c1, l2,
                              c2], 1)
        
        factory.addPlaneSurface([1], 1)
        factory.synchronize()

        gmsh.model.addPhysicalGroup(1, [l1], name = 'inactive_area_1') 
        gmsh.model.addPhysicalGroup(1, [c1], name = 'active_area_1')                                                                                                                                       
        gmsh.model.addPhysicalGroup(1, [l2], name = 'inactive_area_2')                                                                                                                                              
        gmsh.model.addPhysicalGroup(1, [c2], name = 'top_boundary')                                                                                                                                                 
        gmsh.model.addPhysicalGroup(2, [1], name = 'full_surface')                
        
        if self.refinement == True:
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [c1]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 
            

            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", self.lc)
            gmsh.model.mesh.field.setNumber(3, "DistMin", self.l * 0.01)            
            gmsh.model.mesh.field.setNumber(3, "DistMax", self.l * 0.75) # 

            gmsh.model.mesh.field.add("Min", 6)            
            gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3])            
            gmsh.model.mesh.field.setAsBackgroundMesh(6)

            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)

        gmsh.model.mesh.generate(2)
        self.model = gmsh.model
        
    def visualize(self):
        gmsh.fltk.run()

    def save(self,
             save_path = './',                                                                                                                     
             mesh_name = 'default.msh'):                                                                                                    
        if not mesh_name.endswith('.msh'):
            mesh_name += '.msh'
        gmsh.write(save_path + mesh_name)

class HemisphereCylindericalCords(object):
    '''
    create a hemisphere when realized in cylinderical coords
    '''
    
    def __init__(self, width, length, radius,
                 ms_lw, ref= False):


        self.w = width
        self.l = length
        self.radius = radius
        self.lc = ms_lw
        self.refinement = ref

        gmsh.initialize()
        gmsh.model.add('hemi')

    def CreateGeometry(self):

        # p4>_____________ < p3
        #   |             |
        #   |             |
        #   |             |
        #p5> --           |
        #      \          |
        #       \         |
        #        \---------
        #        ^p1      ^p2

        factory = gmsh.model.geo

        p1 = factory.addPoint(self.radius, 0, 0, self.lc, 1)
        p2 = factory.addPoint(self.w, 0, 0, self.lc, 2)
        p3 = factory.addPoint(self.w, self.l, 0, self.lc, 3)
        p4 = factory.addPoint(0, self.l, 0, self.lc, 4)
        p5 = factory.addPoint(0, self.radius,
                              0, self.lc, 5)
        origin = factory.addPoint(0, 0,
                                  0, self.lc, 6)


        l1 = factory.addLine(1, 2) # right side of hemisphere
        l2 = factory.addLine(2, 3) # right wall
        l3 = factory.addLine(3, 4) # top wall
        l4 = factory.addLine(4, 5) # left wall
        
        c1 = factory.addCircleArc(p5, origin, p1) # semicircle

        factory.addCurveLoop([l1, l2, l3, l4, c1], 1)
        
        factory.addPlaneSurface([1], 1)
        
        factory.synchronize()

        gmsh.model.addPhysicalGroup(1, [l1], name = 'inactive_area')
        gmsh.model.addPhysicalGroup(1, [c1], name = 'active_area')
        gmsh.model.addPhysicalGroup(1, [l2, l4], name = 'side_boundary')
        gmsh.model.addPhysicalGroup(1, [l3], name = 'top_boundary')
        gmsh.model.addPhysicalGroup(2, [1], name = 'full_surface')

        if self.refinement == True:
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [c1, l1]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 
            
            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", self.lc)
            
            gmsh.model.mesh.field.setNumber(3, "DistMin", 0.1 * self.radius)
            gmsh.model.mesh.field.setNumber(3, "DistMax", 0.2 * self.radius)
            
            gmsh.model.mesh.field.add("Min", 6)            
            gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3])            
            gmsh.model.mesh.field.setAsBackgroundMesh(6)
            
            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)
    
        gmsh.model.mesh.generate(2)
        self.model = gmsh.model

    def visualize(self):
        gmsh.fltk.run()

    def save(self, save_path = './',
             mesh_name = 'default.msh'):
        
        print(save_path)
        if not mesh_name.endswith('.msh'):
            mesh_name += '.msh'
        gmsh.write(save_path + mesh_name)


class RectangleActiveSite(object):
    '''
    create a rectangular geometry
    '''
    
    def __init__(self, width_box, diffusion_length, square_len,
                 ms_lw, ref= False):


        self.w = width_box
        self.l_diff = diffusion_length
        self.l_box = square_len
        self.lc = ms_lw
        self.refinement = ref

        gmsh.initialize()
        gmsh.model.add('rect')

    def CreateGeometry(self):


        #	P8___________________p7
        #	 |     l7^	     |
        #	 |		     | 
        #    l8> |	 p3___p4     |
        #	 |	 |l3^ |	     | <l6
        #	 |   l2> |    |<l4   |
        #	 p1______p2   p5_____p6
        #	    ^l1		 ^l5

        factory = gmsh.model.geo
        
        p1 = factory.addPoint(0, 0, 0, self.lc, 1)
        
        p2 = factory.addPoint((self.w * 0.5) - (0.5 * self.l_box),
                              0, 0, self.lc, 2)
        
        p3 = factory.addPoint((self.w * 0.5) - (0.5 * self.l_box),
                              self.l_box, 0, self.lc, 3)
        
        p4 = factory.addPoint((self.w * 0.5) + (0.5 * self.l_box),
                             self.l_box, 0, self.lc, 4)

        p5 = factory.addPoint((self.w * 0.5) + (0.5 * self.l_box),
                             0, 0, self.lc, 5)

        p6 = factory.addPoint(self.w,
                              0, 0, self.lc, 6)
        
        p7 = factory.addPoint(self.w,
                              self.l_diff, 0, self.lc, 7)
        p8 = factory.addPoint(0,
                              self.l_diff, 0, self.lc, 8)

        l1 = factory.addLine(1, 2)
        l2 = factory.addLine(2, 3)
        l3 = factory.addLine(3, 4)
        l4 = factory.addLine(4, 5)
        l5 = factory.addLine(5, 6)
        l6 = factory.addLine(6, 7)
        l7 = factory.addLine(7, 8)
        l8 = factory.addLine(8, 1)

        factory.addCurveLoop([l1, l2, l3, l4, l5,
                              l6, l7, l8], 1)
        factory.addPlaneSurface([1], 1)
        
        factory.synchronize()
        x_translation = [1, 0, 0, 1,
                         0, 1, 0, 0,
                         0, 0, 1, 0,
                         0, 0, 0, 1]

        gmsh.model.mesh.setPeriodic(1, [l8], [l6], x_translation)  # mesh on line 2 (right) should match line 4 (left) via translation
        gmsh.model.addPhysicalGroup(1, [l1], name = 'inactive_area_1')
        gmsh.model.addPhysicalGroup(1, [l2, l3, l4], name = 'active_area_1')
        gmsh.model.addPhysicalGroup(1, [l5], name = 'inactive_area_2')
        gmsh.model.addPhysicalGroup(1, [l7], name = 'top_boundary')
        gmsh.model.addPhysicalGroup(1, [l6, l8], name = 'side_boundary')
        gmsh.model.addPhysicalGroup(2, [1], name = 'full_surface')

        if self.refinement == True:
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [l2, l3, l4,
                                                               p3, p4]) # as we get closer to the bottom surface
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 

            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", self.lc)

            gmsh.model.mesh.field.setNumber(3, "DistMin", 0.1 * self.l_box)
            gmsh.model.mesh.field.setNumber(3, "DistMax", 0.15 * self.l_box)
            gmsh.model.mesh.field.setAsBackgroundMesh(3)

            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)
    
        gmsh.model.mesh.generate(2)
        self.model = gmsh.model

    def visualize(self):
        gmsh.fltk.run()

    def save(self, save_path = './',
             mesh_name = 'default.msh'):
        
        print(save_path)
        if not mesh_name.endswith('.msh'):
            mesh_name += '.msh'
        gmsh.write(save_path + mesh_name)

class HemiSphere_v3(object):
    '''
    create a geometry for a hemicircle where the boundary layer changes with the diffusion length.
    '''

    def __init__(self, width_box, length_box, radius,
                 ms_lw, ref= False):


        self.w = width_box
        self.l_diff = length_box
        self.radius = radius
        self.lc = ms_lw
        self.l_side = np.sqrt(self.l_diff**2 - (self.w**2/4))
        self.refinement = ref

        gmsh.initialize()
        gmsh.model.add('hemi')
        
    def CreateGeometry(self):
#
#          -------------------------------
#         /                               \
#        /                                 \
#      p10           _______                p9 <- l5  
# l5-> |            /       \               | <- l3
#      |           /         \              |
#      p1-----------          --------------p8 <- l3 
#        ^l1             ^c1         ^l2

        factory = gmsh.model.geo

        p1 = factory.addPoint(0, 0, 0, self.lc, 1)
        p2 = factory.addPoint((self.w * 0.5) - self.radius ,
                              0, 0, self.lc, 2)
        p3 = factory.addPoint((self.w * 0.5) + self.radius ,
                              0, 0, self.lc, 3)
        p4 = factory.addPoint(self.w,
                              0, 0, self.lc, 4)        
        p5 = factory.addPoint(self.w,
                              self.l_side, 0, self.lc, 5)
        p6 = factory.addPoint(0,
                              self.l_side, 0, self.lc, 6)

        p7 = factory.addPoint(self.w * 0.5,
                              0, 0, self.lc, 7)

        l1 = factory.addLine(1, 2) # left half up to semi circle
        l2 = factory.addLine(3, 4) # right half from semi circle to box edge
        l3 = factory.addLine(4, 5) # right side 
        l5 = factory.addLine(6, 1) # left side 

        c1 = factory.addCircleArc(p3, p7, p2) # semicircle
        c2 = factory.addCircleArc(p5, p7, p6) # semicircle
        
        factory.addCurveLoop([l1, -c1, l2,
                              l3, c2, l5], 1)
        
        factory.addPlaneSurface([1], 1)
        
        factory.synchronize()

        x_translation = [1, 0, 0, 1,
                         0, 1, 0, 0,
                         0, 0, 1, 0,
                         0, 0, 0, 1]

        gmsh.model.mesh.setPeriodic(1, [l5], [l3], x_translation)  # mesh on line 2 (right) should match line 4 (left) via translation
        
        gmsh.model.addPhysicalGroup(1, [l1], name = 'inactive_area_1')
        gmsh.model.addPhysicalGroup(1, [c1], name = 'active_area_1')
        gmsh.model.addPhysicalGroup(1, [l2], name = 'inactive_area_2')
        gmsh.model.addPhysicalGroup(1, [c2], name = 'top_boundary')
        gmsh.model.addPhysicalGroup(1, [l5, l3], name = 'side_boundary')
        gmsh.model.addPhysicalGroup(2, [1], name = 'full_surface')

        if self.refinement == True:
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [c1]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 

            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", self.lc)

            gmsh.model.mesh.field.setNumber(3, "DistMin", self.l_side * 0.01)            
            gmsh.model.mesh.field.setNumber(3, "DistMax", self.l_side * 0.75) # 0.1 


            gmsh.model.mesh.field.add("Distance", 4) # first add a distance field
            gmsh.model.mesh.field.setNumbers(4, "CurvesList", [c1]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(4, "Sampling", 100) 
            gmsh.model.mesh.field.add("Threshold", 5)
            gmsh.model.mesh.field.setNumber(5, "InField", 4)
            gmsh.model.mesh.field.setNumber(5, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(5, "SizeMax", 4 * self.lc)
            gmsh.model.mesh.field.setNumber(5, "DistMin", 0.1 * 1E-6)
            gmsh.model.mesh.field.setNumber(5, "DistMax", 0.15 * 1E-6)

            gmsh.model.mesh.field.add("Min", 6)            
            gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3])            
            gmsh.model.mesh.field.setAsBackgroundMesh(6)

            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)

        gmsh.model.mesh.generate(2)
        self.model = gmsh.model
        
    def visualize(self):
        gmsh.fltk.run()

        
class HemiSphere_v2(object):
    '''
    create a geometry for an inhomgenous strip
    '''

    def __init__(self, width_box, length_box, radius,
                 ms_lw, ref= False):


        self.w = width_box
        self.l = length_box
        self.radius = radius

        self.lc = ms_lw
        self.refinement = ref

        gmsh.initialize()
        gmsh.model.add('rectangle')

        
    def CreateGeometry(self):
#
#          -------------------------------
#         /                               \
#        /                                 \
#      p10           _______                p9 <- l5  
# l5-> |            /       \               | <- l3
#      |           /         \              |
#      p1-----------          --------------p8 <- l3 
#        ^l1             ^c1         ^l2

        factory = gmsh.model.geo

        p1 = factory.addPoint(0, 0, 0, self.lc, 1)
        p2 = factory.addPoint((self.w * 0.5) - self.radius ,
                              0, 0, self.lc, 2)
        p3 = factory.addPoint((self.w * 0.5) + self.radius ,
                              0, 0, self.lc, 3)
        p4 = factory.addPoint(self.w,
                              0, 0, self.lc, 4)
        
        p5 = factory.addPoint(self.w,
                              self.l, 0, self.lc, 5)
        p6 = factory.addPoint(0,
                              self.l, 0, self.lc, 6)

        p7 = factory.addPoint(self.w * 0.5,
                              0, 0, self.lc, 7)

        p8 = factory.addPoint(self.w * 0.5,
                              self.l, 0, self.lc, 8)
        
        l1 = factory.addLine(1, 2) # left half up to semi circle
        l2 = factory.addLine(3, 4) # right half from semi circle to box edge
        l3 = factory.addLine(4, 5) # right side 
#        l4 = factory.addLine(5, 6) # top 
        l5 = factory.addLine(6, 1) # left side 

        c1 = factory.addCircleArc(p3, p7, p2) # semicircle
        c2 = factory.addCircleArc(p5, p8, p6) # semicircle

        factory.addCurveLoop([l1, -c1, l2,
                              l3, c2, l5], 1)
        
        factory.addPlaneSurface([1], 1)
        
        factory.synchronize()

        x_translation = [1, 0, 0, 1,
                         0, 1, 0, 0,
                         0, 0, 1, 0,
                         0, 0, 0, 1]

        gmsh.model.mesh.setPeriodic(1, [l5], [l3], x_translation)  # mesh on line 2 (right) should match line 4 (left) via translation
        
        gmsh.model.addPhysicalGroup(1, [l1], name = 'inactive_area_1')
        gmsh.model.addPhysicalGroup(1, [c1], name = 'active_area_1')
        gmsh.model.addPhysicalGroup(1, [l2], name = 'inactive_area_2')
        gmsh.model.addPhysicalGroup(1, [c2], name = 'top_boundary')
        gmsh.model.addPhysicalGroup(1, [l5, l3], name = 'side_boundary')
        gmsh.model.addPhysicalGroup(2, [1], name = 'full_surface')

        if self.refinement == True:
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [c1]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 

            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", self.lc)

            gmsh.model.mesh.field.setNumber(3, "DistMin", self.l * 0.01)            
            gmsh.model.mesh.field.setNumber(3, "DistMax", self.l * 0.75) # 


            gmsh.model.mesh.field.add("Distance", 4) # first add a distance field
            gmsh.model.mesh.field.setNumbers(4, "CurvesList", [c1]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(4, "Sampling", 100) 
            gmsh.model.mesh.field.add("Threshold", 5)
            gmsh.model.mesh.field.setNumber(5, "InField", 4)
            gmsh.model.mesh.field.setNumber(5, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(5, "SizeMax", 4 * self.lc)
            gmsh.model.mesh.field.setNumber(5, "DistMin", 0.1 * 1E-6)
            gmsh.model.mesh.field.setNumber(5, "DistMax", 0.15 * 1E-6)

            gmsh.model.mesh.field.add("Min", 6)            
            gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3])            
            gmsh.model.mesh.field.setAsBackgroundMesh(6)

            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)

        gmsh.model.mesh.generate(2)
        self.model = gmsh.model
        
    def visualize(self):
        gmsh.fltk.run()

class HemiSphere(object):
    '''
    create a geometry for an inhomgenous strip
    '''

    def __init__(self, width_box, length_box, radius,
                 ms_lw, ref= False):


        self.w = width_box
        self.l = length_box
        self.radius = radius

        self.lc = ms_lw
        self.refinement = ref

        gmsh.initialize()
        gmsh.model.add('rectangle')

        
    def CreateGeometry(self):

#
#      p10--------------------------------- p9 <- l5
#      |             _______                |
# l5-> |            /       \               | <- l3
#      |           /         \              |
#      p1-----------          --------------p8 <- l3 
#        ^l1             ^c1         ^l2

        factory = gmsh.model.geo

        p1 = factory.addPoint(0, 0, 0, self.lc, 1)
        p2 = factory.addPoint((self.w * 0.5) - self.radius ,
                              0, 0, self.lc, 2)
        p3 = factory.addPoint((self.w * 0.5) + self.radius ,
                              0, 0, self.lc, 3)
        p4 = factory.addPoint(self.w,
                              0, 0, self.lc, 4)
        
        p5 = factory.addPoint(self.w,
                              self.l, 0, self.lc, 5)
        p6 = factory.addPoint(0,
                              self.l, 0, self.lc, 6)

        p7 = factory.addPoint(self.w * 0.5,
                              0, 0, self.lc, 7)

        l1 = factory.addLine(1, 2) # left half up to semi circle
        l2 = factory.addLine(3, 4) # right half from semi circle to box edge
        l3 = factory.addLine(4, 5) # right side 
        l4 = factory.addLine(5, 6) # top 
        l5 = factory.addLine(6, 1) # left side 

        c1 = factory.addCircleArc(p3, p7, p2) # semicircle 
        factory.addCurveLoop([l1, -c1, l2,
                              l3,l4, l5], 1)
        
        factory.addPlaneSurface([1], 1)
        
        factory.synchronize()

        x_translation = [1, 0, 0, 1,
                         0, 1, 0, 0,
                         0, 0, 1, 0,
                         0, 0, 0, 1]

        gmsh.model.mesh.setPeriodic(1, [l5], [l3], x_translation)  # mesh on line 2 (right) should match line 4 (left) via translation
        
        gmsh.model.addPhysicalGroup(1, [l1], name = 'inactive_area_1')
        gmsh.model.addPhysicalGroup(1, [c1], name = 'active_area_1')
        gmsh.model.addPhysicalGroup(1, [l2], name = 'inactive_area_2')
        gmsh.model.addPhysicalGroup(1, [l4], name = 'top_boundary')
        gmsh.model.addPhysicalGroup(1, [l5, l3], name = 'side_boundary')
        gmsh.model.addPhysicalGroup(2, [1], name = 'full_surface')

        if self.refinement == True:
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [c1]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 

            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", self.lc)

            gmsh.model.mesh.field.setNumber(3, "DistMin", self.l * 0.01)            
            gmsh.model.mesh.field.setNumber(3, "DistMax", self.l * 0.75) # 


            gmsh.model.mesh.field.add("Distance", 4) # first add a distance field
            gmsh.model.mesh.field.setNumbers(4, "CurvesList", [c1]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(4, "Sampling", 100) 
            gmsh.model.mesh.field.add("Threshold", 5)
            gmsh.model.mesh.field.setNumber(5, "InField", 4)
            gmsh.model.mesh.field.setNumber(5, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(5, "SizeMax", 4 * self.lc)
            gmsh.model.mesh.field.setNumber(5, "DistMin", 0.1 * 1E-6)
            gmsh.model.mesh.field.setNumber(5, "DistMax", 0.15 * 1E-6)

            gmsh.model.mesh.field.add("Min", 6)            
            gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3])            
            gmsh.model.mesh.field.setAsBackgroundMesh(6)

            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)

        gmsh.model.mesh.generate(2)
        self.model = gmsh.model
        
    def visualize(self):
        gmsh.fltk.run()

    def save(self,                                                                                                                                                                                                                                                                     
             save_path = './',                                                                                                                                                                                                                                                           
             mesh_name = 'default.msh'):                                                                                                                                                                                                                                                 
        
        print(save_path)
        if not mesh_name.endswith('.msh'):
            mesh_name += '.msh'
        gmsh.write(save_path + mesh_name)

class InhomogenousStrip(object):
    '''
    create a geometry for an inhomgenous strip 


    '''

    def __init__(self, width_box, length_box, rho_1, rho_2, rho_3,
                 ms_lw, ref= False):


        self.w = width_box
        self.l = length_box
        self.rho_1 = rho_1
        self.rho_2 = rho_2
        self.rho_3 = rho_3 

        self.lc = ms_lw
        self.refinement = ref

        self.A_ecsa_1 = self.rho_1 * self.w
        self.A_ecsa_2 = self.rho_2 * self.w
        self.A_ecsa_3 = self.rho_3 * self.w

        self.A_inactive = self.w - (self.A_ecsa_1 + self.A_ecsa_2 + self.A_ecsa_3)        
        self.rho_inactive_total = self.A_inactive/self.w
        self.rho_inactive = self.rho_inactive_total/4 # assume for now equal spacing

        self.rho_1_w = self.rho_inactive
        self.rho_2_w = self.rho_inactive
        self.rho_3_w = self.rho_inactive
        self.rho_4_w = self.rho_inactive

        self.width_1 = self.rho_1_w * self.w
        self.width_2 = self.rho_2_w * self.w
        self.width_3 = self.rho_3_w * self.w
        self.width_4 = self.rho_4_w * self.w
        
        gmsh.initialize()
        gmsh.model.add('rectangle')

        
    def CreateGeometry(self):

        factory = gmsh.model.geo

        p1 = factory.addPoint(0, 0, 0, self.lc, 1)
        p2 = factory.addPoint(self.width_1,
                              0, 0, self.lc, 2)
        p3 = factory.addPoint(self.width_1 + self.A_ecsa_1,
                              0, 0, self.lc, 3)
        p4 = factory.addPoint(self.width_1 + self.A_ecsa_1 + self.width_2,
                              0, 0, self.lc, 4)
        p5 = factory.addPoint(self.width_1 + self.A_ecsa_1 + self.width_2 + self.A_ecsa_2,
                              0, 0, self.lc, 5)
        p6 = factory.addPoint(self.width_1 + self.A_ecsa_1 + self.width_2 + self.A_ecsa_2 + self.width_3,
                              0, 0, self.lc, 6)
        p7 = factory.addPoint(self.width_1 + self.A_ecsa_1 + self.width_2 + self.A_ecsa_2 + self.width_3 + self.A_ecsa_3,
                              0, 0, self.lc, 7)
        p8 = factory.addPoint(self.width_1 + self.A_ecsa_1 + self.width_2 + self.A_ecsa_2 + self.width_3 + self.A_ecsa_3 + self.width_4,
                              0, 0, self.lc, 8)
        p9 = factory.addPoint(self.width_1 + self.A_ecsa_1 + self.width_2 + self.A_ecsa_2 + self.width_3 + self.A_ecsa_3 + self.width_4,
                              self.l, 0, self.lc, 9)

        p10 = factory.addPoint(0,
                               self.l, 0, self.lc, 10)

        l1 = factory.addLine(1, 2) # inactive area 1
        l2 = factory.addLine(2, 3) # active area 1
        l3 = factory.addLine(3, 4) # inactive area 2
        l4 = factory.addLine(4, 5) # active area 2
        l5 = factory.addLine(5, 6) # inactive area 3
        l6 = factory.addLine(6, 7) # active area 3
        l7 = factory.addLine(7, 8) # inactive area 4
        l8 = factory.addLine(8, 9) # right side wall 
        l9 = factory.addLine(9, 10) # top wall
        l10 = factory.addLine(10, 1) # left side wall         

        factory.addCurveLoop([l1, l2, l3, l4,
                              l5, l6, l7, l8,
                              l9, l10],
                             1)
        factory.addPlaneSurface([1], 1)
        
        factory.synchronize()

        x_translation = [1, 0, 0, 1,
                         0, 1, 0, 0,
                         0, 0, 1, 0,
                         0, 0, 0, 1]
        
        gmsh.model.mesh.setPeriodic(1, [l10], [l8], x_translation)  # mesh on line 2 (right) should match line 4 (left) via translation

        gmsh.model.addPhysicalGroup(1, [l1], name = 'inactive_area_1')
        gmsh.model.addPhysicalGroup(1, [l2], name = 'active_area_1')
        gmsh.model.addPhysicalGroup(1, [l3], name = 'inactive_area_2')
        gmsh.model.addPhysicalGroup(1, [l4], name = 'active_area_2')
        gmsh.model.addPhysicalGroup(1, [l5], name = 'inactive_area_3')
        gmsh.model.addPhysicalGroup(1, [l6], name = 'active_area_3')
        gmsh.model.addPhysicalGroup(1, [l7], name = 'inactive_area_4')
        gmsh.model.addPhysicalGroup(1, [l9], name = 'top_boundary')
        gmsh.model.addPhysicalGroup(1, [l10, l8], name = 'side_boundary')
        gmsh.model.addPhysicalGroup(2, [1], name = 'full_surface')

        if self.refinement == True:
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [l1, l3, l5, l7, 
                                                               l2, l4, l6]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 

            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", self.lc)

            gmsh.model.mesh.field.setNumber(3, "DistMin", self.l * 0.01)            
            gmsh.model.mesh.field.setNumber(3, "DistMax", self.l * 0.75) # 


            gmsh.model.mesh.field.add("Distance", 4) # first add a distance field
            gmsh.model.mesh.field.setNumbers(4, "CurvesList", [l2]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(4, "Sampling", 100) 
            gmsh.model.mesh.field.add("Threshold", 5)
            gmsh.model.mesh.field.setNumber(5, "InField", 4)
            gmsh.model.mesh.field.setNumber(5, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(5, "SizeMax", 4 * self.lc)
            gmsh.model.mesh.field.setNumber(5, "DistMin", 0.1 * 1E-6)
            gmsh.model.mesh.field.setNumber(5, "DistMax", 0.15 * 1E-6)

            gmsh.model.mesh.field.add("Min", 6)            
            gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3])            
            gmsh.model.mesh.field.setAsBackgroundMesh(6)

            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)

        gmsh.model.mesh.generate(2)
        self.model = gmsh.model
        
    def visualize(self):
        gmsh.fltk.run()
    
        
class Rectangle3(object):
    '''
    create a 2d rectangle with length and height and add physical groups for bottom, sides and top 
    ensure that the sides are pbc. The mesh is refined towards the bottom since that is where the reaction happens.
    here we also allow for two defined regions for example active/inactive 

    center the 'active strip' to make sure periodic conditions are actually enforced properly
    '''

    def __init__(self, width_box, length_box, width_active_strip,
                 ms_lw, ref=False):        
        
        self.w = width_box
        self.l = length_box
        self.active_start = 0.5 * self.w - 0.5 * width_active_strip
        self.active_end = 0.5 * self.w + 0.5 * width_active_strip

        self.lc = ms_lw
        self.refinement = ref
        gmsh.initialize()
        gmsh.model.add('rectangle')

    def CreateGeometry(self):

        #      p6------------p5 <- l5  
        # l6-> |              | <- l4
        #      p1---p2__p3---p4 <- l3 
        #         ^l1 ^l2
        factory = gmsh.model.geo
        
        p1 = factory.addPoint(0, 0, 0, self.lc, 1)
        p2 = factory.addPoint(self.active_start, 0, 0, self.lc, 2)
        p3 = factory.addPoint(self.active_end, 0, 0, self.lc, 3) 
        p4 = factory.addPoint(self.w, 0, 0, self.lc, 4)
        p5 = factory.addPoint(self.w, self.l, 0, self.lc, 5)
        p6 = factory.addPoint(0, self.l, 0, self.lc, 6)
        
        l1 = factory.addLine(1, 2)
        l2 = factory.addLine(2, 3)
        l3 = factory.addLine(3, 4)
        l4 = factory.addLine(4, 5)
        l5 = factory.addLine(5, 6)
        l6 = factory.addLine(6, 1)
        
        factory.addCurveLoop([l1, l2, l3, l4, l5, l6],
                             1)
        factory.addPlaneSurface([1], 1)
        
        factory.synchronize()

        x_translation = [1, 0, 0, 1,
                         0, 1, 0, 0,
                         0, 0, 1, 0,
                         0, 0, 0, 1]

        gmsh.model.mesh.setPeriodic(1, [l4], [l6], x_translation)  # mesh on line 2 (right) should match line 4 (left) via translation

        gmsh.model.addPhysicalGroup(1, [l1], name = 'inactive_bottom_1')
        gmsh.model.addPhysicalGroup(1, [l2], name = 'active_bottom')
        gmsh.model.addPhysicalGroup(1, [l3], name = 'inactive_bottom_2')         
        gmsh.model.addPhysicalGroup(1, [l5], name = 'top_boundary') 
        gmsh.model.addPhysicalGroup(1, [l4, l6], name = 'side_boundary')
        gmsh.model.addPhysicalGroup(2, [1], name = 'full_surface')        
        
        if self.refinement == True:
            # would be better if this were dictionary or some sort of function
            # that would be passed on to the class this current way is stupid.
            
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [l1, l2, l3]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 

            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 20)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", 4 * self.lc)

            gmsh.model.mesh.field.setNumber(3, "DistMin", 0.2 * 1E-6)            
            gmsh.model.mesh.field.setNumber(3, "DistMax", 25 * 1E-6)


            gmsh.model.mesh.field.add("Distance", 4) # first add a distance field
            gmsh.model.mesh.field.setNumbers(4, "CurvesList", [l2]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(4, "Sampling", 100) 
            gmsh.model.mesh.field.add("Threshold", 5)
            gmsh.model.mesh.field.setNumber(5, "InField", 4)
            gmsh.model.mesh.field.setNumber(5, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(5, "SizeMax", 4 * self.lc)
            gmsh.model.mesh.field.setNumber(5, "DistMin", 0.1 * 1E-6)
            gmsh.model.mesh.field.setNumber(5, "DistMax", 0.15 * 1E-6)

            gmsh.model.mesh.field.add("Min", 6)            
#            gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3, 5])
            gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3])            
            gmsh.model.mesh.field.setAsBackgroundMesh(6)

            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)
        
        
        gmsh.model.mesh.generate(2)
        self.model = gmsh.model
        
    def visualize(self):
        gmsh.fltk.run()

    def save(self, save_path = './', 
             mesh_name = 'default.msh'):
        print(save_path)
        if not mesh_name.endswith('.msh'):
            mesh_name += '.msh'
        gmsh.write(save_path + mesh_name)
        


class Rectangle2(object):
    '''
    create a 2d rectangle with length and height and add physical groups for bottom, sides and top 
    ensure that the sides are pbc. The mesh is refined towards the bottom since that is where the reaction happens.
    here we also allow for two defined regions for example active/inactive 

    '''

    def __init__(self, w, w2, l, ms_lw, ref=False):

        self.w = w
        self.inactive = w2
        self.l = l
        self.lc = ms_lw
        self.refinement = ref
        gmsh.initialize()
        gmsh.model.add('rectangle')

    def CreateGeometry(self):

        #      p4---------p5 <- l4  
        # l5-> |          | <- l3
        #      p1--p2|---p3 <- l2 (0 -> w/2 -> w)
        #      ^- l1
        factory = gmsh.model.geo
        
        p1 = factory.addPoint(0, 0, 0, self.lc, 1)
        p2 = factory.addPoint(self.inactive, 0, 0, self.lc, 2) 
        p3 = factory.addPoint(self.w, 0, 0, self.lc, 3)
        p4 = factory.addPoint(0, self.l, 0, self.lc, 4)
        p5 = factory.addPoint(self.w, self.l, 0, self.lc, 5)

        l1 = factory.addLine(1, 2)
        l2 = factory.addLine(2, 3)
        l3 = factory.addLine(3, 5)
        l4 = factory.addLine(5, 4)
        l5 = factory.addLine(4, 1)
        
        factory.addCurveLoop([l1, l2, l3, l4, l5],
                             1)
        factory.addPlaneSurface([1], 1)
        
        factory.synchronize()

        x_translation = [1, 0, 0, 1,
                         0, 1, 0, 0,
                         0, 0, 1, 0,
                         0, 0, 0, 1]

        gmsh.model.mesh.setPeriodic(1, [l3], [l5], x_translation)  # mesh on line 2 (right) should match line 4 (left) via translation

        gmsh.model.addPhysicalGroup(1, [l1], name = 'bottom_boundary 1')
        gmsh.model.addPhysicalGroup(1, [l2], name = 'bottom_boundary 2')         
        gmsh.model.addPhysicalGroup(1, [l4], name = 'top_boundary') 
        gmsh.model.addPhysicalGroup(1, [l3, l5], name = 'side_boundary')
        gmsh.model.addPhysicalGroup(2, [1], name = 'full_surface')        
        
        if self.refinement == True:
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [l1, l2, p2]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 

            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 20)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", 4 * self.lc)
            gmsh.model.mesh.field.setNumber(3, "DistMin", 0.2 * 1E-6)            
            gmsh.model.mesh.field.setNumber(3, "DistMax", 25 * 1E-6)


            gmsh.model.mesh.field.add("Distance", 4) # first add a distance field
            gmsh.model.mesh.field.setNumbers(4, "CurvesList", [p2]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(4, "Sampling", 100) 

            gmsh.model.mesh.field.add("Threshold", 5)
            gmsh.model.mesh.field.setNumber(5, "InField", 4)
            gmsh.model.mesh.field.setNumber(5, "SizeMin", self.lc / 30)
            gmsh.model.mesh.field.setNumber(5, "SizeMax", 4 * self.lc)
            gmsh.model.mesh.field.setNumber(5, "DistMin", 0.1 * 1E-6)
            gmsh.model.mesh.field.setNumber(5, "DistMax", 0.15 * 1E-6)

            gmsh.model.mesh.field.add("Min", 6)            
            gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3, 5])
#            gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3])            
            gmsh.model.mesh.field.setAsBackgroundMesh(6)

            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)
        
        
        gmsh.model.mesh.generate(2)
        self.model = gmsh.model
        
    def visualize(self):
        gmsh.fltk.run()

    def save(self,
             save_path = './',
             mesh_name = 'default.msh'):
        if not save_path.endswith('/'):
            save_path += '/'
        
        print(save_path)
        if not mesh_name.endswith('.msh'):
            mesh_name += '.msh'
        gmsh.write(save_path + mesh_name)
        

class SinusoidalWall(object):
    '''
    create a rectangle with a sinusoidal wall at the bottom the sides are ensured to be periodic boundaries.
    '''

    def __init__(self, w, l, amplitude, alpha, num_points, ms_lw,  ref = False):

        self.w = w
        self.l = l
        self.amplitude = amplitude
        self.alpha = alpha
        self.num_points = num_points
        self.lc = ms_lw
        self.refinement = ref
        gmsh.initialize()
        gmsh.model.add('SinusoidalWall')

    def CreateGeometry(self):

        #      ----- <- l3  
        # l4-> |   | <- l2 
        #      ----- <- l1 (0 -> w) this would be sinusoidal section
        def sinusoidal_wall(x, amplitude, alpha, width):
            return amplitude * np.sin(2 * np.pi * x / (alpha*width))

        def curve_length_integrand(x, amplitude, alpha, width):
            B = (2 * np.pi)/(alpha * width)    
            dy_dx = amplitude * B * np.cos(B * x)
            integrand = np.sqrt(1 + dy_dx**2)
            return integrand

        factory = gmsh.model.geo

        x_vals = np.linspace(0, self.w, self.num_points)
        y_vals = sinusoidal_wall(x_vals, self.amplitude, self.alpha, self.w)

        self.curve_length = quad(curve_length_integrand, 0, self.w, args = (self.amplitude,
                                                                            self.alpha,
                                                                            self.w))
#        y_vals = self.amplitude * np.sin(2 * np.pi * x_vals / (self.alpha * self.w))

        sinusoidal_points = []
        for x, y in zip(x_vals, y_vals):
            point = factory.addPoint(x, y, 0, self.lc)
            sinusoidal_points.append(point)

        fig, ax = plt.subplots()
        ax.plot(x_vals, y_vals)
        fig.savefig('sin_boundary.pdf')
            
        # Connect the sinusoidal points with lines
        sinusoidal_lines = []
        for i in range(self.num_points - 1):
            line = factory.addLine(sinusoidal_points[i], sinusoidal_points[i + 1])
            sinusoidal_lines.append(line)

        sinusoidal_lines_copy = copy.deepcopy(sinusoidal_lines)
        p1 = factory.addPoint(0, self.l, 0, self.lc, sinusoidal_points[-1] + 1)
        p2 = factory.addPoint(self.w, self.l, 0, self.lc, sinusoidal_points[-1] + 2)

        l1 = factory.addLine(p1, p2)
        l2 = factory.addLine(sinusoidal_points[0], p1)
        l3 = factory.addLine(p2, sinusoidal_points[-1])

        sinusoidal_lines.append(-l3)
        sinusoidal_lines.append(-l1)
        sinusoidal_lines.append(-l2)
        factory.addCurveLoop(sinusoidal_lines, 1)
        factory.addPlaneSurface([1], 1)        

        gmsh.option.setNumber("Geometry.Tolerance", 1e-15) # do we need this??        
        factory.synchronize()
        
        gmsh.model.addPhysicalGroup(1, sinusoidal_lines_copy, name = 'bottom_boundary') 
        gmsh.model.addPhysicalGroup(1, [l1], name = 'top_boundary') 
        gmsh.model.addPhysicalGroup(1, [l2, l3], name = 'side_boundary')
        gmsh.model.addPhysicalGroup(2, [1], name = 'full_surface')        
        
        # for refinement
        if self.refinement == True:
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", sinusoidal_lines_copy) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 

            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 20)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", 4 * self.lc)
            #            gmsh.model.mesh.field.setNumber(3, "DistMin", max(self.l/3 - 0.2, 0.1))
            gmsh.model.mesh.field.setNumber(3, "DistMin", 0.2 * 1E-6)            
            gmsh.model.mesh.field.setNumber(3, "DistMax", 25 * 1E-6)
            gmsh.model.mesh.field.setAsBackgroundMesh(3)

            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)

        # Create mesh
        gmsh.model.mesh.generate(2)
        self.model = gmsh.model
        
    def visualize(self):
        gmsh.fltk.run()
        
        
class Rectangle(object):
    '''
    create a 2d rectangle with length and height and add physical groups for bottom, sides and top 
    ensure that the sides are pbc. The mesh is refined towards the bottom since that is where the reaction happens.
    '''

    def __init__(self, w, l, ms_lw,
                 ref=False, small_size = False):

        self.w = w
        self.l = l
        self.lc = ms_lw
        self.refinement = ref
        self.small_size = small_size
        gmsh.initialize()
        gmsh.model.add('rectangle')

        if self.small_size == True:
            print('reducing the tolerance!')
            gmsh.option.setNumber("Geometry.Tolerance", 1-10)
        
    def CreateGeometry(self):

        #      ----- <- l3  
        # l4-> |   | <- l2 
        #      ----- <- l1 (0 -> w)
        factory = gmsh.model.geo
        
        factory.addPoint(0, 0, 0, self.lc, 1)
        factory.addPoint(self.w, 0, 0, self.lc, 2)
        factory.addPoint(0, self.l, 0, self.lc, 3)
        factory.addPoint(self.w, self.l, 0, self.lc, 4)

        l1 = factory.addLine(1, 2)
        l2 = factory.addLine(2, 4)
        l3 = factory.addLine(4, 3)
        l4 = factory.addLine(3, 1)
        factory.addCurveLoop([l1, l2, l3, l4],
                             1)
        factory.addPlaneSurface([1], 1)
        
        factory.synchronize()

        x_translation = [1, 0, 0, 1,
                         0, 1, 0, 0,
                         0, 0, 1, 0,
                         0, 0, 0, 1]

#        gmsh.model.mesh.setPeriodic(1, [l2], [l4], x_translation)  # mesh on line 2 (right) should match line 4 (left) via translation
#        gmsh.model.mesh.setPeriodic(1, [l4], [l2], x_translation)  # mesh on line 2 (right) should match line 4 (left) via translation
        
        gmsh.model.addPhysicalGroup(1, [l1], name = 'bottom_boundary') 
        gmsh.model.addPhysicalGroup(1, [l3], name = 'top_boundary') 
        gmsh.model.addPhysicalGroup(1, [l2, l4], name = 'side_boundary')
        gmsh.model.addPhysicalGroup(2, [1], name = 'full_surface')        

        if self.refinement == True and self.small_size == True:
            print('Doing the refinement for the small.')
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [l1]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 
            
            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 3500)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", self.lc)

            gmsh.model.mesh.field.setNumber(3, "DistMin", self.l * 1e-5)
            gmsh.model.mesh.field.setNumber(3, "DistMax", self.l * 50 * 1e-5)
            # gmsh.model.mesh.field.setNumber(3, "DistMin", 0.001 * self.l)
            # gmsh.model.mesh.field.setNumber(3, "DistMax", 0.005 * self.l)
            
            gmsh.model.mesh.field.add("Min", 6)            
            gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3])            
            gmsh.model.mesh.field.setAsBackgroundMesh(6)
            
            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)

        # for refinement
        if self.refinement == True and self.small_size == False:            
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [l1]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 

            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 20)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", 4 * self.lc)
#            gmsh.model.mesh.field.setNumber(3, "DistMin", max(self.l/3 - 0.2, 0.1))
            gmsh.model.mesh.field.setNumber(3, "DistMin", self.l/11)            
            gmsh.model.mesh.field.setNumber(3, "DistMax", self.l/8)
            gmsh.model.mesh.field.setAsBackgroundMesh(3)

            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)
        
        
        gmsh.model.mesh.generate(2)
        self.model = gmsh.model
        
    def visualize(self):
        gmsh.fltk.run()

    def save(self,
             save_path = './',      
             mesh_name = 'default.msh'):
        if not save_path.endswith('/'):
            save_path += '/'
        
        if not mesh_name.endswith('.msh'):
            mesh_name += '.msh'
        gmsh.write(save_path + mesh_name)
        
class SphereInBox(object):
    '''
    create the necessary geometry 
    '''

    def __init__(self, r, h, w, l,
                 ms_h, ms_lw):
#                 h_meshsize, w_meshsize, l_meshsize):

        '''
        Parameters

        r: is the radius of the sphere
        h: is the height of the box (zmax)
        w: is the width of the box (xmax)
        l: is the length of the box (ymax)
        h_meshsize: meshing constraint for the h meshsize
        w_meshsize: meshing constraint for the w meshsize
        l_meshsize: meshing constraint for the l meshsize

        '''
        self.r = r
        self.h = h
        self.w = w
        self.l = l
        self.ms_h = ms_h
        self.ms_lw = ms_lw
#        self.h_ms = h_meshsize
#        self.w_ms = w_meshsize
#        self.l_ms = l_meshsize

        gmsh.initialize()
        gmsh.model.add('SphereInBox')

        
    def CreateGeometry(self):

        factory = gmsh.model.geo
        
        factory.addPoint(0, 0, 0, self.ms_lw, 1)
        factory.addPoint(self.w, 0, 0, self.ms_lw, 2)
        factory.addPoint(0, self.l, 0, self.ms_lw, 3)
        factory.addPoint(self.w, self.l, 0, self.ms_lw, 4)

        factory.addLine(1, 2, 1)
        factory.addLine(2, 4, 2)
        factory.addLine(4, 3, 3)
        factory.addLine(3, 1, 4)
        factory.addCurveLoop([1, 2, 3, 4], 1)
        factory.addPlaneSurface([1], 1)

        factory.addPoint(0, 0, self.h, self.ms_h, 5)
        factory.addPoint(0, self.l, self.h, self.ms_h, 6)

        factory.addLine(1, 5, 5)
        factory.addLine(5, 6, 6)
        factory.addLine(6, 3, 7)

        factory.addCurveLoop([5, 6, 7, 4], 2)
        factory.addPlaneSurface([2], 2)

        factory.addPoint(self.w, 0, self.h, self.ms_h, 7)
        factory.addPoint(self.w, self.l, self.h, self.ms_h, 8)

        factory.addLine(7, 8, 8)
        factory.addLine(8, 6, 9)
        factory.addLine(5, 7, 10)

        factory.addCurveLoop([8, 9, -6, 10], 3)
        factory.addPlaneSurface([3], 3)

        factory.addLine(7, 2, 11)
        factory.addLine(4, 8, 12)

        factory.addCurveLoop([-8, 11, 2, 12], 4)
        factory.addPlaneSurface([4], 4)

        factory.addCurveLoop([1, -11, -10, -5], 5)
        factory.addPlaneSurface([5], 5)

        factory.addCurveLoop([12, 9 ,  7 , -3], 6)
        factory.addPlaneSurface([6], 6)


        p1 = factory.addPoint(self.w/2, self.l/2, self.h/2,
                              self.ms_lw)
        p2 = factory.addPoint(self.w/2 + self.r, self.l/2, self.h/2, self.ms_lw)
        p3 = factory.addPoint(self.w/2 - self.r, self.l/2, self.h/2, self.ms_lw)

        p4 = factory.addPoint(self.w/2, self.l/2, self.h/2 + self.r, self.ms_lw)
        p5 = factory.addPoint(self.w/2, self.l/2, self.h/2 - self.r, self.ms_lw)
        p6 = factory.addPoint(self.w/2, self.l/2 + self.r, self.h/2, self.ms_lw)
        p7 = factory.addPoint(self.w/2, self.l/2 - self.r, self.h/2, self.ms_lw)

        c1 = factory.addCircleArc(p3, p1, p4)
        c2 = factory.addCircleArc(p3, p1, p7)
        c3 = factory.addCircleArc(p7, p1, p4)
        c4 = factory.addCircleArc(p3, p1, p5)
        c5 = factory.addCircleArc(p7, p1, p5)
        c5 = factory.addCircleArc(p7, p1, p5)
        c6 = factory.addCircleArc(11, p1, 14)
        c7 = factory.addCircleArc(14, p1, 10)
        c8 = factory.addCircleArc(10, p1, 15)
        c9 = factory.addCircleArc(12, p1, 10)
        c10 = factory.addCircleArc(10, p1, 13)
        c11 = factory.addCircleArc(12, p1, 14)
        c12 = factory.addCircleArc(14, p1, 13)


        l1 = factory.addCurveLoop([13, 24, -19])
        s1 = factory.addSurfaceFilling([l1])
        
        l2 = factory.addCurveLoop([14, 15, -13])
        s2 = factory.addSurfaceFilling([l2])
        
        l3 = factory.addCurveLoop([21, 15, 22])
        s3 = factory.addSurfaceFilling([l3])
        
        l4 = factory.addCurveLoop([20, 23, -25 ])
        s4 = factory.addSurfaceFilling([l4])

        l5 = factory.addCurveLoop([22, -20, -24])
        s5 = factory.addSurfaceFilling([l5])
        
        l6 = factory.addCurveLoop([21, 17, -23])
        s6 = factory.addSurfaceFilling([l6])
        
        l7 = factory.addCurveLoop([14, 17, -16])
        s7 = factory.addSurfaceFilling([l7])
        
        l8 = factory.addCurveLoop([19, 25, -16])
        s8 = factory.addSurfaceFilling([l8])


        # add surface loop for the sphere 
        factory.addSurfaceLoop([1, 2, 3,
                               4, 5, 6],
                              1)

        factory.addSurfaceLoop([s1, s2, s3, s4,
                                       s5, s6, s7, s8],
                              2)
        
        factory.addVolume([1, 2], 1)

        factory.synchronize()


 # you control the translation with the last three entries in this case (1, 0, 0) and then matches via new_cords = M * old_cords where old_cords are given by [x, y, z, 1]
        
        x_translation = [1, 0, 0, 1,
                         0, 1, 0, 0,
                         0, 0, 1, 0,
                         0, 0, 0, 1]

        gmsh.model.mesh.setPeriodic(2, [4], [2], x_translation)  # mesh on surface 4 (right) should match surface 2 (left) via translation

        y_translation = [1, 0, 0, 0,
                         0, 1, 0, 1,
                         0, 0, 1, 0,
                         0, 0, 0, 1]


        gmsh.model.mesh.setPeriodic(2, [6], [5], y_translation)


        gmsh.model.addPhysicalGroup(2, [1], name = 'bottom_boundary') 

        gmsh.model.addPhysicalGroup(2, [3], name = 'top_boundary') 
        gmsh.model.addPhysicalGroup(2, [2, 4], name = 'side_x_boundary')
        
        gmsh.model.addPhysicalGroup(2, [5, 6], name = 'side_y_boundary')
        
        gmsh.model.addPhysicalGroup(2, [s1, s2, s3,
                                        s4, s5, s6, 
                                        s7, s8], name = 'sphere')

        gmsh.model.addPhysicalGroup(3, [1], name = 'interior_volume') 
        
        gmsh.model.mesh.generate(3)

    def visualize(self):
        gmsh.fltk.run()


class SphereBottomBox(object):
    '''
    create the necessary geometry  for the sphere at the bottom of the box
    '''

    def __init__(self, r, h, w, l,
                 ms_h, ms_lw):
#                 h_meshsize, w_meshsize, l_meshsize):

        '''
        Parameters

        r: is the radius of the sphere
        h: is the height of the box (zmax)
        w: is the width of the box (xmax)
        l: is the length of the box (ymax)
        h_meshsize: meshing constraint for the h meshsize
        w_meshsize: meshing constraint for the w meshsize
        l_meshsize: meshing constraint for the l meshsize

        '''
        self.r = r
        self.h = h
        self.w = w
        self.l = l
        self.ms_h = ms_h
        self.ms_lw = ms_lw

#        self.h_ms = h_meshsize
#        self.w_ms = w_meshsize
#        self.l_ms = l_meshsize

        gmsh.initialize()
        gmsh.model.add('SphereInBox')

        
    def CreateGeometry(self):

        factory = gmsh.model.geo
        
        factory.addPoint(0, 0, 0, self.ms_lw, 1)
        factory.addPoint(self.w, 0, 0, self.ms_lw, 2)
        factory.addPoint(0, self.l, 0, self.ms_lw, 3)
        factory.addPoint(self.w, self.l, 0, self.ms_lw, 4)

        factory.addLine(1, 2, 1)
        factory.addLine(2, 4, 2)
        factory.addLine(4, 3, 3)
        factory.addLine(3, 1, 4)
#        factory.addCurveLoop([1, 2, 3, 4], 1)
#        factory.addPlaneSurface([1], 1)

        factory.addPoint(0, 0, self.h, self.ms_h, 5)
        factory.addPoint(0, self.l, self.h, self.ms_h, 6)

        factory.addLine(1, 5, 5)
        factory.addLine(5, 6, 6)
        factory.addLine(6, 3, 7)

        factory.addCurveLoop([5, 6, 7, 4], 2)
        factory.addPlaneSurface([2], 2)

        factory.addPoint(self.w, 0, self.h, self.ms_h, 7)
        factory.addPoint(self.w, self.l, self.h, self.ms_h, 8)

        factory.addLine(7, 8, 8)
        factory.addLine(8, 6, 9)
        factory.addLine(5, 7, 10)

        factory.addCurveLoop([8, 9, -6, 10], 3)
        factory.addPlaneSurface([3], 3)

        factory.addLine(7, 2, 11)
        factory.addLine(4, 8, 12)

        factory.addCurveLoop([-8, 11, 2, 12], 4)
        factory.addPlaneSurface([4], 4)

        factory.addCurveLoop([1, -11, -10, -5], 5)
        factory.addPlaneSurface([5], 5)

        factory.addCurveLoop([12, 9 ,  7 , -3], 6)
        factory.addPlaneSurface([6], 6)


        # this is the sphere part lets add the bottom 'center'
        p1 = factory.addPoint(self.w/2, self.l/2, 0,
                              self.ms_lw) # y plane x plane 

        # the true center
        p2 = factory.addPoint(self.w/2, self.l/2, self.r,
                              self.ms_lw) # y plane x plane
        
        p3 = factory.addPoint(self.w/2 + self.r, self.l/2, self.r, self.ms_lw) # y plane

        p4 = factory.addPoint(self.w/2 - self.r, self.l/2, self.r, self.ms_lw) # y plane

        p5 = factory.addPoint(self.w/2, self.l/2, 2 * self.r, self.ms_lw) # y plane x plane

        p6 = factory.addPoint(self.w/2, self.l/2 + self.r, self.r, self.ms_lw) # x plane

        p7 = factory.addPoint(self.w/2, self.l/2 - self.r, self.r, self.ms_lw) # x plane

        # x plane
        c1 = factory.addCircleArc(p1, p2, p6, 13)
        c2 = factory.addCircleArc(p6, p2, p5, 14)        
        c3 = factory.addCircleArc(p5, p2, p7, 15)
        c4 = factory.addCircleArc(p7, p2, p1, 16)

        # z plane
        c5 = factory.addCircleArc(p6, p2, p3, 17)
        c6 = factory.addCircleArc(p3, p2, p7, 18)        
        c7 = factory.addCircleArc(p7, p2, p4, 19)
        c8 = factory.addCircleArc(p4, p2, p6, 20)

        # the y plane
        c9 = factory.addCircleArc(p4, p2, p5, 21)
        c10 = factory.addCircleArc(p4, p2, p1, 22)
        c11 = factory.addCircleArc(p3, p2, p1, 23)
        c12 = factory.addCircleArc(p3, p2, p5, 24)
        
        l1 = factory.addCurveLoop([c3, -c6, c12]) # 
        s1 = factory.addSurfaceFilling([l1])
        
        l2 = factory.addCurveLoop([c7, c9, c3])
        s2 = factory.addSurfaceFilling([l2])
        
        l3 = factory.addCurveLoop([c8, c2, -c9])
        s3 = factory.addSurfaceFilling([l3])
        
        l4 = factory.addCurveLoop([c12, -c2, c5])
        s4 = factory.addSurfaceFilling([l4])

        l5 = factory.addCurveLoop([c11, -c4, -c6])
        s5 = factory.addSurfaceFilling([l5])
        
        l6 = factory.addCurveLoop([c11, c1, c5])
        s6 = factory.addSurfaceFilling([l6])
        
        l7 = factory.addCurveLoop([c10, c1, -c8])
        s7 = factory.addSurfaceFilling([l7])
        
        l8 = factory.addCurveLoop([c4, -c10, -c7])
        s8 = factory.addSurfaceFilling([l8])

# adding bottom surface where it is disconnected I am not sure if this is actually necessary        
        bottom_l1 = factory.addLine(1, p1)
        bottom_l2 = factory.addLine(2, p1)
        bottom_l3 = factory.addLine(3, p1)
        bottom_l4 = factory.addLine(4, p1)

        bottom_c1 = factory.addCurveLoop([bottom_l1, -bottom_l3, 4])
        bottom_c2 = factory.addCurveLoop([bottom_l1, -bottom_l2, -1])
        bottom_c3 = factory.addCurveLoop([bottom_l2, -bottom_l4, -2])
        bottom_c4 = factory.addCurveLoop([bottom_l4, -bottom_l3, -3])

        bottom_s1 = factory.addPlaneSurface([bottom_c1])
        bottom_s2 = factory.addPlaneSurface([bottom_c2])
        bottom_s3 = factory.addPlaneSurface([bottom_c3])
        bottom_s4 = factory.addPlaneSurface([bottom_c4])        

        factory.addSurfaceLoop([bottom_s1, bottom_s2, bottom_s3, bottom_s4,
                                2, 3, 4, 5, 6],
                               1)

        factory.addSurfaceLoop([s1, s2, s3, s4,
                                s5, s6, s7, s8],
                              2)
        
        factory.addVolume([1, 2], 1)



        factory.synchronize()


 # you control the translation with the last three entries in this case (1, 0, 0) and then matches via new_cords = M * old_cords where old_cords are given by [x, y, z, 1]
        
        x_translation = [1, 0, 0, self.w, # 1
                         0, 1, 0, 0,
                         0, 0, 1, 0,
                         0, 0, 0, 1]

        gmsh.model.mesh.setPeriodic(2, [4], [2], x_translation)  # mesh on surface 4 (right) should match surface 2 (left) via translation

        y_translation = [1, 0, 0, 0,
                         0, 1, 0, self.l, # 1
                         0, 0, 1, 0,
                         0, 0, 0, 1]


        gmsh.model.mesh.setPeriodic(2, [6], [5], y_translation)


        gmsh.model.addPhysicalGroup(2, [bottom_s1, bottom_s2, bottom_s3, bottom_s4],
                                    name = 'bottom_boundary') 

        gmsh.model.addPhysicalGroup(2, [3], name = 'top_boundary') 
        gmsh.model.addPhysicalGroup(2, [2, 4], name = 'side_x_boundary')
        
        gmsh.model.addPhysicalGroup(2, [5, 6], name = 'side_y_boundary')
        
        gmsh.model.addPhysicalGroup(2, [s1, s2, s3,
                                        s4, s5, s6, 
                                        s7, s8], name = 'sphere')

        gmsh.model.addPhysicalGroup(3, [1], name = 'interior_volume') 
        
        gmsh.model.mesh.generate(3)

        self.model = gmsh.model
#        gmsh.finalize()        
    def visualize(self):
        gmsh.fltk.run()        


class Rectangle_wall(object):
    '''
    create a 2d rectangle with length and height and add physical groups for bottom, sides and top 
    ensure that the sides are pbc. The mesh is refined towards the bottom since that is where the reaction happens.
    This is only for debugging the cylinderical coords 
    '''

    def __init__(self, w, l, ms_lw, ref=False):

        self.w = w
        self.l = l
        self.lc = ms_lw
        self.refinement = ref
        gmsh.initialize()
        gmsh.model.add('rectangle')

    def CreateGeometry(self):

        #      ----- <- l3  
        # l4-> |   | <- l2 
        #      ----- <- l1 (0 -> w)
        factory = gmsh.model.geo
        
        factory.addPoint(0, 0, 0, self.lc, 1)
        factory.addPoint(self.w, 0, 0, self.lc, 2)
        factory.addPoint(0, self.l, 0, self.lc, 3)
        factory.addPoint(self.w, self.l, 0, self.lc, 4)

        l1 = factory.addLine(1, 2)
        l2 = factory.addLine(2, 4)
        l3 = factory.addLine(4, 3)
        l4 = factory.addLine(3, 1)
        factory.addCurveLoop([l1, l2, l3, l4],
                             1)
        factory.addPlaneSurface([1], 1)
        
        factory.synchronize()

        x_translation = [1, 0, 0, 1,
                         0, 1, 0, 0,
                         0, 0, 1, 0,
                         0, 0, 0, 1]

#        gmsh.model.mesh.setPeriodic(1, [l2], [l4], x_translation)  # mesh on line 2 (right) should match line 4 (left) via translation
#        gmsh.model.mesh.setPeriodic(1, [l4], [l2], x_translation)  # mesh on line 2 (right) should match line 4 (left) via translation
        
        gmsh.model.addPhysicalGroup(1, [l1], name = 'bottom_boundary') 
        gmsh.model.addPhysicalGroup(1, [l3], name = 'top_boundary') 
        gmsh.model.addPhysicalGroup(1, [l2], name = 'right_side_boundary')
        gmsh.model.addPhysicalGroup(1, [l4], name = 'left_side_boundary')        
        gmsh.model.addPhysicalGroup(2, [1], name = 'full_surface')        

        # for refinement
        if self.refinement == True:
            gmsh.model.mesh.field.add("Distance", 2) # first add a distance field
            gmsh.model.mesh.field.setNumbers(2, "CurvesList", [l1]) # as we get closer to the bottom surface         
            gmsh.model.mesh.field.setNumber(2, "Sampling", 100) 

            gmsh.model.mesh.field.add("Threshold", 3)
            gmsh.model.mesh.field.setNumber(3, "InField", 2)
            gmsh.model.mesh.field.setNumber(3, "SizeMin", self.lc / 20)
            gmsh.model.mesh.field.setNumber(3, "SizeMax", 4 * self.lc)
#            gmsh.model.mesh.field.setNumber(3, "DistMin", max(self.l/3 - 0.2, 0.1))
            gmsh.model.mesh.field.setNumber(3, "DistMin", self.l/11)            
            gmsh.model.mesh.field.setNumber(3, "DistMax", self.l/8)
            gmsh.model.mesh.field.setAsBackgroundMesh(3)

            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.Algorithm", 5)
        
        
        gmsh.model.mesh.generate(2)
        self.model = gmsh.model
        
    def visualize(self):
        gmsh.fltk.run()    

    def save(self, save_path = './',
             mesh_name = 'default.msh'):
        
        print(save_path)
        if not mesh_name.endswith('.msh'):
            mesh_name += '.msh'
        gmsh.write(save_path + mesh_name)
        
