"""
Mesh Data Processor Module
Processes and formats mesh data for frontend visualization
"""

import numpy as np
import json


class MeshDataProcessor:
    """
    Processes mesh data for export and visualization
    """
    
    def __init__(self):
        """Initialize the mesh data processor"""
        pass
    
    def generate_color_map(self, energies, scheme='viridis'):
        """
        Generate color mapping for energy values
        
        Args:
            energies (np.ndarray): Energy values
            scheme (str): Color scheme ('viridis', 'hot', 'cool')
            
        Returns:
            list: List of hex color strings
        """
        # Normalize energies to [0, 1]
        if len(energies) == 0:
            return []
        
        e_min = np.min(energies)
        e_max = np.max(energies)
        
        if e_max == e_min:
            normalized = np.ones_like(energies) * 0.5
        else:
            normalized = (energies - e_min) / (e_max - e_min)
        
        # Generate colors based on scheme
        colors = []
        for value in normalized:
            if scheme == 'viridis':
                color = self._viridis_color(value)
            elif scheme == 'hot':
                color = self._hot_color(value)
            elif scheme == 'cool':
                color = self._cool_color(value)
            else:
                color = self._viridis_color(value)
            
            colors.append(color)
        
        return colors
    
    def _viridis_color(self, value):
        """
        Viridis-like color mapping (green -> yellow -> red for energy)
        Lower energy (favorable) = green, higher energy (unfavorable) = red
        
        Args:
            value (float): Normalized value in [0, 1]
            
        Returns:
            str: Hex color string
        """
        # Invert so low energy is green (favorable)
        value = 1.0 - value
        
        if value < 0.5:
            # Green to Yellow
            r = int(255 * (1 - value * 2))
            g = 255
            b = 0
        else:
            # Yellow to Red
            r = 255
            g = int(255 * (2 - value * 2))
            b = 0
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _hot_color(self, value):
        """
        Hot color mapping (red -> orange -> yellow)
        
        Args:
            value (float): Normalized value in [0, 1]
            
        Returns:
            str: Hex color string
        """
        if value < 0.33:
            # Black to Red
            r = int(255 * value / 0.33)
            g = 0
            b = 0
        elif value < 0.67:
            # Red to Yellow
            r = 255
            g = int(255 * (value - 0.33) / 0.34)
            b = 0
        else:
            # Yellow to White
            r = 255
            g = 255
            b = int(255 * (value - 0.67) / 0.33)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _cool_color(self, value):
        """
        Cool color mapping (blue -> cyan)
        
        Args:
            value (float): Normalized value in [0, 1]
            
        Returns:
            str: Hex color string
        """
        r = int(255 * value)
        g = 255
        b = 255 - int(255 * value)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def prepare_mesh_data(self, vertices, triangles, energies, metadata=None):
        """
        Prepare mesh data for JSON export
        
        Args:
            vertices (np.ndarray): Nx3 array of vertex coordinates
            triangles (np.ndarray): Mx3 array of triangle indices
            energies (np.ndarray): N array of energy values at vertices
            metadata (dict): Optional metadata dictionary
            
        Returns:
            dict: Mesh data dictionary ready for JSON export
        """
        # Convert numpy arrays to lists
        vertices_list = vertices.tolist()
        triangles_list = triangles.tolist()
        energies_list = energies.tolist()
        
        # Generate colors
        colors = self.generate_color_map(energies)
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            'vertex_count': len(vertices),
            'triangle_count': len(triangles),
            'energy_range': {
                'min': float(np.min(energies)),
                'max': float(np.max(energies)),
                'mean': float(np.mean(energies)),
                'std': float(np.std(energies))
            }
        })
        
        return {
            'vertices': vertices_list,
            'triangles': triangles_list,
            'energies': energies_list,
            'colors': colors,
            'metadata': metadata
        }
    
    def save_mesh_to_json(self, mesh_data, filepath):
        """
        Save mesh data to JSON file
        
        Args:
            mesh_data (dict): Mesh data dictionary
            filepath (str): Output file path
        """
        with open(filepath, 'w') as f:
            json.dump(mesh_data, f, indent=2)
    
    def optimize_mesh(self, vertices, triangles, energies, target_triangle_count=None):
        """
        Optimize mesh by reducing triangle count while preserving features
        
        Args:
            vertices (np.ndarray): Nx3 array of vertex coordinates
            triangles (np.ndarray): Mx3 array of triangle indices
            energies (np.ndarray): N array of energy values
            target_triangle_count (int): Target number of triangles
            
        Returns:
            tuple: (optimized_vertices, optimized_triangles, optimized_energies)
        """
        # Simple optimization: just return original if no target specified
        # In a production system, you would implement mesh decimation here
        if target_triangle_count is None or target_triangle_count >= len(triangles):
            return vertices, triangles, energies
        
        # For now, return original (placeholder for future optimization)
        return vertices, triangles, energies
    
    def calculate_mesh_quality_metrics(self, vertices, triangles):
        """
        Calculate quality metrics for the mesh
        
        Args:
            vertices (np.ndarray): Nx3 array of vertex coordinates
            triangles (np.ndarray): Mx3 array of triangle indices
            
        Returns:
            dict: Dictionary of quality metrics
        """
        areas = []
        aspect_ratios = []
        
        for triangle in triangles:
            v0 = vertices[triangle[0]]
            v1 = vertices[triangle[1]]
            v2 = vertices[triangle[2]]
            
            # Calculate area
            edge1 = v1 - v0
            edge2 = v2 - v0
            area = 0.5 * np.linalg.norm(np.cross(edge1, edge2))
            areas.append(area)
            
            # Calculate aspect ratio (longest edge / shortest edge)
            edge_lengths = [
                np.linalg.norm(v1 - v0),
                np.linalg.norm(v2 - v1),
                np.linalg.norm(v0 - v2)
            ]
            aspect_ratio = max(edge_lengths) / (min(edge_lengths) + 1e-10)
            aspect_ratios.append(aspect_ratio)
        
        return {
            'mean_area': float(np.mean(areas)),
            'total_area': float(np.sum(areas)),
            'mean_aspect_ratio': float(np.mean(aspect_ratios)),
            'max_aspect_ratio': float(np.max(aspect_ratios))
        }
