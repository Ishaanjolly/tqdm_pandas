import os
import pandas as pd
from tqdm import tqdm

def _get_file_size(file):
    """Get file size if possible."""
    try:
        if isinstance(file, str) and os.path.isfile(file):
            return os.path.getsize(file)
        elif hasattr(file, 'seek') and hasattr(file, 'tell'):
            current_pos = file.tell()
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(current_pos)
            return size
    except (OSError, IOError, AttributeError):
        pass
    return None

class TqdmFileReader:
    """File-like wrapper with progress bar."""
    
    def __init__(self, file, desc=None):
        self.file = file
        self.file_size = _get_file_size(file)
        self.pbar = tqdm(
            total=self.file_size,
            unit='B',
            unit_scale=True,
            desc=desc or "Reading"
        )
        
    def __enter__(self):
        return self
        
    def __exit__(self, *args):
        self.pbar.close()
        
    def read(self, size=-1):
        data = self.file.read(size)
        self.pbar.update(len(data))
        return data
        
    def readline(self, size=-1):
        data = self.file.readline(size)
        self.pbar.update(len(data))
        return data
        
    def __iter__(self):
        for line in self.file:
            self.pbar.update(len(line))
            yield line

def _wrap_file(file, desc=None):
    """Wrap file or path with progress bar."""
    if isinstance(file, str):
        return TqdmFileReader(open(file, 'rb'), desc=desc)
    elif hasattr(file, 'read'):
        return TqdmFileReader(file, desc=desc)
    return file


def create_progress_readers(original_functions):
    """Create progress-enabled readers that use the original pandas functions."""
    
    def read_csv_with_progress(source, desc=None, **kwargs):
        with _wrap_file(source, desc=desc or "Reading CSV") as f:
            return original_functions['read_csv'](f, **kwargs)

    def read_json_with_progress(source, desc=None, **kwargs):
        with _wrap_file(source, desc=desc or "Reading JSON") as f:
            return original_functions['read_json'](f, **kwargs)

    def read_table_with_progress(source, desc=None, **kwargs):
        with _wrap_file(source, desc=desc or "Reading Table") as f:
            return original_functions['read_table'](f, **kwargs)
        
    def read_excel_with_progress(source, desc=None, **kwargs):
        with _wrap_file(source, desc=desc or "Reading Excel") as f:
            return original_functions['read_excel'](f, **kwargs)
        
    def read_parquet_with_progress(source, desc=None, **kwargs):
        if isinstance(source, str):
            file_size = _get_file_size(source)
            if file_size:
                with tqdm(total=file_size, unit='B', unit_scale=True, desc=desc or "Reading Parquet") as pbar:
                    result = original_functions['read_parquet'](source, **kwargs)
                    pbar.update(file_size)  # Complete the bar
                    return result
            else:
                return original_functions['read_parquet'](source, **kwargs)
        else:
            return original_functions['read_parquet'](source, **kwargs)
    
    return {
        'read_csv': read_csv_with_progress,
        'read_json': read_json_with_progress,
        'read_table': read_table_with_progress,
        'read_excel': read_excel_with_progress,
        'read_parquet': read_parquet_with_progress,
    }

    