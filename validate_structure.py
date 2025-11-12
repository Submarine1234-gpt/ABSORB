#!/usr/bin/env python3
"""
Validation script for ABSORB platform structure
Checks that all required files and modules are present
"""

import os
import sys

def check_file(path, description):
    """Check if a file exists"""
    exists = os.path.exists(path)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {path}")
    return exists

def check_directory(path, description):
    """Check if a directory exists"""
    exists = os.path.isdir(path)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {path}")
    return exists

def main():
    """Run validation checks"""
    print("=" * 60)
    print("ABSORB Platform Structure Validation")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Backend structure
    print("Backend Structure:")
    print("-" * 60)
    all_passed &= check_file("backend/app.py", "Main Flask app")
    all_passed &= check_file("backend/config.py", "Configuration")
    all_passed &= check_directory("backend/core", "Core module")
    all_passed &= check_file("backend/core/workflow.py", "Workflow orchestrator")
    all_passed &= check_directory("backend/core/calculators", "Calculators module")
    all_passed &= check_file("backend/core/calculators/calculator_factory.py", "Calculator factory")
    all_passed &= check_directory("backend/core/site_finder", "Site finders module")
    all_passed &= check_file("backend/core/site_finder/hollow_finder.py", "Hollow site finder")
    all_passed &= check_file("backend/core/site_finder/ontop_finder.py", "On-top site finder")
    all_passed &= check_directory("backend/core/optimizers", "Optimizers module")
    all_passed &= check_file("backend/core/optimizers/rotation_optimizer.py", "Rotation optimizer")
    all_passed &= check_directory("backend/services", "Services module")
    all_passed &= check_file("backend/services/calculation_service.py", "Calculation service")
    all_passed &= check_file("backend/services/file_service.py", "File service")
    all_passed &= check_file("backend/services/session_service.py", "Session service")
    all_passed &= check_directory("backend/utils", "Utils module")
    all_passed &= check_file("backend/utils/logger.py", "Logger utility")
    all_passed &= check_file("backend/utils/validators.py", "Validators utility")
    all_passed &= check_file("backend/templates/index.html", "Backend template")
    print()
    
    # Frontend structure
    print("Frontend Structure:")
    print("-" * 60)
    all_passed &= check_file("frontend/package.json", "Package configuration")
    all_passed &= check_file("frontend/vite.config.js", "Vite configuration")
    all_passed &= check_file("frontend/src/main.js", "Main entry point")
    all_passed &= check_file("frontend/src/App.vue", "Root component")
    all_passed &= check_directory("frontend/src/components", "Components directory")
    all_passed &= check_file("frontend/src/components/Dashboard.vue", "Dashboard component")
    all_passed &= check_file("frontend/src/components/CalculationForm.vue", "Calculation form")
    all_passed &= check_file("frontend/src/components/ChartControls.vue", "Chart controls")
    all_passed &= check_file("frontend/src/components/VisualizationChart.vue", "Visualization chart")
    all_passed &= check_file("frontend/src/components/ResultHistory.vue", "Result history")
    all_passed &= check_directory("frontend/src/services", "Services directory")
    all_passed &= check_file("frontend/src/services/api.js", "API service")
    all_passed &= check_directory("frontend/src/utils", "Utils directory")
    all_passed &= check_file("frontend/src/utils/constants.js", "Constants")
    print()
    
    # Configuration files
    print("Configuration & Documentation:")
    print("-" * 60)
    all_passed &= check_file("requirements.txt", "Python requirements")
    all_passed &= check_file("README.md", "Documentation")
    all_passed &= check_file("start.sh", "Linux/Mac startup script")
    all_passed &= check_file("start.bat", "Windows startup script")
    all_passed &= check_file(".gitignore", "Git ignore file")
    print()
    
    # Summary
    print("=" * 60)
    if all_passed:
        print("✓ All validation checks passed!")
        print("The ABSORB platform structure is complete.")
        return 0
    else:
        print("✗ Some validation checks failed.")
        print("Please review the missing files/directories above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
