# Data_Snapshot
Python utility that summarizes the contents of a CSV file. It provides:

- Per-column statistics (data type, counts, unique values, numeric stats, top frequent value).
- Null and empty string counts.
- Overall file metadata (row/column counts, rows with null/empty values).

This tool is useful for quick data profiling and quality checks.

## Features
- Interactive file selection with optional tab-completion (via prompt_toolkit if installed).
- Handles nulls and empty strings separately and combined.
- Provides numeric stats (mean, median, std, min, max) for numeric columns.
- Provides mode and frequency for non-numeric columns.

## Requirements
- Python 3.11+ (tested in a conda environment)
- Packages Argparse, Pandas

Optional: https://python-prompt-toolkit.readthedocs.io/ 

## Usage
Run the script from the command line:
```bash
python DataSnapshot.py [csv_path] [--output OUTPUT_PATH] [--nrows N]
```

csv_path (optional): Path to the input CSV file. If omitted, you’ll be prompted.
--output, -o: Path to save the per-column summary as CSV.
--nrows: Number of rows to read (useful for large files).

For better interactive experience, install prompt_toolkit:
```bash
pip install prompt_toolkit
```

## Examples
Summarize a CSV interactively:
```bash
python DataSnapshot.py
```

Summarize a CSV and save output:
```bash
python DataSnapshot.py data.csv --output summary.csv
```

Summarize first 1000 rows:
```bash
python DataSnapshot.py data.csv --nrows 1000
```


## Notes
