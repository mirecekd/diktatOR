"""
Modul pro retry/backoff logiku pro Gemini API volání
"""
import time
import functools
from typing import Callable, Any
import logging

# Nastavení loggeru
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 5,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0
):
    """
    Dekorátor pro retry s exponential backoff.
    
    Args:
        max_retries: Maximální počet pokusů (včetně prvního)
        initial_delay: Počáteční delay v sekundách
        backoff_factor: Násobitel pro exponential backoff
        max_delay: Maximální delay v sekundách
    
    Returns:
        Dekorovaná funkce s retry logikou
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(f"Attempt {attempt}/{max_retries} for {func.__name__}")
                    result = func(*args, **kwargs)
                    
                    if attempt > 1:
                        logger.info(f"{func.__name__} succeeded on attempt {attempt}")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"{func.__name__} failed after {max_retries} attempts: {str(e)}")
                        raise
                    
                    logger.warning(f"{func.__name__} failed on attempt {attempt}: {str(e)}")
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    
                    time.sleep(delay)
                    
                    # Exponential backoff
                    delay = min(delay * backoff_factor, max_delay)
            
            # Toto by nemělo nastat, ale pro jistotu
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator
