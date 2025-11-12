"""
Triangle Mesh Generator Module
Main interface for generating surface triangle meshes with energy interpolation
"""

import numpy as np
import os
import json

from .delaunay_triangulation import DelaunayTriangulator
from .energy_interpolation import EnergyInterpolator
from .mesh_data_processor import MeshDataProcessor


class TriangleMeshGenerator:
    """
    Main class for generating 3D triangle meshes from surface atoms and adsorption sites
    """
    
    def __init__(self, surface_atoms, adsorption_sites, surface_axis=2):
        """
        Initialize the triangle mesh generator
        
        Args:
            surface_atoms (np.ndarray): Nx3 array of surface atom coordinates
            adsorption_sites (list): List of adsorption site dictionaries
            surface_axis (int): Axis perpendicular to surface (0=x, 1=y, 2=z)
        """
        self.surface_atoms = np.array(surface_atoms)
        self.adsorption_sites = adsorption_sites
        self.surface_axis = surface_axis
        
        # Initialize components
        self.triangulator = DelaunayTriangulator()
        self.interpolator = EnergyInterpolator()
        self.processor = MeshDataProcessor()
        
        # Mesh data
        self.vertices = None
        self.triangles = None
        self.energies = None
        
    def generate_mesh(self, max_edge_length=None, smooth_iterations=1):
        """
        Generate the complete triangle mesh with energy interpolation
        
        Args:
            max_edge_length (float): Maximum allowed edge length for triangles
            smooth_iterations (int): Number of energy smoothing iterations
            
        Returns:
            dict: Mesh data dictionary
        """
        # Extract site positions and energies
        site_positions = np.array([site['position'] for site in self.adsorption_sites])
        site_energies = np.array([site.get('energy', 0.0) for site in self.adsorption_sites])
        
        # Use surface atoms as mesh vertices
        self.vertices = self.surface_atoms.copy()
        
        # Perform triangulation
        self.triangles, projected_points = self.triangulator.triangulate_surface(
            self.vertices,
            projection_axis=self.surface_axis
        )
        
        # Filter large triangles if specified
        if max_edge_length is not None:
            self.triangles = self.triangulator.filter_large_triangles(
                self.triangles,
                self.vertices,
                max_edge_length
            )
        
        # Interpolate energies to vertices
        vertex_positions_2d = projected_points
        site_positions_2d = self._project_to_2d(site_positions)
        
        self.energies = self.interpolator.interpolate_to_vertices(
            site_positions_2d,
            site_energies,
            vertex_positions_2d,
            method='linear'
        )
        
        # Smooth energies if requested
        if smooth_iterations > 0:
            self.energies = self.interpolator.smooth_energies(
                self.energies,
                self.triangles,
                iterations=smooth_iterations
            )
        
        # Prepare mesh data for export
        metadata = {
            'surface_axis': self.surface_axis,
            'num_sites': len(self.adsorption_sites),
            'num_surface_atoms': len(self.surface_atoms)
        }
        
        mesh_data = self.processor.prepare_mesh_data(
            self.vertices,
            self.triangles,
            self.energies,
            metadata=metadata
        )
        
        return mesh_data
    
    def _project_to_2d(self, points_3d):
        """
        Project 3D points to 2D by removing surface axis
        
        Args:
            points_3d (np.ndarray): Nx3 array of 3D coordinates
            
        Returns:
            np.ndarray: Nx2 array of 2D coordinates
        """
        axes = [0, 1, 2]
        axes.remove(self.surface_axis)
        return points_3d[:, axes]
    
    def save_mesh(self, output_path):
        """
        Save the generated mesh to a JSON file
        
        Args:
            output_path (str): Output file path
        """
        if self.vertices is None or self.triangles is None:
            raise ValueError("Must generate mesh before saving")
        
        mesh_data = self.processor.prepare_mesh_data(
            self.vertices,
            self.triangles,
            self.energies
        )
        
        self.processor.save_mesh_to_json(mesh_data, output_path)
    
    def get_mesh_statistics(self):
        """
        Get statistics about the generated mesh
        
        Returns:
            dict: Dictionary of mesh statistics
        """
        if self.vertices is None or self.triangles is None:
            return {}
        
        quality_metrics = self.processor.calculate_mesh_quality_metrics(
            self.vertices,
            self.triangles
        )
        
        return {
            'num_vertices': len(self.vertices),
            'num_triangles': len(self.triangles),
            'energy_range': {
                'min': float(np.min(self.energies)),
                'max': float(np.max(self.energies)),
                'mean': float(np.mean(self.energies))
            },
            **quality_metrics
        }


def generate_surface_mesh_from_results(result_dir, surface_axis=2):
    """
    Generate surface mesh from calculation results
    
    Args:
        result_dir (str): Directory containing calculation results
        surface_axis (int): Surface axis (0=x, 1=y, 2=z)
        
    Returns:
        dict: Mesh data dictionary or None if generation failed
    """
    try:
        # Load surface atoms
        surface_atoms_file = os.path.join(result_dir, 'surface_atoms.json')
        if not os.path.exists(surface_atoms_file):
            return None
        
        with open(surface_atoms_file, 'r') as f:
            surface_data = json.load(f)
        
        surface_atoms = surface_data.get('coords', [])
        
        # Load adsorption sites
        sites_file = os.path.join(result_dir, 'adsorption_sites.json')
        if not os.path.exists(sites_file):
            return None
        
        with open(sites_file, 'r') as f:
            sites_data = json.load(f)
        
        adsorption_sites = sites_data.get('sites', [])
        
        if len(surface_atoms) < 3 or len(adsorption_sites) < 3:
            return None
        
        # Generate mesh
        generator = TriangleMeshGenerator(
            surface_atoms,
            adsorption_sites,
            surface_axis=surface_axis
        )
        
        mesh_data = generator.generate_mesh(
            max_edge_length=10.0,  # Reasonable default
            smooth_iterations=1
        )
        
        # Save mesh data
        mesh_file = os.path.join(result_dir, 'surface_mesh.json')
        generator.save_mesh(mesh_file)
        
        return mesh_data
        
    except Exception as e:
        print(f"Failed to generate surface mesh: {e}")
        return None
