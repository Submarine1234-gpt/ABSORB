"""
Main workflow orchestrator for surface adsorption calculations
"""
import os
import json
import numpy as np
import ase.io
from ase.constraints import FixAtoms

from .calculators import CalculatorFactory
from .site_finder import HollowSiteFinder, OnTopSiteFinder
from .optimizers import RotationOptimizer
from utils import get_session_logger, plot_adsorption_site, plot_energy_distribution


class SurfaceAdsorptionWorkflow:
    """
    Orchestrates the complete surface adsorption calculation workflow
    """
    
    def __init__(self, **kwargs):
        """
        Initialize workflow with parameters
        
        Args:
            **kwargs: Configuration parameters including:
                - output_folder: Output directory path
                - surface_axis: Surface axis (0, 1, or 2)
                - place_on_bottom: Place on bottom surface
                - adsorption_height: Height above surface
                - vacuum_thickness: Vacuum layer thickness
                - surface_search_depth: Depth to search for surface atoms
                - collision_threshold: Minimum distance threshold
                - hollow_sites_enabled: Enable hollow site detection
                - on_top_sites_enabled: Enable on-top site detection
                - knn_neighbors: KNN neighbors for hollow sites
                - hollow_site_deduplication_distance: Deduplication distance
                - on_top_target_atom: Target atom for on-top sites
                - rotation_count: Number of rotations for sphere method
                - rotation_step: Rotation step in degrees
                - rotation_method: Rotation method ('normal' or 'sphere')
        """
        # Extract and store all parameters
        self.output_folder = kwargs.get('output_folder', 'adsorption_results')
        self.surface_axis = int(kwargs.get('surface_axis', 2))
        self.place_on_bottom = bool(kwargs.get('place_on_bottom', False))
        self.adsorption_height = float(kwargs.get('adsorption_height', 2.0))
        self.vacuum_thickness = float(kwargs.get('vacuum_thickness', 20.0))
        self.surface_search_depth = float(kwargs.get('surface_search_depth', 3.5))
        self.collision_threshold = float(kwargs.get('collision_threshold', 1.2))
        
        # Site finder parameters
        self.hollow_sites_enabled = bool(kwargs.get('hollow_sites_enabled', True))
        self.knn_neighbors = int(kwargs.get('knn_neighbors', 2))
        self.hollow_site_deduplication_distance = float(
            kwargs.get('hollow_site_deduplication_distance', 1.5)
        )
        
        self.on_top_sites_enabled = bool(kwargs.get('on_top_sites_enabled', True))
        self.on_top_target_atom = str(kwargs.get('on_top_target_atom', 'O'))
        
        # Rotation parameters
        self.rotation_count = int(kwargs.get('rotation_count', 50))
        self.rotation_step = float(kwargs.get('rotation_step', 30))
        
        # Handle rotation_method - accept both boolean (legacy) and string values
        # Validate and set rotation method with explicit logging
        rotation_method_param = kwargs.get('rotation_method', 'normal')
        if isinstance(rotation_method_param, bool):
            # Legacy boolean support: True = sphere, False = normal
            self.rotation_method = 'sphere' if rotation_method_param else 'normal'
        elif isinstance(rotation_method_param, str):
            # String support: must be 'normal' or 'sphere'
            if rotation_method_param.lower() in ['normal', 'sphere']:
                self.rotation_method = rotation_method_param.lower()
            else:
                # Invalid value, default to 'normal'
                self.rotation_method = 'normal'
        else:
            # Invalid type, default to 'normal'
            self.rotation_method = 'normal'
        
        # Create output folder
        os.makedirs(self.output_folder, exist_ok=True)
        
        # Set up logger
        session_id = kwargs.get('session_id', 'workflow')
        self.logger = get_session_logger(session_id, self.output_folder)
        self.logger.info(f"Workflow initialized with parameters: {kwargs}")
        self.logger.info(f"Rotation method selected: {self.rotation_method.upper()}")
    
    def run(self, substrate_path, adsorbate_path):
        """
        Execute the complete workflow
        
        Args:
            substrate_path: Path to substrate CIF file
            adsorbate_path: Path to adsorbate CIF file
        """
        try:
            # Load structures
            substrate, adsorbate = self._load_structures(substrate_path, adsorbate_path)
            
            # Build surface slab
            surface_slab = self._build_surface_slab(substrate)
            
            # Calculate reference energies
            chgnet_calc = CalculatorFactory.create_calculator('chgnet')
            e_slab = self._calculate_energy(surface_slab, chgnet_calc, "Surface slab")
            e_adsorbate = self._calculate_energy(adsorbate, chgnet_calc, "Adsorbate")
            
            # Find surface atoms
            surface_atoms_coords, surface_atoms_indices = self._find_surface_atoms(surface_slab)
            
            if surface_atoms_coords.size == 0:
                self.logger.warning("No surface atoms found, exiting calculation")
                return
            
            # Find adsorption sites
            adsorption_sites = self._find_adsorption_sites(
                surface_slab, surface_atoms_coords, surface_atoms_indices
            )
            
            if not adsorption_sites:
                self.logger.warning("No valid adsorption sites found, exiting calculation")
                return
            
            # Optimize adsorbate at each site
            optimized_results = self._place_and_optimize_adsorbate(
                surface_slab, adsorbate, adsorption_sites, e_slab, e_adsorbate
            )
            
            # Generate outputs
            if optimized_results:
                self._create_visualization_data(surface_slab, optimized_results)
                self._save_summary(optimized_results)
                
                # Generate energy distribution plot
                energy_plot_path = os.path.join(self.output_folder, '04_energy_distribution.png')
                plot_energy_distribution(optimized_results, energy_plot_path, self.logger)
            else:
                self.logger.warning("No sites successfully optimized")
            
            self.logger.info("Calculation finished successfully")
            
        except Exception as e:
            self.logger.error(f"Workflow failed with error: {e}", exc_info=True)
            raise
    
    def _load_structures(self, substrate_path, adsorbate_path):
        """Load substrate and adsorbate structures"""
        self.logger.info("Loading structure files...")
        substrate = ase.io.read(substrate_path, format='cif')
        adsorbate = ase.io.read(adsorbate_path, format='cif')
        self.logger.info(
            f"Loaded: Substrate={substrate.get_chemical_formula()}, "
            f"Adsorbate={adsorbate.get_chemical_formula()}"
        )
        return substrate, adsorbate
    
    def _build_surface_slab(self, substrate):
        """Build surface slab with vacuum"""
        self.logger.info("Building surface slab model...")
        slab = substrate.copy()
        slab.set_pbc(True)
        slab.center(vacuum=self.vacuum_thickness, axis=self.surface_axis)
        
        pbc = [True, True, True]
        pbc[self.surface_axis] = False
        slab.set_pbc(pbc)
        
        self.logger.info(f"Slab built. PBC: {slab.get_pbc()}, Cell: {np.diag(slab.cell)}")
        
        # Save slab structure
        ase.io.write(os.path.join(self.output_folder, '01_built_surface.cif'), slab)
        return slab
    
    def _calculate_energy(self, atoms, calculator, name):
        """Calculate energy of atoms object"""
        atoms_copy = atoms.copy()
        atoms_copy.calc = calculator
        energy = atoms_copy.get_potential_energy()
        self.logger.info(f"{name} energy: {energy:.4f} eV")
        return energy
    
    def _find_surface_atoms(self, slab):
        """Find surface atoms based on position"""
        placement = "bottom" if self.place_on_bottom else "top"
        self.logger.info(f"Finding {placement} surface atoms...")
        
        positions = slab.get_positions()
        coords_on_axis = positions[:, self.surface_axis]
        
        if self.place_on_bottom:
            surface_level = np.min(coords_on_axis)
            mask = (coords_on_axis <= surface_level + self.surface_search_depth)
        else:
            surface_level = np.max(coords_on_axis)
            mask = (coords_on_axis >= surface_level - self.surface_search_depth)
        
        surface_atoms_indices = np.where(mask)[0]
        surface_atoms_coords = positions[surface_atoms_indices]
        
        self.logger.info(f"Found {len(surface_atoms_coords)} {placement} surface atoms")
        
        # Save surface atoms for visualization
        with open(os.path.join(self.output_folder, 'surface_atoms.json'), 'w') as f:
            json.dump({'coords': surface_atoms_coords.tolist()}, f)
        
        return surface_atoms_coords, surface_atoms_indices
    
    def _find_adsorption_sites(self, slab, surface_atoms_coords, surface_atoms_indices):
        """Find all adsorption sites"""
        all_sites = []
        
        # Find hollow sites
        if self.hollow_sites_enabled:
            hollow_finder = HollowSiteFinder(
                knn_neighbors=self.knn_neighbors,
                deduplication_distance=self.hollow_site_deduplication_distance,
                surface_axis=self.surface_axis,
                place_on_bottom=self.place_on_bottom,
                logger=self.logger
            )
            hollow_sites = hollow_finder.find_sites(surface_atoms_coords)
            all_sites.extend(hollow_sites)
        
        # Find on-top sites
        if self.on_top_sites_enabled:
            ontop_finder = OnTopSiteFinder(
                target_atom=self.on_top_target_atom,
                surface_axis=self.surface_axis,
                place_on_bottom=self.place_on_bottom,
                logger=self.logger
            )
            ontop_sites = ontop_finder.find_sites(
                surface_atoms_coords, surface_atoms_indices, slab
            )
            all_sites.extend(ontop_sites)
        
        self.logger.info(f"Total adsorption sites found: {len(all_sites)}")
        return all_sites
    
    def _place_and_optimize_adsorbate(self, slab, adsorbate, sites, e_slab, e_adsorbate):
        """Place and optimize adsorbate at each site"""
        self.logger.info(f"Starting optimization at {len(sites)} sites...")
        self.logger.info(f"Using rotation method: {self.rotation_method.upper()}")
        
        if self.rotation_method == 'sphere':
            self.logger.info(f"  - Spherical sampling with {self.rotation_count} rotation axes")
            self.logger.info(f"  - Rotation step: {self.rotation_step}° per axis")
        else:
            self.logger.info(f"  - Normal rotation around surface normal vector")
        
        results = []
        skipped = 0
        
        # Create calculators
        chgnet_calc = CalculatorFactory.create_calculator('chgnet')
        lj_calc = CalculatorFactory.create_calculator('lj')
        
        # Create rotation optimizer
        rotation_optimizer = RotationOptimizer(
            calculator=lj_calc,
            rotation_method=self.rotation_method,
            rotation_count=self.rotation_count,
            rotation_step=self.rotation_step,
            logger=self.logger
        )
        
        for i, site_data in enumerate(sites):
            site_pos = site_data['site']
            site_normal = site_data['normal']
            site_type = site_data.get('type', 'Unknown')
            
            self.logger.info(f"--- Processing site {i+1}/{len(sites)} ({site_type}) ---")
            
            # Place adsorbate at site
            target_pos = site_pos + site_normal * self.adsorption_height
            self.logger.info(f"Target position: {target_pos}")
            
            placed_adsorbate = self._place_adsorbate(adsorbate, target_pos)
            
            # Create combined system
            system = slab.copy()
            system.extend(placed_adsorbate)
            adsorbate_indices = list(range(len(slab), len(system)))
            
            # Fix slab atoms
            system.constraints = FixAtoms(indices=range(len(slab)))
            
            # Optimize rotation
            try:
                optimized_system, opt_info = rotation_optimizer.optimize(
                    system, adsorbate_indices, normal=site_normal
                )
                
                # Check for collisions
                min_dist = self._get_minimum_distance(
                    optimized_system, adsorbate_indices, len(slab)
                )
                
                if min_dist < self.collision_threshold:
                    self.logger.warning(
                        f"Site {i+1} has collision (min distance: {min_dist:.2f} Å), skipping"
                    )
                    skipped += 1
                    continue
                
                # Calculate final energy with CHGNet
                optimized_system.calc = chgnet_calc
                e_total = optimized_system.get_potential_energy()
                adsorption_energy = e_total - (e_slab + e_adsorbate)
                
                # Remove calculator and constraints for saving
                optimized_system.calc = None
                optimized_system.constraints = []
                
                self.logger.info(
                    f"Site {i+1} optimized. Adsorption energy: {adsorption_energy:.4f} eV, "
                    f"Min distance: {min_dist:.2f} Å"
                )
                
                # Save structure
                filename = f"02_adsorbed_site_{i+1}_{site_type}.cif"
                ase.io.write(os.path.join(self.output_folder, filename), optimized_system)
                
                # Store result
                result_info = {
                    'system': optimized_system,
                    'adsorption_energy': adsorption_energy,
                    'site_type': site_type,
                    'surface_site_coordinates': site_pos.tolist(),
                    'adsorbate_com_coordinates': optimized_system[adsorbate_indices].get_center_of_mass().tolist(),
                    'site_index': i + 1,
                    'optimization_info': opt_info
                }
                results.append(result_info)
                
                # Generate plot for this site
                plot_filename = f"03_plot_site_{i+1}_{site_type}.png"
                plot_path = os.path.join(self.output_folder, plot_filename)
                plot_adsorption_site(
                    optimized_system, 
                    adsorbate_indices, 
                    result_info, 
                    plot_path, 
                    self.logger
                )
                
            except Exception as e:
                self.logger.error(f"Site {i+1} optimization failed: {e}")
                skipped += 1
                continue
        
        self.logger.info(f"Optimization complete. Success: {len(results)}, Skipped: {skipped}")
        return results
    
    def _place_adsorbate(self, adsorbate, target_position):
        """Place adsorbate at target position"""
        placed = adsorbate.copy()
        current_com = placed.get_center_of_mass()
        translation = target_position - current_com
        placed.translate(translation)
        return placed
    
    def _get_minimum_distance(self, system, adsorbate_indices, num_slab_atoms):
        """Get minimum distance between adsorbate and slab"""
        dist_matrix = system.get_all_distances(mic=True)
        return np.min(dist_matrix[np.ix_(adsorbate_indices, range(num_slab_atoms))])
    
    def _create_visualization_data(self, slab, results):
        """Create JSON data for frontend visualization"""
        self.logger.info("Creating visualization data...")
        
        # Create adsorption sites data with correct structure for frontend
        sites_data = {
            'cell': slab.cell.tolist(),
            'sites': []
        }
        
        for result in results:
            sites_data['sites'].append({
                'position': result['surface_site_coordinates'],  # Frontend expects 'position'
                'energy': float(round(result['adsorption_energy'], 4)),
                'type': result['site_type']  # Include site type for frontend display
            })
        
        # Save adsorption sites data
        sites_filename = os.path.join(self.output_folder, 'adsorption_sites.json')
        with open(sites_filename, 'w', encoding='utf-8') as f:
            json.dump(sites_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Adsorption sites data saved to {sites_filename}")
        
        # Note: surface_atoms.json is already generated in _find_surface_atoms method
        # surface_mesh.json is generated on-demand by the backend API endpoint
    
    def _save_summary(self, results):
        """Save calculation summary"""
        self.logger.info("--- Final Results Summary (sorted by stability) ---")
        
        sorted_results = sorted(results, key=lambda x: x['adsorption_energy'])
        
        # Create final visualization with all sites
        first_result = sorted_results[0]
        final_system = first_result['system'][:len(first_result['system']) - len(first_result['system'][:])]
        
        # Reconstruct slab from first result (it contains slab + adsorbate)
        num_slab_atoms = len(first_result['system']) - len(
            [i for i in range(len(first_result['system'])) 
             if i in range(len(first_result['system']))]
        )
        
        # Save individual summaries
        for result in sorted_results:
            self.logger.info(
                f"Site {result['site_index']} ({result['site_type']}): "
                f"Adsorption energy = {result['adsorption_energy']:.4f} eV"
            )
