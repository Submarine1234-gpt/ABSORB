# ABSORB Frontend Components Documentation

## Overview

The ABSORB frontend has been completely redesigned with Element Plus UI framework and modern visualization capabilities including 3D surface triangle mesh rendering.

## Technology Stack

- **Vue 3**: Progressive JavaScript framework
- **Element Plus 2.4.2**: Professional UI component library
- **Vite 4**: Fast build tool and dev server
- **Three.js 0.158**: 3D WebGL rendering for mesh visualization
- **Plotly.js**: Interactive 2D/3D plotting
- **TypeScript**: Type-safe development

## Component Architecture

### Main Components

#### App.vue
Main application container with Element Plus layout.

**Features:**
- `el-container` layout structure
- Dark mode toggle support
- Responsive design
- Professional header/footer

**Usage:**
```vue
<template>
  <el-container class="app-container">
    <el-header>...</el-header>
    <el-main>...</el-main>
    <el-footer>...</el-footer>
  </el-container>
</template>
```

#### Dashboard.vue
Main dashboard with calculation progress and visualization.

**Features:**
- `el-row`/`el-col` responsive grid layout
- `el-card` for content sections
- `el-progress` for calculation status
- `el-alert` for status messages
- Real-time log streaming

**Key Methods:**
- `handleCalculationStarted()`: Initialize new calculation
- `startLogStreaming()`: Stream calculation logs via SSE
- `loadResults()`: Fetch calculation history

#### CalculationForm.vue
Calculation parameters input form with file upload.

**Features:**
- `el-form` with validation
- `el-upload` drag-and-drop file upload
- `el-collapse` for parameter grouping
- `el-slider` for numeric parameters
- `el-select` for dropdown options
- `el-checkbox` for boolean toggles

**Collapsible Sections:**
1. **Input Files**: Substrate and adsorbate CIF files
2. **Basic Parameters**: Surface axis, heights, thresholds
3. **Site Detection**: Hollow and on-top site options
4. **Rotation Optimization**: Spherical sampling settings

**Usage Example:**
```vue
<CalculationForm 
  :is-running="isCalculationRunning"
  @calculation-started="handleCalculationStarted"
/>
```

#### VisualizationChart.vue
Multi-view visualization with tabbed interface.

**Features:**
- `el-tabs` for multiple visualization modes
- `el-skeleton` loading states
- Three tabs: Scatter Plot, Heat Map, Surface Mesh

**Tabs:**
1. **Scatter Plot**: 3D scatter visualization with Plotly
2. **Heat Map**: 2D energy projection
3. **Surface Mesh**: 3D triangle mesh with Three.js

**Props:**
- `sessionId`: Current calculation session
- `displayOptions`: Visualization display settings

#### SurfaceMeshViewer.vue
3D triangle mesh viewer using Three.js.

**Features:**
- WebGL-based 3D rendering
- OrbitControls for 360° rotation
- Energy-based color mapping
- Wireframe/solid display modes
- Interactive camera controls

**Color Scheme:**
- Green: Low energy (favorable adsorption)
- Yellow: Medium energy
- Red: High energy (unfavorable adsorption)

**Technical Details:**
- Uses `BufferGeometry` for efficient rendering
- Vertex colors for energy visualization
- Automatic camera positioning
- Grid and axis helpers

**Props:**
- `sessionId`: Session identifier
- `meshOptions`: Display configuration
  - `wireframe`: Display mode (boolean)
  - `opacity`: Mesh transparency (0.1-1.0)
  - `colorScheme`: Color mapping scheme

#### MeshControls.vue
Control panel for mesh visualization settings.

**Features:**
- Display mode toggle (solid/wireframe)
- Opacity slider
- Color scheme selector
- Responsive controls with `el-form`

**Events:**
- `update-options`: Emits mesh option changes

#### ResultHistory.vue
Historical calculation results table.

**Features:**
- `el-table` with sorting and pagination
- `el-pagination` for large datasets
- `el-tag` for status indicators
- `el-button-group` for actions
- View and download options

**Actions:**
- View: Load historical result
- Download: Get result ZIP file

#### ChartControls.vue
Display options for chart visualization.

**Features:**
- `el-checkbox` bordered controls
- Surface atoms visibility toggle
- Adsorption sites visibility toggle
- Energy-based coloring toggle

## Backend API Integration

### New Endpoints

#### GET /api/visualization/{session_id}/surface_mesh.json
Retrieve surface mesh data for 3D visualization.

