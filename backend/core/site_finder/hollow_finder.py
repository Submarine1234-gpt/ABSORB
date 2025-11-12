"""
Hollow site finder using KD-tree clustering
"""
import numpy as np
import scipy.spatial
from .base_finder import BaseSiteFinder


class HollowSiteFinder(BaseSiteFinder):
    """
    Finds hollow adsorption sites using KNN clustering
    """
    
    def __init__(self, knn_neighbors=2, deduplication_distance=1.5, **kwargs):
        """
        Initialize hollow site finder
        
        Args:
            knn_neighbors: Number of nearest neighbors for clustering
            deduplication_distance: Distance threshold for removing duplicate sites
            **kwargs: Additional arguments passed to BaseSiteFinder
        """
        super().__init__(**kwargs)
        self.knn_neighbors = knn_neighbors
        self.deduplication_distance = deduplication_distance
    
    def find_sites(self, surface_atoms_coords, surface_atoms_indices=None, slab=None):
        """
        Find hollow sites on the surface
        
        Args:
            surface_atoms_coords: Coordinates of surface atoms
            surface_atoms_indices: Indices of surface atoms (not used)
            slab: ASE Atoms object (not used)
            
        Returns:
            List of hollow site dictionaries
        """
        self.log_info("Finding hollow sites using KNN clustering...")
        
        if len(surface_atoms_coords) < self.knn_neighbors + 1:
            self.log_warning("Not enough surface atoms for hollow site detection")
            return []
        
        # Get 2D coordinates in the surface plane
        plane_axes = [i for i in range(3) if i != self.surface_axis]
        coords_2d = surface_atoms_coords[:, plane_axes]
        
        # Build KD-tree for efficient neighbor search
        kdtree = scipy.spatial.KDTree(coords_2d)
        
        # Find potential hollow sites
        potential_sites = []
        away_direction = self.get_surface_normal()
        
        _, indices_list = kdtree.query(coords_2d, k=self.knn_neighbors + 1)
        
        for i in range(len(surface_atoms_coords)):
            cluster_atoms = surface_atoms_coords[indices_list[i]]
            centroid = np.mean(cluster_atoms, axis=0)
            
            # Calculate surface normal from cluster geometry
            normal = self._calculate_cluster_normal(cluster_atoms, away_direction)
            
            potential_sites.append({
                'site': centroid,
                'normal': normal,
                'type': 'Hollow'
            })
        
        # Remove duplicate sites
        unique_sites = self._deduplicate_sites(potential_sites)
        
        self.log_info(f"Found {len(unique_sites)} unique hollow sites")
        return unique_sites
    
    def _calculate_cluster_normal(self, cluster_atoms, default_normal):
        """
        Calculate surface normal from cluster geometry
        
        Args:
            cluster_atoms: Array of cluster atom coordinates
            default_normal: Default normal vector
            
        Returns:
            Normalized surface normal
        """
        normal = default_normal.copy()
        
        if self.knn_neighbors >= 2 and len(cluster_atoms) > 2:
            v1, v2, v3 = cluster_atoms[0], cluster_atoms[1], cluster_atoms[2]
            cross_product = np.cross(v2 - v1, v3 - v1)
            norm_val = np.linalg.norm(cross_product)
            
            if norm_val > 1e-6:
                cross_product /= norm_val
                # Ensure normal points away from surface
                if np.dot(cross_product, default_normal) < 0:
                    cross_product = -cross_product
                normal = cross_product
        
        return normal
    
    def _deduplicate_sites(self, sites):
        """
        Remove duplicate sites based on distance threshold
        
        Args:
            sites: List of site dictionaries
            
        Returns:
            List of unique sites
        """
        if not sites:
            return []
        
        unique_sites = [sites[0]]
        
        for site in sites[1:]:
            is_duplicate = any(
                np.linalg.norm(site['site'] - unique['site']) < self.deduplication_distance
                for unique in unique_sites
            )
            if not is_duplicate:
                unique_sites.append(site)
        
        return unique_sites
