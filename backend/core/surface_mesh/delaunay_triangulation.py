"""
Delaunay Triangulation Module
Implements 2D Delaunay triangulation for surface mesh generation
"""

import numpy as np
from scipy.spatial import Delaunay


class DelaunayTriangulator:
    """
    Performs Delaunay triangulation on surface atom positions
    """
    
    def __init__(self):
        """Initialize the Delaunay triangulator"""
        self.triangulation = None
        
    def triangulate_2d(self, points):
        """
        Perform 2D Delaunay triangulation on surface points
        
        Args:
            points (np.ndarray): Nx2 array of 2D surface coordinates (x, y)
            
        Returns:
            np.ndarray: Mx3 array of triangle indices
        """
        if len(points) < 3:
            raise ValueError("Need at least 3 points for triangulation")
        
        # Perform Delaunay triangulation
        self.triangulation = Delaunay(points)
        
        return self.triangulation.simplices
    
    def triangulate_surface(self, surface_atoms, projection_axis=2):
        """
        Triangulate surface atoms by projecting to 2D plane
        
        Args:
            surface_atoms (np.ndarray): Nx3 array of 3D surface coordinates
            projection_axis (int): Axis to project out (0=x, 1=y, 2=z)
            
        Returns:
            tuple: (triangles, projected_points)
                - triangles: Mx3 array of triangle indices
                - projected_points: Nx2 array of 2D projected points
        """
        # Get axes for 2D projection
        axes = [0, 1, 2]
        axes.remove(projection_axis)
        
        # Project to 2D
        projected_points = surface_atoms[:, axes]
        
        # Perform triangulation
        triangles = self.triangulate_2d(projected_points)
        
        return triangles, projected_points
    
    def filter_large_triangles(self, triangles, vertices, max_edge_length):
        """
        Filter out triangles with edges longer than max_edge_length
        
        Args:
            triangles (np.ndarray): Mx3 array of triangle indices
            vertices (np.ndarray): Nx3 array of vertex coordinates
            max_edge_length (float): Maximum allowed edge length
            
        Returns:
            np.ndarray: Filtered triangle array
        """
        filtered_triangles = []
        
        for triangle in triangles:
            # Get triangle vertices
            v0 = vertices[triangle[0]]
            v1 = vertices[triangle[1]]
            v2 = vertices[triangle[2]]
            
            # Calculate edge lengths
            edge1 = np.linalg.norm(v1 - v0)
            edge2 = np.linalg.norm(v2 - v1)
            edge3 = np.linalg.norm(v0 - v2)
            
            # Keep triangle if all edges are within threshold
            if max(edge1, edge2, edge3) <= max_edge_length:
                filtered_triangles.append(triangle)
        
        return np.array(filtered_triangles)
    
    def get_triangle_neighbors(self):
        """
        Get neighboring triangles for each triangle
        
        Returns:
            np.ndarray: Mx3 array where each row contains indices of neighboring triangles
        """
        if self.triangulation is None:
            raise ValueError("Must perform triangulation first")
        
        return self.triangulation.neighbors
    
    def get_triangle_centroids(self, triangles, vertices):
        """
        Calculate centroids of all triangles
        
        Args:
            triangles (np.ndarray): Mx3 array of triangle indices
            vertices (np.ndarray): Nx3 array of vertex coordinates
            
        Returns:
            np.ndarray: Mx3 array of triangle centroids
        """
        centroids = []
        
        for triangle in triangles:
            v0 = vertices[triangle[0]]
            v1 = vertices[triangle[1]]
            v2 = vertices[triangle[2]]
            
            centroid = (v0 + v1 + v2) / 3.0
            centroids.append(centroid)
        
        return np.array(centroids)
