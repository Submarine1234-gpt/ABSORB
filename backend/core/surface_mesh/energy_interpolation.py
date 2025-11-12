"""
Energy Interpolation Module
Interpolates adsorption energies across the surface mesh
"""

import numpy as np
from scipy.interpolate import griddata, LinearNDInterpolator


class EnergyInterpolator:
    """
    Interpolates adsorption energies from site points to mesh vertices
    """
    
    def __init__(self):
        """Initialize the energy interpolator"""
        self.interpolator = None
        
    def interpolate_to_vertices(self, site_positions, site_energies, vertex_positions, method='linear'):
        """
        Interpolate energies from adsorption sites to mesh vertices
        
        Args:
            site_positions (np.ndarray): Nx2 or Nx3 array of site positions
            site_energies (np.ndarray): N array of energy values
            vertex_positions (np.ndarray): Mx2 or Mx3 array of vertex positions
            method (str): Interpolation method ('linear', 'nearest', 'cubic')
            
        Returns:
            np.ndarray: M array of interpolated energy values
        """
        # Ensure we have valid data
        if len(site_positions) < 3:
            raise ValueError("Need at least 3 sites for interpolation")
        
        # Handle 3D positions by projecting to 2D if needed
        if site_positions.shape[1] == 3:
            site_positions = site_positions[:, :2]
        if vertex_positions.shape[1] == 3:
            vertex_positions = vertex_positions[:, :2]
        
        # Perform interpolation
        interpolated = griddata(
            site_positions,
            site_energies,
            vertex_positions,
            method=method,
            fill_value=np.nan
        )
        
        # Handle NaN values using nearest neighbor interpolation
        if np.any(np.isnan(interpolated)):
            nearest = griddata(
                site_positions,
                site_energies,
                vertex_positions,
                method='nearest'
            )
            interpolated = np.where(np.isnan(interpolated), nearest, interpolated)
        
        return interpolated
    
    def create_linear_interpolator(self, site_positions, site_energies):
        """
        Create a reusable linear interpolator
        
        Args:
            site_positions (np.ndarray): Nx2 array of site positions
            site_energies (np.ndarray): N array of energy values
            
        Returns:
            LinearNDInterpolator: Interpolator object
        """
        self.interpolator = LinearNDInterpolator(site_positions, site_energies)
        return self.interpolator
    
    def interpolate_with_stored(self, vertex_positions):
        """
        Use stored interpolator to interpolate energies
        
        Args:
            vertex_positions (np.ndarray): Mx2 array of vertex positions
            
        Returns:
            np.ndarray: M array of interpolated energies
        """
        if self.interpolator is None:
            raise ValueError("Must create interpolator first")
        
        return self.interpolator(vertex_positions)
    
    def smooth_energies(self, energies, triangles, iterations=1):
        """
        Smooth energy values using Laplacian smoothing
        
        Args:
            energies (np.ndarray): N array of energy values at vertices
            triangles (np.ndarray): Mx3 array of triangle indices
            iterations (int): Number of smoothing iterations
            
        Returns:
            np.ndarray: Smoothed energy values
        """
        smoothed = energies.copy()
        n_vertices = len(energies)
        
        # Build adjacency information
        adjacency = [set() for _ in range(n_vertices)]
        for triangle in triangles:
            adjacency[triangle[0]].update([triangle[1], triangle[2]])
            adjacency[triangle[1]].update([triangle[0], triangle[2]])
            adjacency[triangle[2]].update([triangle[0], triangle[1]])
        
        # Perform smoothing iterations
        for _ in range(iterations):
            new_energies = smoothed.copy()
            
            for i in range(n_vertices):
                if len(adjacency[i]) > 0:
                    # Average with neighbors
                    neighbor_energies = [smoothed[j] for j in adjacency[i]]
                    new_energies[i] = (smoothed[i] + np.mean(neighbor_energies)) / 2.0
            
            smoothed = new_energies
        
        return smoothed
    
    def normalize_energies(self, energies, min_val=0.0, max_val=1.0):
        """
        Normalize energy values to a specified range
        
        Args:
            energies (np.ndarray): Energy values to normalize
            min_val (float): Minimum value of output range
            max_val (float): Maximum value of output range
            
        Returns:
            np.ndarray: Normalized energy values
        """
        e_min = np.min(energies)
        e_max = np.max(energies)
        
        if e_max == e_min:
            return np.full_like(energies, (min_val + max_val) / 2.0)
        
        # Normalize to [0, 1]
        normalized = (energies - e_min) / (e_max - e_min)
        
        # Scale to [min_val, max_val]
        return normalized * (max_val - min_val) + min_val
    
    def get_energy_gradient(self, energies, vertices, triangles):
        """
        Calculate energy gradients across triangles
        
        Args:
            energies (np.ndarray): Energy values at vertices
            vertices (np.ndarray): Nx3 array of vertex coordinates
            triangles (np.ndarray): Mx3 array of triangle indices
            
        Returns:
            np.ndarray: Mx3 array of gradient vectors
        """
        gradients = []
        
        for triangle in triangles:
            v0, v1, v2 = vertices[triangle]
            e0, e1, e2 = energies[triangle]
            
            # Calculate gradient using finite differences
            edge1 = v1 - v0
            edge2 = v2 - v0
            
            de1 = e1 - e0
            de2 = e2 - e0
            
            # Simple gradient approximation
            if np.linalg.norm(edge1) > 0 and np.linalg.norm(edge2) > 0:
                grad = (de1 * edge1 / np.linalg.norm(edge1)**2 + 
                       de2 * edge2 / np.linalg.norm(edge2)**2)
            else:
                grad = np.zeros(3)
            
            gradients.append(grad)
        
        return np.array(gradients)
