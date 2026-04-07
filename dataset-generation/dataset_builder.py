"""
Bradley Henry - 40248051 
Github issue #119

Dataset Builder — sliding-window time-series preprocessor.

Converts a dated CSV into windowed .npy train/val/test splits.
Preprocessing: sort by date → dedup (keep last) → sliding windows → chronological split.

Generated with assistance from Claude Sonnet 4.6 (Perplexity AI, 2026).
"""

import argparse, json, os
import numpy as np
import pandas as pd


def load_and_clean(path: str, target_col: str) -> pd.DataFrame:
    """Load CSV and apply date-sort + deduplication cleaning.

    Args:
        path (str): Path to the input CSV file.
        target_col (str): Name of the numeric target column.

    Returns:
        pd.DataFrame: Cleaned dataframe with columns ['date', target_col],
            sorted ascending by date, one row per unique date (last kept).

    Raises:
        ValueError: If 'date' or target_col columns are missing.
    """
    df = pd.read_csv(path)
    for col in ("date", target_col):
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}'")
    df["date"] = pd.to_datetime(df["date"])
    df = (df.sort_values("date")
            .drop_duplicates(subset="date", keep="last")
            [["date", target_col]]
            .reset_index(drop=True))
    return df


def build_windows(df: pd.DataFrame, target_col: str, lookback: int, stride: int):
    """Build sliding windows of fixed lookback over the target series.

    Args:
        df (pd.DataFrame): Cleaned dataframe from load_and_clean().
        target_col (str): Name of the numeric target column.
        lookback (int): Number of past observations per window (N).
        stride (int): Step size between consecutive window start indices.

    Returns:
        tuple:
            - X (np.ndarray): Feature windows, shape (n_samples, lookback), float64.
            - y (np.ndarray): Target values, shape (n_samples,), float64.
            - dates (np.ndarray): ISO date strings of each y observation,
              shape (n_samples,), dtype str.

    Raises:
        ValueError: If the dataset has too few rows to form any window.
    """
    vals  = df[target_col].to_numpy(dtype=float)
    dates = df["date"].dt.strftime("%Y-%m-%d").to_numpy()
    n = len(vals)
    if n <= lookback:
        raise ValueError(f"Need > {lookback} rows after dedup; got {n}.")
    idxs = range(0, n - lookback, stride)
    X = np.array([vals[i : i + lookback] for i in idxs])
    y = np.array([vals[i + lookback]     for i in idxs])
    d = np.array([dates[i + lookback]    for i in idxs])
    return X, y, d


def chronological_split(X, y, dates, ratios=(0.70, 0.15, 0.15)):
    """Split windowed samples chronologically into train / val / test sets.

    No shuffling is applied; order is preserved to prevent data leakage.
    Each split is guaranteed at least 1 sample via boundary guards.

    Args:
        X (np.ndarray): Feature array, shape (n_samples, lookback).
        y (np.ndarray): Target array, shape (n_samples,).
        dates (np.ndarray): Date strings array, shape (n_samples,).
        ratios (tuple[float, float, float]): Fractional sizes for
            (train, val, test). Must sum to 1.0. Defaults to (0.70, 0.15, 0.15).

    Returns:
        dict[str, tuple]: Keys 'train', 'val', 'test'; each value is
            a tuple of (X_split, y_split, dates_split) as np.ndarray.
    """
    n  = len(X)
    i1 = max(1, int(n * ratios[0]))
    i2 = max(i1 + 1, int(n * (ratios[0] + ratios[1])))
    return {
        "train": (X[:i1],   y[:i1],   dates[:i1]),
        "val":   (X[i1:i2], y[i1:i2], dates[i1:i2]),
        "test":  (X[i2:],   y[i2:],   dates[i2:]),
    }


# In save_artifacts(), replace the np.save block with:
def save_artifacts(splits: dict, out_dir: str, meta: dict, fmt: str = "npy") -> dict:
    """
    Args:
        fmt (str): Export format — one of 'npy', 'csv', 'parquet'.
    """
    os.makedirs(out_dir, exist_ok=True)
    counts = {}
    for split, (X, y, d) in splits.items():
        n_features = X.shape[1]
        feat_cols  = [f"t-{n_features - i}" for i in range(n_features)]
        df_out = pd.DataFrame(X, columns=feat_cols)
        df_out["y"]           = y
        df_out["target_date"] = d

        if fmt == "npy":
            for arr, tag in ((X, "X"), (y, "y"), (d, "target_dates")):
                np.save(os.path.join(out_dir, f"{split}_{tag}.npy"), arr)
        elif fmt == "csv":
            df_out.to_csv(os.path.join(out_dir, f"{split}.csv"), index=False)
        elif fmt == "parquet":
            df_out.to_parquet(os.path.join(out_dir, f"{split}.parquet"), index=False)
        else:
            raise ValueError(f"Unsupported format: '{fmt}'. Choose npy, csv, or parquet.")

        counts[split] = int(len(y))

    meta["split_counts"] = counts
    meta["format"]       = fmt
    with open(os.path.join(out_dir, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)
    return counts


def main():
    """CLI entry point — parse arguments and run the full pipeline."""
    p = argparse.ArgumentParser(
        description="Build sliding-window dataset from a time-series CSV."
    )
    p.add_argument("input",       help="Path to input CSV")
    p.add_argument("output_dir",  help="Artifacts output directory")
    p.add_argument("--lookback",   type=int, default=7,  metavar="N",
                   help="Window size N (default: 7)")
    p.add_argument("--stride",     type=int, default=1,  metavar="N",
                   help="Stride between windows (default: 1)")
    p.add_argument("--target-col", default="target",
                   help="Target column name (default: target)")
    p.add_argument("--split",      nargs=3, type=float,
                   default=[0.70, 0.15, 0.15], metavar=("TRAIN", "VAL", "TEST"),
                   help="Chronological split ratios (default: 0.70 0.15 0.15)")
    
    p.add_argument("--format", default="npy", choices=["npy", "csv", "parquet"],
               help="Export format for dataset artifacts (default: npy)")
    
    args = p.parse_args()

    if abs(sum(args.split) - 1.0) > 1e-6:
        p.error("Split ratios must sum to 1.0")

    print(f"[1/4] Loading   {args.input}")
    df = load_and_clean(args.input, args.target_col)
    print(f"      Rows after dedup: {len(df)}")

    print(f"[2/4] Windowing  lookback={args.lookback}  stride={args.stride}")
    X, y, dates = build_windows(df, args.target_col, args.lookback, args.stride)
    print(f"      Samples: {len(X)}  X shape: {X.shape}")

    print(f"[3/4] Splitting  {args.split}")
    splits = chronological_split(X, y, dates, tuple(args.split))

    meta = {
        "input": args.input, "target_col": args.target_col,
        "lookback": args.lookback, "stride": args.stride,
        "split_ratios": dict(zip(("train", "val", "test"), args.split)),
        "total_samples": int(len(X)),
    }
    print(f"[4/4] Exporting  {args.output_dir}")
    counts = save_artifacts(splits, args.output_dir, meta, fmt=args.format)

    print("\nArtifacts written:")
    for split in ("train", "val", "test"):
        for tag in ("X", "y", "target_dates"):
            fp = os.path.join(args.output_dir, f"{split}_{tag}.npy")
            print(f"   {fp:<48} ({counts[split]:>3} rows, {os.path.getsize(fp)} bytes)")
    print(f"   {os.path.join(args.output_dir, 'metadata.json')}")
    print(f"\n   train={counts['train']}  val={counts['val']}  test={counts['test']}")


if __name__ == "__main__":
    main()