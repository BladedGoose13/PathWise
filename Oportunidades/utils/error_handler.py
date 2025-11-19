from typing import Callable, Any, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorHandler:
    @staticmethod
    def with_fallback(primary_func: Callable, 
                     fallback_funcs: List[Callable], 
                     *args, **kwargs) -> Any:
        """
        Try primary function, fall back to alternatives if it fails
        
        Args:
            primary_func: Main function to try
            fallback_funcs: List of fallback functions to try in order
            *args, **kwargs: Arguments to pass to all functions
        """
        # Try primary function
        try:
            result = primary_func(*args, **kwargs)
            if result:
                return result
        except Exception as e:
            logger.warning(f"Primary function failed: {e}")
        
        # Try fallback functions
        for fallback in fallback_funcs:
            try:
                result = fallback(*args, **kwargs)
                if result:
                    logger.info(f"Fallback successful: {fallback.__name__}")
                    return result
            except Exception as e:
                logger.warning(f"Fallback {fallback.__name__} failed: {e}")
        
        # All failed
        logger.error("All functions failed, returning None")
        return None
    
    @staticmethod
    def safe_api_call(func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        Safely call an API function and return structured result
        
        Returns:
            Dict with 'success', 'data', and 'error' keys
        """
        try:
            data = func(*args, **kwargs)
            return {
                'success': True,
                'data': data,
                'error': None
            }
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return {
                'success': False,
                'data': None,
                'error': str(e)
            }
