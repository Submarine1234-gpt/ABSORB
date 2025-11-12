# ABSORB - Surface Adsorption Calculation Platform

A comprehensive platform for automated surface adsorption site identification, geometry optimization, and adsorption energy calculation using machine learning potentials.

## Features

- 🎯 **Automatic Site Detection**: Identifies hollow and on-top adsorption sites
- 🔄 **Rotation Optimization**: Advanced algorithms for optimal adsorbate orientation
- ⚡ **ML Potential Calculations**: Fast adsorption energy calculations using CHGNet
- 📊 **Real-time Monitoring**: Live calculation logs via Server-Sent Events
- 🎨 **3D Visualization**: Interactive Plotly.js visualization of results
- 📁 **Result Management**: History tracking and downloadable result packages

## Architecture

```
ABSORB/
├── backend/                 # Flask backend application
│   ├── core/               # Core calculation logic
│   │   ├── calculators/    # Calculator factory (CHGNet, LJ)
│   │   ├── site_finder/    # Site detection algorithms
│   │   ├── optimizers/     # Rotation optimizers
│   │   └── workflow.py     # Main workflow orchestrator
│   ├── services/           # Service layer
│   │   ├── calculation_service.py
│   │   ├── file_service.py
│   │   └── session_service.py
│   ├── utils/              # Utilities
│   │   ├── logger.py
│   │   └── validators.py
│   ├── config.py           # Configuration
│   └── app.py              # Flask application
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── services/       # API service
│   │   └── utils/          # Frontend utilities
│   ├── package.json
│   └── vite.config.js
└── requirements.txt        # Python dependencies
```

## Technology Stack

### Backend
- **Framework**: Flask 2.3.3
- **Calculation Engine**: ASE 3.22.1 + CHGNet 0.3.0
- **Scientific Computing**: NumPy, SciPy
- **ML Framework**: PyTorch 2.0.1

### Frontend
- **Framework**: Vue.js 3
- **Build Tool**: Vite
- **Visualization**: Plotly.js
- **HTTP Client**: Axios

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+ and npm
- Git

### Backend Setup

```bash
# Clone the repository
git clone <repository-url>
cd ABSORB

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Build frontend for production
npm run build
```

## Usage

### Quick Start

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

This will start both the backend server (port 5000) and frontend dev server (port 3000).

### Manual Start

**Backend:**
```bash
cd backend
python app.py
```

**Frontend (Development):**
```bash
cd frontend
npm run dev
```

**Frontend (Production Build):**
```bash
cd frontend
npm run build
npm run preview
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Health Check**: http://localhost:5000/api/health

## Configuration

### Backend Configuration (`backend/config.py`)

```python
# Calculation parameters
DEFAULT_PARAMS = {
    'surface_axis': 2,              # 0=X, 1=Y, 2=Z
    'place_on_bottom': False,       # Place on bottom surface
    'adsorption_height': 2.0,       # Height above surface (Å)
    'vacuum_thickness': 20.0,       # Vacuum layer thickness (Å)
    'collision_threshold': 1.2,     # Min distance threshold (Å)
    'hollow_sites_enabled': True,   # Enable hollow sites
    'on_top_sites_enabled': True,   # Enable on-top sites
    'rotation_count': 50,           # Number of rotation samples
    'rotation_method': False        # Use spherical sampling
}
```

### Frontend Configuration (`frontend/vite.config.js`)

Proxy settings automatically forward API requests to the backend during development.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/run-calculation` | POST | Submit new calculation |
| `/check-status/<session_id>` | GET | Check calculation status |
| `/stream-logs/<session_id>` | GET | Stream calculation logs (SSE) |
| `/get-viz-data/<session_id>/<filename>` | GET | Get visualization data |
| `/get-results` | GET | Get all results |
| `/download-result/<session_id>` | GET | Download results ZIP |
| `/api/health` | GET | Health check |

## Workflow

1. **Upload Files**: Provide substrate and adsorbate CIF files
2. **Configure Parameters**: Set calculation parameters
3. **Submit Calculation**: Start background calculation
4. **Monitor Progress**: View real-time logs
5. **Visualize Results**: Interactive 3D visualization
6. **Download Results**: Get complete result package

## Development

### Code Organization

- **Factory Pattern**: Extensible calculator and optimizer factories
- **Service Layer**: Separation of concerns (calculation, file, session)
- **Modular Components**: Independent Vue components
- **Type Safety**: Parameter validation and error handling
- **Logging**: Comprehensive logging for debugging

### Adding New Calculators

```python
from backend.core.calculators import CalculatorFactory

# Register custom calculator
CalculatorFactory.register_calculator('my_calculator', MyCalculatorClass)
```

### Adding New Site Finders

```python
from backend.core.site_finder import BaseSiteFinder

class CustomSiteFinder(BaseSiteFinder):
    def find_sites(self, surface_atoms_coords, surface_atoms_indices, slab):
        # Implementation
        pass
```

## Troubleshooting

### Common Issues

**Issue**: CHGNet import error
**Solution**: Ensure PyTorch is installed correctly for your system

**Issue**: Frontend can't connect to backend
**Solution**: Check that backend is running on port 5000

**Issue**: File upload fails
**Solution**: Check file is in CIF format and < 16MB

### Logs

- **Backend logs**: `backend/logs/app.log`
- **Calculation logs**: `backend/user_uploads/results/<session_id>/calculation.log`

## Performance

- **Typical calculation time**: 2-10 minutes depending on system size
- **Memory usage**: ~2-4 GB for average systems
- **Concurrent calculations**: Supported via threading

## License

[Your License Here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- ASE (Atomic Simulation Environment)
- CHGNet machine learning potential
- Vue.js and Vite communities
- Plotly.js for visualization