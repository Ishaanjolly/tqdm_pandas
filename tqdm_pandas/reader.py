import os
import pandas as pd
from tqdm import tqdm
import io
import threading
import time

def _get_file_size(file):
    """Get file size if possible."""
    try:
        if hasattr(file, 'seek') and hasattr(file, 'tell'):
            pos = file.tell()
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(pos)
            return size
        elif isinstance(file, str) and os.path.isfile(file):
            return os.path.getsize(file)
    except (IOError, OSError):
        pass
    return None

class TqdmFileReader:
    """A file-like wrapper with a progress bar."""
    
    def __init__(self, file, desc=None, total=None):
        self.file = file
        self.file_size = total or _get_file_size(file)
        self.progress = 0
        self.desc = desc or "Reading"
        
        # Start with empty tqdm bar
        self.pbar = tqdm(
            total=self.file_size,
            unit='B',
            unit_scale=True,
            desc=self.desc
        )
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pbar.close()
        
    def read(self, size=-1):
        data = self.file.read(size)
        data_len = len(data)
        self.progress += data_len
        self.pbar.update(data_len)
        return data
        
    def readline(self, size=-1):
        data = self.file.readline(size)
        data_len = len(data)
        self.progress += data_len
        self.pbar.update(data_len)
        return data
        
    def __iter__(self):
        return self
        
    def __next__(self):
        line = self.readline()
        if not line:
            raise StopIteration
        return line
        
    def seekable(self):
        return self.file.seekable()
        
    def seek(self, offset, whence=0):
        self.file.seek(offset, whence)
        if whence == 0:
            self.progress = offset
        elif whence == 1:
            self.progress += offset
        elif whence == 2 and self.file_size:
            self.progress = self.file_size + offset
        self.pbar.update(0)  # Refresh the progress bar
        
    def tell(self):
        return self.file.tell()

def _is_file_like(obj):
    """Check if an object is file-like."""
    return hasattr(obj, 'read') and hasattr(obj, 'seek')

def _wrap_file(file, desc=None):
    """Wrap a file or filename with TqdmFileReader."""
    if isinstance(file, str):
        return TqdmFileReader(open(file, 'rb'), desc=desc, total=_get_file_size(file))
    elif _is_file_like(file):
        return TqdmFileReader(file, desc=desc, total=_get_file_size(file))
    return file

def read_csv(filepath_or_buffer, desc=None, **kwargs):
    """Read a CSV file with a progress bar."""
    with _wrap_file(filepath_or_buffer, desc=desc or "Reading CSV") as f:
        return pd.read_csv(f, **kwargs)

def read_excel(io, desc=None, **kwargs):
    """Read an Excel file with a progress bar."""
    # Excel files are handled differently since pandas uses openpyxl/xlrd
    # We can't easily wrap the file object, so we'll use a simpler approach
    if isinstance(io, str):
        size = _get_file_size(io)
        pbar = tqdm(total=100, desc=desc or "Reading Excel", unit="%")
        
        # Use a thread to update progress since we can't intercept reads
        def update_pbar():
            for i in range(100):
                time.sleep(0.01)  # Adjust based on expected file size
                pbar.update(1)
                if pbar.n >= 100:
                    break
        
        thread = threading.Thread(target=update_pbar)
        thread.daemon = True
        thread.start()
        
        try:
            df = pd.read_excel(io, **kwargs)
            pbar.n = 100  # Ensure bar completes
            pbar.refresh()
            return df
        finally:
            pbar.close()
    else:
        # Can't reliably show progress for file-like objects with Excel
        return pd.read_excel(io, **kwargs)

def read_json(path_or_buf, desc=None, **kwargs):
    """Read a JSON file with a progress bar."""
    with _wrap_file(path_or_buf, desc=desc or "Reading JSON") as f:
        return pd.read_json(f, **kwargs)

def read_parquet(path, desc=None, **kwargs):
    """Read a Parquet file with a progress bar."""
    # Parquet uses PyArrow/fastparquet under the hood, which makes wrapping more complex
    if isinstance(path, str):
        pbar = tqdm(total=100, desc=desc or "Reading Parquet", unit="%")
        try:
            df = pd.read_parquet(path, **kwargs)
            pbar.n = 100
            pbar.refresh()
            return df
        finally:
            pbar.close()
    else:
        return pd.read_parquet(path, **kwargs)

def read_sql(sql, con, desc=None, **kwargs):
    """Read a SQL query or database table with a progress bar."""
    pbar = tqdm(total=100, desc=desc or "Reading SQL", unit="%")
    try:
        df = pd.read_sql(sql, con, **kwargs)
        pbar.n = 100
        pbar.refresh()
        return df
    finally:
        pbar.close()

def read_table(filepath_or_buffer, desc=None, **kwargs):
    """Read a general delimited file with a progress bar."""
    with _wrap_file(filepath_or_buffer, desc=desc or "Reading Table") as f:
        return pd.read_table(f, **kwargs)