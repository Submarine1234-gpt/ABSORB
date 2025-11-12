/**
 * Constants and configuration for frontend application
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || ''

export const SURFACE_AXES = [
  { value: 0, label: 'X-axis (0)' },
  { value: 1, label: 'Y-axis (1)' },
  { value: 2, label: 'Z-axis (2)' }
]

export const DEFAULT_PARAMS = {
  surface_axis: 2,
  place_on_bottom: false,
  adsorption_height: 2.0,
  vacuum_thickness: 20.0,
  surface_search_depth: 3.5,
  collision_threshold: 1.2,
  hollow_sites_enabled: true,
  knn_neighbors: 2,
  hollow_site_deduplication_distance: 1.5,
  on_top_sites_enabled: true,
  on_top_target_atom: 'O',
  rotation_count: 50,
  rotation_step: 30,
  rotation_method: false
}

export const PARAM_RANGES = {
  adsorption_height: { min: 0.1, max: 10.0, step: 0.1 },
  vacuum_thickness: { min: 5.0, max: 50.0, step: 1.0 },
  surface_search_depth: { min: 0.5, max: 10.0, step: 0.1 },
  collision_threshold: { min: 0.5, max: 3.0, step: 0.1 },
  knn_neighbors: { min: 1, max: 10, step: 1 },
  hollow_site_deduplication_distance: { min: 0.1, max: 5.0, step: 0.1 },
  rotation_count: { min: 10, max: 200, step: 10 },
  rotation_step: { min: 1, max: 90, step: 1 }
}

export const STATUS_MESSAGES = {
  idle: 'Ready to start calculation',
  uploading: 'Uploading files...',
  running: 'Calculation in progress...',
  complete: 'Calculation complete',
  error: 'An error occurred'
}

export const FILE_TYPES = {
  substrate: 'Substrate CIF file',
  adsorbate: 'Adsorbate CIF file'
}
