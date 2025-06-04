# tqdm_pandas 

This package aims to end put some certainity into reading large files with pandas 
by adding a progress bar to the process. 


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

# Read a large Excel file with a progress bar
df = pd.read_excel('XXX.xlsx')

# Read a large JSON file with a progress bar
df = pd.read_json('XXX.json')

# Read a large Parquet file with a progress bar
df = pd.read_parquet('XXX.parquet')

# Unpatch pandas to remove progress bar functionality       
unpatch_pandas()

```
## Contributing 
Contributions are welcome! Please feel free to submit a pull request or open an issue if you find a bug or have a feature request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author   
Ishaan Jolly
