# tdqm_pandas: pandas progress reader

I've often found myself needing to read a large file with pandas and have been left frustated over 
how long it takes to read the file. This package provides a simple way to add a progress bar to the reading of files

## Installation

```
pip install tdqm_pandas
```
## Usage

```
import pandas as pd
from tqdm_pandas import patch_pandas, unpatch_pandas 

# Patch pandas to add progress bar functionality directly to the existing pandas functions
patch_pandas()
# Read a large CSV file with a progress bar
df = pd.read_csv('XXX.csv')
```

