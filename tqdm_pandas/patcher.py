
import pandas as pd
from tqdm_pandas.reader import (
    read_csv_with_progress,
    read_excel_with_progress,
    read_json_with_progress,
    read_table_with_progress,
)
import logging 
logger = logging.getLogger(__name__)


_original_functions = {}

def patch_pandas():
    """
    Monkey patch pandas read functions to include progress bars.
    This allows users to continue using pd.read_csv() while getting
    progress bars automatically.
    """
    
    if _original_functions:
        logger.warning("pandas is already patched with tqdm progress bars")
        return False
    
    # Store original functions and replace with patched versions
    _original_functions = {
        "read_csv": pd.read_csv,
        "read_excel": pd.read_excel,
        "read_json": pd.read_json,
        "read_parquet": pd.read_parquet,
        "read_sql": pd.read_sql,
        "read_table": pd.read_table,
    }
    
    # Replace with tqdm-enabled versions
    pd.read_csv = read_csv_with_progress
    pd.read_excel = read_excel_with_progress
    pd.read_json = read_json_with_progress
    pd.read_table = read_table_with_progress
    
    return True

def unpatch_pandas():
    """
    Restore original pandas read functions without progress bars.
    """
    
    if not _original_functions:
        logger.warning("pandas is not currently patched by tqdm_pandas")
        return False
    
    # Restore original functions
    pd.read_csv = _original_functions["read_csv"]
    pd.read_excel = _original_functions["read_excel"]
    pd.read_json = _original_functions["read_json"]
    pd.read_table = _original_functions["read_table"]
    
    # Clear the stored originals
    _original_functions.clear()
    
    return True
