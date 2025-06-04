
import pandas as pd
from tqdm_pandas.reader import create_progress_readers
import logging 
logger = logging.getLogger(__name__)


_originals = {}

def patch_pandas() -> bool:
    """Add progress bars to pandas read functions."""
    if _originals:
        logger.warning("pandas is already patched with tqdm progress bars")
        return False  

    _originals.update({
        'read_csv': pd.read_csv,
        'read_excel': pd.read_excel, 
        'read_json': pd.read_json,
        'read_table': pd.read_table,
        'read_parquet': pd.read_parquet
    })
    
    progress_readers = create_progress_readers(_originals)
    
    pd.read_csv = progress_readers['read_csv']
    pd.read_excel = progress_readers['read_excel']
    pd.read_json = progress_readers['read_json']
    pd.read_table = progress_readers['read_table']
    pd.read_parquet = progress_readers['read_parquet']
    
    logger.info("pandas read functions patched with tqdm progress bars")
    
    return True

def unpatch_pandas() -> bool:
    """Restore original pandas read functions."""
    if not _originals:
        logger.warning("pandas is not currently patched by tqdm_pandas")
        return False 
    

    for name, func in _originals.items():
        setattr(pd, name, func)
    
    _originals.clear()
    logger.info("pandas read functions restored to original versions")
    return True