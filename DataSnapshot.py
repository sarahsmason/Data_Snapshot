# TimeSeriesExplorer.py
# Python utility that summarizes the contents of a CSV file. Script will prompt for source and return
#Per-column statistics (data type, counts, unique values, numeric stats, top frequent value).
#Null and empty string counts.
#Overall file metadata (row/column counts, rows with null/empty values).
# Author: Sarah Mason
# Date: 2026-01-04


import argparse
import pandas as pd
import os
from pathlib import Path

# Optional enhanced tab-completion: prefer prompt_toolkit if installed,
# otherwise try to enable readline-based filename completion where available.
try:
    from prompt_toolkit import prompt as pt_prompt
    from prompt_toolkit.completion import PathCompleter
    _USE_PROMPT_TOOLKIT = True
except Exception:
    pt_prompt = None
    PathCompleter = None
    _USE_PROMPT_TOOLKIT = False


def _prompt_for_path(prompt_text: str) -> str:
    """Prompt for a filesystem path with tab completion when possible.

    Uses prompt_toolkit.PathCompleter when available. Falls back to
    readline-based completion on POSIX, otherwise falls back to plain input().
    """
    if _USE_PROMPT_TOOLKIT and pt_prompt is not None and PathCompleter is not None:
        completer = PathCompleter(expanduser=True)
        return pt_prompt(prompt_text, completer=completer)

    # Try readline-based completion (best-effort).
    try:
        import readline, glob

        def _rl_completer(text, state):
            # expanduser variables before globbing
            pattern = os.path.expanduser(text) + "*"
            matches = glob.glob(pattern)
            # append separator for directories to hint the user
            matches = [m + (os.sep if os.path.isdir(m) else "") for m in matches]
            return matches[state] if state < len(matches) else None

        readline.set_completer(_rl_completer)
        # Enable Tab completion
        try:
            readline.parse_and_bind('tab: complete')
        except Exception:
            # Some readline implementations might differ; ignore failures
            pass
    except Exception:
        # No readline available; proceed with plain input
        pass

    return input(prompt_text)
def summarize(df: pd.DataFrame) -> pd.DataFrame:
    # masks
    null_mask = df.isna()
    empty_mask = df.apply(lambda col: col.fillna('').astype(str).str.strip() == '')
    combined = null_mask | empty_mask

    rows_any_null_or_empty = combined.any(axis=1).sum()
    rows_all_null_or_empty = combined.all(axis=1).sum()

    rows, cols = df.shape

    records = []
    for col in df.columns:
        ser = df[col]
        dtype = ser.dtype
        non_null = ser.count()
        nulls = ser.isna().sum()
        empties = ser.fillna('').astype(str).str.strip().eq('').sum()
        combined_count = (ser.isna() | ser.fillna('').astype(str).str.strip().eq('')).sum()
        unique = ser.nunique(dropna=True)

        stats = {}
        if pd.api.types.is_numeric_dtype(ser):
            stats['mean'] = ser.dropna().mean()
            stats['median'] = ser.dropna().median()
            stats['std'] = ser.dropna().std()
            stats['min'] = ser.dropna().min()
            stats['max'] = ser.dropna().max()
        else:
            top = ser.dropna().astype(str).str.strip()
            top = top[top != '']
            if not top.empty:
                top_mode = top.mode()
                stats['top'] = top_mode.iloc[0] if not top_mode.empty else ''
                stats['top_freq'] = (top == stats.get('top','')).sum()
            else:
                stats['top'] = ''
                stats['top_freq'] = 0

        rec = {
            'column': col,
            'dtype': str(dtype),
            'non_null_count': int(non_null),
            'null_count': int(nulls),
            'empty_string_count': int(empties),
            'null_or_empty_count': int(combined_count),
            'unique': int(unique),
            **stats
        }
        records.append(rec)

    summary_df = pd.DataFrame.from_records(records).set_index('column')
    # top-level counts as metadata
    meta = {
        'total_rows': rows,
        'total_columns': cols,
        'rows_with_any_null_or_empty': int(rows_any_null_or_empty),
        'rows_with_all_null_or_empty': int(rows_all_null_or_empty),
    }
    return summary_df, meta

def main():
    parser = argparse.ArgumentParser(description="Summarize a CSV (per-column stats + null/empty counts).")
    parser.add_argument("csv", nargs='?', help="Path to input CSV file (optional). If omitted, you'll be prompted.")
    parser.add_argument("--output", "-o", help="Path to save per-column summary CSV")
    parser.add_argument("--nrows", type=int, default=None, help="Only read this many rows (for large files)")
    args = parser.parse_args()

    # Determine CSV path (argument or interactive prompt)
    csv_path = args.csv
    if not csv_path:
        while True:
            try:
                csv_path = _prompt_for_path("Enter path to CSV file (or 'q' to quit): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nNo file provided. Exiting.")
                return
            if csv_path.lower() in ('q', 'quit', ''):
                print("No file provided. Exiting.")
                return
            # Expand user and check
            p = Path(csv_path).expanduser()
            if p.is_file():
                csv_path = str(p)
                break
            print(f"File not found: {csv_path}. Try again or install 'prompt_toolkit' for better tab-completion (pip install prompt_toolkit)")

    df = pd.read_csv(csv_path, nrows=args.nrows)
    summary_df, meta = summarize(df)

    print("=== File summary ===")
    print(f"Total rows: {meta['total_rows']}")
    print(f"Total columns: {meta['total_columns']}")
    print(f"Rows with ANY null/empty: {meta['rows_with_any_null_or_empty']}")
    print(f"Rows with ALL null/empty: {meta['rows_with_all_null_or_empty']}")
    print("\n=== Per-column summary ===")
    pd.set_option('display.max_columns', None)
    print(summary_df)

    if args.output:
        summary_df.to_csv(args.output)
        print(f"\nPer-column summary saved to: {args.output}")

if __name__ == "__main__":
    main()

