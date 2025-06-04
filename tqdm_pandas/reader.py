import os
from tqdm import tqdm

def _get_file_size(file):
    """
    Get file size if possible

    Attempts to determine the size of a file object or file path
    Supports both file paths (strings) and file-like objects with seek/tell methods

    Parameters
    ----------
    file : str or file-like object
        File path as a string or file-like object with seek and tell methods

    Returns
    -------
    int or None
        File size in bytes if determinable, None otherwise

    Notes
    -----
    For file paths, uses os.path.getsize(). For file-like objects, uses
    seek/tell to determine size while preserving the current file position.
    Returns None if size cannot be determined due to errors or unsupported
    file types
    """
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
    """
    File-like wrapper with progress bar

    A wrapper class that adds a tqdm progress bar to file reading operations.
    Supports standard file operations like read(), readline(), and iteration
    while displaying progress based on bytes read

    Parameters
    ----------
    file : file-like object
        The file object to wrap with progress tracking.
    desc : str, optional
        Description text to display with the progress bar. Default is "Reading"

    """
    
    def __init__(self, file:object, desc:str=None):
        self.file = file
        self.file_size = _get_file_size(file)
        self.pbar = tqdm(
            total=self.file_size,
            unit='B',
            unit_scale=True,
            desc=desc or "Reading"
        )
        
    def __enter__(self):
        """context manager entry method"""
        return self
        
    def __exit__(self, *args):
        """Close progress bar on exit"""
        self.pbar.close()
        
    def read(self, size: int=-1):
        """
        Read and return up to size bytes from the file

        Parameters
        ----------
        size : int, optional
            Number of bytes to read. If -1 or omitted, read entire file

        Returns
        -------
        bytes or str
            Data read from the file
        """
        data = self.file.read(size)
        self.pbar.update(len(data))
        return data
        
    def readline(self, size:int=-1):
        """
        Read and return one line from the file.

        Parameters
        ----------
        size : int, optional
            Maximum number of bytes to read. If -1 or omitted, read entire line

        Returns
        -------
        bytes or str
            One line from the file
        """
        data = self.file.readline(size)
        self.pbar.update(len(data))
        return data
        
    def __iter__(self):
        """
        Iterate over lines in the file

        Yields
        ------
        bytes or str
            Each line in the file
        """
        for line in self.file:
            self.pbar.update(len(line))
            yield line

def _wrap_file(file:object, desc:str=None):
    """
    Wrap file or path with progress bar

    Creates a TqdmFileReader wrapper for file objects or opens files from paths
    with progress tracking enabled.

    Parameters
    ----------
    file : str or file-like object
        File path as string or existing file-like object to wrap
    desc : str, optional
        Description for the progress bar

    Returns
    -------
    TqdmFileReader or original file
        Wrapped file with progress tracking, or original file if wrapping
        is not applicable
    """
    if isinstance(file, str):
        return TqdmFileReader(open(file, 'rb'), desc=desc)
    elif hasattr(file, 'read'):
        return TqdmFileReader(file, desc=desc)
    return file


def create_progress_readers(original_functions:dict) -> dict:
    """Create progress-enabled readers that use the original pandas functions."""
    
    def read_csv_with_progress(source:str, desc:str=None, **kwargs):
        """
        Read csv file with progress bar
        
        Parameters
        ----------
        source : file path
        desc : str, optional
            Progress bar description. Default is "Reading JSON"
        **kwargs
            Additional arguments passed to pandas.read_json()
            
        Returns
        -------
        pandas.DataFrame
            Parsed csv data
        """
        with _wrap_file(source, desc=desc or "Reading CSV") as f:
            return original_functions['read_csv'](f, **kwargs)

    def read_json_with_progress(source: str, desc:str =None, **kwargs):
        """
        Read JSON file with progress bar
        
        Parameters
        ----------
        source : File path or file-like object to read.
        desc : str, optional
            Progress bar description. Default is "Reading JSON"
        **kwargs
            Additional arguments passed to pandas.read_json()
            
        Returns
        -------
        pandas.DataFrame
            Parsed JSON data
        """
        with _wrap_file(source, desc=desc or "Reading JSON") as f:
            return original_functions['read_json'](f, **kwargs)

    def read_table_with_progress(source, desc=None, **kwargs):
        """
        Read table file with progress bar
        
        Parameters
        ----------
        source : File path or file-like object to read.
        desc : str, optional
            Progress bar description. Default is "Reading JSON"
        **kwargs
            Additional arguments passed to pandas.read_json()
            
        Returns
        -------
        pandas.DataFrame
            Parsed table data
        """
        with _wrap_file(source, desc=desc or "Reading Table") as f:
            return original_functions['read_table'](f, **kwargs)
        
    def read_excel_with_progress(source:str, desc:str=None, **kwargs):
        """
        Read Excel file with progress bar
        
        Parameters
        ----------
        source : File path or file-like object to read
        desc : str, optional
            Progress bar description. Default is "Reading JSON".
        **kwargs
            Additional arguments passed to pandas.read_json()
            
        Returns
        -------
        pandas.DataFrame
            Parsed Excel data
        """
        with _wrap_file(source, desc=desc or "Reading Excel") as f:
            return original_functions['read_excel'](f, **kwargs)
        
    def read_parquet_with_progress(source:str, desc=None, **kwargs):
        """Read Parquet file with progress bar.
        
        Parameters
        ----------
        source : str
            File path or file-like object to read.
        desc : str, optional
            Progress bar description. Default is "Reading Parquet"
        **kwargs
            Additional arguments passed to pandas.read_parquet()
            
        Returns
        -------
        pandas.DataFrame
            Parsed Parquet data
        """
        if isinstance(source, str):
            file_size = _get_file_size(source)
            if file_size:
                with tqdm(total=file_size, unit='B', unit_scale=True, desc=desc or "Reading Parquet") as pbar:
                    result = original_functions['read_parquet'](source, **kwargs)
                    pbar.update(file_size) 
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

    