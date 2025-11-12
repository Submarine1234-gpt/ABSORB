"""
Calculator factory for creating different types of calculators
Supports CHGNet and LennardJones calculators
"""
from chgnet.model import CHGNetCalculator
from ase.calculators.lj import LennardJones


class CalculatorFactory:
    """
    Factory class for creating ASE calculators
    """
    
    _calculators = {
        'chgnet': CHGNetCalculator,
        'lennard_jones': LennardJones,
        'lj': LennardJones
    }
    
    @classmethod
    def create_calculator(cls, calculator_type='chgnet', **kwargs):
        """
        Create a calculator instance
        
        Args:
            calculator_type: Type of calculator ('chgnet', 'lennard_jones', 'lj')
            **kwargs: Additional arguments for calculator initialization
            
        Returns:
            Calculator instance
            
        Raises:
            ValueError: If calculator type is not supported
        """
        calculator_type = calculator_type.lower()
        
        if calculator_type not in cls._calculators:
            raise ValueError(
                f"Unknown calculator type: {calculator_type}. "
                f"Supported types: {list(cls._calculators.keys())}"
            )
        
        calculator_class = cls._calculators[calculator_type]
        return calculator_class(**kwargs)
    
    @classmethod
    def register_calculator(cls, name, calculator_class):
        """
        Register a new calculator type
        
        Args:
            name: Name for the calculator
            calculator_class: Calculator class
        """
        cls._calculators[name.lower()] = calculator_class
    
    @classmethod
    def get_available_calculators(cls):
        """
        Get list of available calculator types
        
        Returns:
            List of calculator names
        """
        return list(cls._calculators.keys())
