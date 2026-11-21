# tqdm_pandas 

[![Monthly downloads](https://img.shields.io/pypi/dm/tqdm-pandas?style=for-the-badge&logo=pypi&logoColor=white&label=Downloads%2Fmonth&labelColor=1e293b&color=14b8a6)](https://pypistats.org/packages/tqdm-pandas)
[![PyPI version](https://img.shields.io/pypi/v/tqdm-pandas?style=for-the-badge&logo=python&logoColor=white&labelColor=1e293b&color=3b82f6)](https://pypi.org/project/tqdm-pandas/)

Track large pandas file reads with a progress bar, so you can see your data loading.


## Installation

```
pip install tqdm-pandas
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
### Reading Excel sheets

Install `openpyxl` to read `.xlsx` workbooks:

```bash
pip install openpyxl
```

Use `sheet_name` to read a specific sheet, selected sheets, or every sheet:

```python
import pandas as pd
from tqdm_pandas import patch_pandas, unpatch_pandas

patch_pandas()
try:
    # One sheet returns a DataFrame (replace these names with your sheet names).
    sales = pd.read_excel('report.xlsx', sheet_name='Sales')

    # A list of sheet names returns a dictionary of DataFrames.
    selected = pd.read_excel('report.xlsx', sheet_name=['Sales', 'Expenses'])
    expenses = selected['Expenses']

    # None reads every sheet into a dictionary keyed by sheet name.
    all_sheets = pd.read_excel('report.xlsx', sheet_name=None)
    for name, frame in all_sheets.items():
        print(f'{name}: {len(frame)} rows')
finally:
    unpatch_pandas()
```

The progress bar tracks bytes read from the workbook, rather than sheets completed.

## Contributing 
Contributions are welcome! Please feel free to submit a pull request or open an issue if you find a bug or have a feature request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author   
Ishaan Jolly
