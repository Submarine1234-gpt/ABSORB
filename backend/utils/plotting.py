"""
Plotting utilities for generating visualization plots of adsorption sites
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def plot_adsorption_site(system, adsorbate_indices, site_info, output_path, logger=None):
    """
    Generate a 3D visualization plot for an individual adsorption site
    
    Args:
        system: ASE Atoms object containing the full system (slab + adsorbate)
        adsorbate_indices: List of indices for adsorbate atoms
        site_info: Dictionary containing site information (energy, type, index, etc.)
        output_path: Path where the plot image should be saved
        logger: Optional logger for logging messages
    """
    try:
        # Extract information
        site_type = site_info.get('site_type', 'Unknown')
        site_index = site_info.get('site_index', 0)
        adsorption_energy = site_info.get('adsorption_energy', 0.0)
        
        # Get coordinates
        positions = system.get_positions()
        slab_indices = [i for i in range(len(system)) if i not in adsorbate_indices]
        
        slab_pos = positions[slab_indices]
        adsorbate_pos = positions[adsorbate_indices]
        
        # Create figure
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot slab atoms
        ax.scatter(slab_pos[:, 0], slab_pos[:, 1], slab_pos[:, 2],
                  c='gray', marker='o', s=20, alpha=0.5, label='Substrate')
        
        # Plot adsorbate atoms
        ax.scatter(adsorbate_pos[:, 0], adsorbate_pos[:, 1], adsorbate_pos[:, 2],
                  c='red', marker='o', s=100, alpha=0.9, label='Adsorbate')
        
        # Set labels and title
        ax.set_xlabel('X (Å)')
        ax.set_ylabel('Y (Å)')
        ax.set_zlabel('Z (Å)')
        
        title = f'Site {site_index} ({site_type})\nAdsorption Energy: {adsorption_energy:.4f} eV'
        ax.set_title(title, fontsize=12, fontweight='bold')
        
        # Add legend
        ax.legend(loc='upper right')
        
        # Set viewing angle for better visualization
        ax.view_init(elev=20, azim=45)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        if logger:
            logger.info(f"Plot saved to {output_path}")
        
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"Failed to generate plot: {e}", exc_info=True)
        return False


def plot_energy_distribution(results, output_path, logger=None):
    """
    Generate a plot showing the distribution of adsorption energies across all sites
    
    Args:
        results: List of result dictionaries containing adsorption site information
        output_path: Path where the plot image should be saved
        logger: Optional logger for logging messages
    """
    try:
        if not results:
            if logger:
                logger.warning("No results to plot energy distribution")
            return False
        
        # Extract data
        site_indices = [r['site_index'] for r in results]
        energies = [r['adsorption_energy'] for r in results]
        site_types = [r['site_type'] for r in results]
        
        # Create color map based on site types
        unique_types = list(set(site_types))
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_types)))
        type_colors = {t: colors[i] for i, t in enumerate(unique_types)}
        point_colors = [type_colors[t] for t in site_types]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot bars
        bars = ax.bar(range(len(site_indices)), energies, color=point_colors, alpha=0.7)
        
        # Customize plot
        ax.set_xlabel('Site Index', fontsize=12)
        ax.set_ylabel('Adsorption Energy (eV)', fontsize=12)
        ax.set_title('Adsorption Energy Distribution Across Sites', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(site_indices)))
        ax.set_xticklabels(site_indices)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add horizontal line at y=0
        ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        
        # Add legend for site types
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=type_colors[t], label=t, alpha=0.7) 
                          for t in unique_types]
        ax.legend(handles=legend_elements, loc='best', title='Site Type')
        
        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        if logger:
            logger.info(f"Energy distribution plot saved to {output_path}")
        
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"Failed to generate energy distribution plot: {e}", exc_info=True)
        return False
