"""
Base class for adsorption site finders
"""
import numpy as np
from abc import ABC, abstractmethod


class BaseSiteFinder(ABC):
    """
    Abstract base class for finding adsorption sites on surfaces
    """
    
    def __init__(self, surface_axis=2, place_on_bottom=False, logger=None):
        """
        Initialize site finder
        
        Args:
            surface_axis: Axis perpendicular to surface (0, 1, or 2)
            place_on_bottom: Whether to place on bottom surface
            logger: Logger instance
        """
        self.surface_axis = surface_axis
        self.place_on_bottom = place_on_bottom
        self.logger = logger
    
    @abstractmethod
    def find_sites(self, surface_atoms_coords, surface_atoms_indices, slab=None):
        """
        Find adsorption sites
        
        Args:
            surface_atoms_coords: Coordinates of surface atoms
            surface_atoms_indices: Indices of surface atoms
            slab: ASE Atoms object (optional, needed for some finders)
            
        Returns:
            List of site dictionaries with keys:
                - 'site': numpy array of site coordinates
                - 'normal': numpy array of surface normal
                - 'type': string describing site type
        """
        pass
    
    def get_surface_normal(self):
        """
        Get the surface normal vector
        
        Returns:
            Surface normal as numpy array
        """
        normal = np.zeros(3)
        normal[self.surface_axis] = -1.0 if self.place_on_bottom else 1.0
        return normal
    
    def log_info(self, message):
        """Log info message if logger available"""
        if self.logger:
            self.logger.info(message)
    
    def log_warning(self, message):
        """Log warning message if logger available"""
        if self.logger:
            self.logger.warning(message)