**Response:**
```json
{
  "vertices": [[x, y, z], ...],
  "triangles": [[i, j, k], ...],
  "energies": [e1, e2, ...],
  "colors": ["#00ff00", ...],
  "metadata": {
    "vertex_count": 150,
    "triangle_count": 250,
    "energy_range": {
      "min": -3.2,
      "max": 1.5,
      "mean": -1.8
    }
  }
}
```

#### POST /api/mesh/generate
Generate surface mesh for a session.

**Request:**
```json
{
  "session_id": "uuid",
  "surface_axis": 2,
  "max_edge_length": 10.0
}
```

**Response:**
```json
{
  "success": true,
  "message": "Mesh generated successfully",
  "mesh_stats": {
    "vertices": 150,
    "triangles": 250
  }
}
```

## Surface Mesh Module

### Backend Components

#### DelaunayTriangulator
Performs 2D Delaunay triangulation on surface points.

**Methods:**
- `triangulate_2d()`: 2D triangulation
- `triangulate_surface()`: 3D surface triangulation with projection
- `filter_large_triangles()`: Remove elongated triangles
- `get_triangle_centroids()`: Calculate triangle centers

#### EnergyInterpolator
Interpolates adsorption energies across mesh vertices.

**Methods:**
- `interpolate_to_vertices()`: Linear/nearest/cubic interpolation
- `smooth_energies()`: Laplacian smoothing
- `normalize_energies()`: Scale to range
- `get_energy_gradient()`: Calculate energy gradients

#### MeshDataProcessor
Processes and formats mesh data for visualization.

**Methods:**
- `generate_color_map()`: Energy to color conversion
- `prepare_mesh_data()`: Format for JSON export
- `save_mesh_to_json()`: Write to file
- `calculate_mesh_quality_metrics()`: Mesh statistics

#### TriangleMeshGenerator
Main interface for mesh generation.

**Usage:**
```python
from backend.core.surface_mesh import TriangleMeshGenerator

generator = TriangleMeshGenerator(
    surface_atoms,
    adsorption_sites,
    surface_axis=2
)

mesh_data = generator.generate_mesh(
    max_edge_length=10.0,
    smooth_iterations=1
)

generator.save_mesh('output.json')
```

## Building and Running

### Install Dependencies
```bash
cd frontend
npm install
```

### Development Server
```bash
npm run dev
```

### Production Build
```bash
npm run build
```

### Build Output
- `dist/`: Production build directory
- `dist/index.html`: Entry point
- `dist/assets/`: CSS and JS bundles

## Configuration

### Auto-Import Setup
The project uses `unplugin-auto-import` and `unplugin-vue-components` for automatic Element Plus component imports.

**Benefits:**
- No manual component registration
- Smaller bundle size
- Better development experience

**Generated Files:**
- `auto-imports.d.ts`: Auto-import type definitions
- `components.d.ts`: Component type definitions

### TypeScript Configuration
- `tsconfig.json`: Main TypeScript config
- `tsconfig.node.json`: Node-specific config

## Styling

### Element Plus Theme
- Primary color: `#409EFF` (Element Plus blue)
- Success color: `#67C23A`
- Warning color: `#E6A23C`
- Danger color: `#F56C6C`

### Responsive Breakpoints
- `xs`: < 768px (mobile)
- `lg`: ≥ 992px (desktop)

### Dark Mode
Implemented with localStorage persistence and toggle in header.

## Browser Compatibility

- Modern browsers with WebGL support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance Considerations

### Large Meshes
- Mesh optimization for >1000 triangles
- Triangle filtering by edge length
- Vertex decimation (future enhancement)

### Rendering
- WebGL hardware acceleration
- Efficient BufferGeometry usage
- Lazy loading of Three.js components

## Troubleshooting

### Build Issues
**Problem:** Missing dependencies
```bash
npm install
```

**Problem:** TypeScript errors
```bash
npm run build -- --skipLibCheck
```

### Runtime Issues
**Problem:** Mesh not displaying
- Check browser WebGL support
- Verify mesh data format
- Check console for errors

**Problem:** Slow rendering
- Reduce mesh complexity
- Lower opacity for better performance
- Use wireframe mode

## Future Enhancements

1. **Mesh Decimation**: Advanced mesh simplification algorithms
2. **Export Options**: STL, OBJ, PLY format support
3. **Advanced Coloring**: Custom color schemes and gradients
4. **Measurement Tools**: Distance and angle measurements
5. **Animation**: Rotation and energy evolution animations
6. **VR Support**: WebXR for immersive visualization

## Contributing

When adding new components:
1. Use Element Plus components first
2. Follow Vue 3 Composition API or Options API consistently
3. Add TypeScript types where beneficial
4. Document props, events, and methods
5. Include usage examples

## License

Copyright © 2024 ABSORB Platform
