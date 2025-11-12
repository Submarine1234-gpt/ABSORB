"""
On-top site finder for specific atoms
"""
import numpy as np
from .base_finder import BaseSiteFinder


class OnTopSiteFinder(BaseSiteFinder):
    """
    Finds on-top adsorption sites on specific atoms
    """
    
    def __init__(self, target_atom='O', **kwargs):
        """
        Initialize on-top site finder
        
        Args:
            target_atom: Symbol of target atom for on-top sites
            **kwargs: Additional arguments passed to BaseSiteFinder
        """
        super().__init__(**kwargs)
        self.target_atom = target_atom
    
    def find_sites(self, surface_atoms_coords, surface_atoms_indices, slab):
        """
        Find on-top sites on specific atoms
        
        Args:
            surface_atoms_coords: Coordinates of surface atoms (not used directly)
            surface_atoms_indices: Indices of surface atoms in slab
            slab: ASE Atoms object containing the surface
            
        Returns:
            List of on-top site dictionaries
        """
        self.log_info(f"Finding on-top sites on '{self.target_atom}' atoms...")
        
        if slab is None:
            self.log_warning("Slab object required for on-top site finding")
            return []
        
        sites = []
        normal = self.get_surface_normal()
        
        for atom_index in surface_atoms_indices:
            atom = slab[atom_index]
            if atom.symbol == self.target_atom:
                sites.append({
                    'site': atom.position,
                    'normal': normal,
                    'type': 'On-Top'
                })
        
        self.log_info(f"Found {len(sites)} on-top sites on '{self.target_atom}' atoms")
        return sites
