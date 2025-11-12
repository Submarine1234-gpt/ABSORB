"""
Rotation optimizer for adsorbate orientation
"""
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.spatial.transform import Rotation
from .base_optimizer import BaseOptimizer


class RotationOptimizer(BaseOptimizer):
    """
    Optimizes adsorbate orientation through rotation
    """
    
    def __init__(self, rotation_method='normal', rotation_count=50, 
                 rotation_step=30, **kwargs):
        """
        Initialize rotation optimizer
        
        Args:
            rotation_method: 'normal' for axis rotation or 'sphere' for spherical sampling
            rotation_count: Number of rotation axes for sphere method
            rotation_step: Rotation step in degrees for sphere method
            **kwargs: Additional arguments passed to BaseOptimizer
        """
        super().__init__(**kwargs)
        self.rotation_method = rotation_method
        self.rotation_count = rotation_count
        self.rotation_step = rotation_step
    
    def optimize(self, system, adsorbate_indices, normal=None, **kwargs):
        """
        Optimize adsorbate rotation
        
        Args:
            system: ASE Atoms object
            adsorbate_indices: Indices of adsorbate atoms
            normal: Surface normal vector (required for 'normal' method)
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (optimized_system, info_dict)
        """
        if self.rotation_method == 'sphere':
            return self._optimize_sphere_rotation(system, adsorbate_indices)
        else:
            return self._optimize_normal_rotation(system, adsorbate_indices, normal)
    
    def _optimize_normal_rotation(self, system, adsorbate_indices, normal):
        """
        Optimize rotation around surface normal
        
        Args:
            system: ASE Atoms object
            adsorbate_indices: Indices of adsorbate atoms
            normal: Surface normal vector
            
        Returns:
            Tuple of (optimized_system, info_dict)
        """
        if normal is None:
            raise ValueError("Surface normal required for normal rotation method")
        
        self.log_info("Optimizing rotation around surface normal...")
        
        rotation_center = system[adsorbate_indices].get_center_of_mass()
        
        # Define energy function for rotation
        def energy_func(angle_deg):
            rotated = self._get_rotated_system_normal(
                angle_deg, system, adsorbate_indices, rotation_center, normal
            )
            rotated.calc = self.calculator
            return rotated.get_potential_energy()
        
        # Optimize rotation angle
        result = minimize_scalar(energy_func, bounds=(0, 360), method='bounded')
        
        # Get final optimized system
        optimized_system = self._get_rotated_system_normal(
            result.x, system, adsorbate_indices, rotation_center, normal
        )
        
        info = {
            'method': 'normal',
            'optimal_angle': result.x,
            'energy': result.fun
        }
        
        self.log_info(f"Optimal rotation angle: {result.x:.2f}°")
        return optimized_system, info
    
    def _optimize_sphere_rotation(self, system, adsorbate_indices):
        """
        Optimize rotation using spherical sampling
        
        Args:
            system: ASE Atoms object
            adsorbate_indices: Indices of adsorbate atoms
            
        Returns:
            Tuple of (optimized_system, info_dict)
        """
        self.log_info("Optimizing rotation using spherical sampling...")
        
        rotation_axes = self._generate_uniform_rotations(self.rotation_count)
        best_energy = float('inf')
        best_system = None
        best_axis = None
        best_angle = None
        
        adsorbate_com = system[adsorbate_indices].get_center_of_mass()
        
        for axis_dir in rotation_axes:
            axis_dir = axis_dir / np.linalg.norm(axis_dir)
            
            for angle in np.arange(0, 360, self.rotation_step):
                rot = Rotation.from_rotvec(np.radians(angle) * axis_dir)
                
                trial_system = self._get_rotated_system(
                    rot, system, adsorbate_indices, adsorbate_com
                )
                trial_system.calc = self.calculator
                energy = trial_system.get_potential_energy()
                
                if energy < best_energy:
                    best_energy = energy
                    best_system = trial_system
                    best_axis = axis_dir
                    best_angle = angle
        
        if best_system is None:
            raise RuntimeError("All rotations failed")
        
        info = {
            'method': 'sphere',
            'optimal_axis': best_axis.tolist() if best_axis is not None else None,
            'optimal_angle': best_angle,
            'energy': best_energy
        }
        
        self.log_info(f"Optimal rotation - Axis: {best_axis}, Angle: {best_angle}°")
        return best_system, info
    
    def _get_rotated_system_normal(self, angle_deg, system, adsorbate_indices, 
                                   center, axis):
        """
        Rotate system around surface normal
        
        Args:
            angle_deg: Rotation angle in degrees
            system: ASE Atoms object
            adsorbate_indices: Indices of adsorbate atoms
            center: Center of rotation
            axis: Rotation axis
            
        Returns:
            Rotated system
        """
        rotated_system = system.copy()
        adsorbate_part = system[adsorbate_indices]
        adsorbate_part.rotate(angle_deg, v=axis, center=center)
        rotated_system.positions[adsorbate_indices] = adsorbate_part.positions
        return rotated_system
    
    def _get_rotated_system(self, rotation_obj, system, adsorbate_indices, center):
        """
        Apply rotation object to system
        
        Args:
            rotation_obj: scipy Rotation object
            system: ASE Atoms object
            adsorbate_indices: Indices of adsorbate atoms
            center: Center of rotation
            
        Returns:
            Rotated system
        """
        rotated_system = system.copy()
        adsorbate_part = rotated_system[adsorbate_indices]
        
        pos = adsorbate_part.get_positions()
        translated = pos - center
        rotated = rotation_obj.apply(translated) + center
        adsorbate_part.set_positions(rotated)
        
        rotated_system.positions[adsorbate_indices] = adsorbate_part.positions
        return rotated_system
    
    def _generate_uniform_rotations(self, num_rotations):
        """
        Generate uniformly distributed rotation axes using Fibonacci sphere
        
        Args:
            num_rotations: Number of rotation axes to generate
            
        Returns:
            Array of rotation axis vectors
        """
        indices = np.arange(0, num_rotations, dtype=float) + 0.5
        phi = np.arccos(1 - 2 * indices / num_rotations)
        theta = np.pi * (1 + 5**0.5) * indices
        
        directions = np.stack([
            np.sin(phi) * np.cos(theta),
            np.sin(phi) * np.sin(theta),
            np.cos(phi)
        ], axis=-1)
        
        return directions
