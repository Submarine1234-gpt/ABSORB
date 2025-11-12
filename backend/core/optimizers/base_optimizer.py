"""
Base class for geometry optimizers
"""
import numpy as np
from abc import ABC, abstractmethod


class BaseOptimizer(ABC):
    """
    Abstract base class for adsorbate geometry optimization
    """
    
    def __init__(self, calculator, logger=None):
        """
        Initialize optimizer
        
        Args:
            calculator: ASE calculator instance
            logger: Logger instance
        """
        self.calculator = calculator
        self.logger = logger
    
    @abstractmethod
    def optimize(self, system, adsorbate_indices, **kwargs):
        """
        Optimize adsorbate geometry
        
        Args:
            system: ASE Atoms object containing surface and adsorbate
            adsorbate_indices: Indices of adsorbate atoms
            **kwargs: Additional optimization parameters
            
        Returns:
            Tuple of (optimized_system, optimization_info)
        """
        pass
    
    def log_info(self, message):
        """Log info message if logger available"""
        if self.logger:
            self.logger.info(message)
    
    def log_warning(self, message):
        """Log warning message if logger available"""
        if self.logger:
            self.logger.warning(message)
    
    def log_error(self, message):
        """Log error message if logger available"""
        if self.logger:
            self.logger.error(message)
