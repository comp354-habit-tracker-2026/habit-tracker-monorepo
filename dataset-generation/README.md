# Dataset Builder Pipeline

Converts a dated time-series CSV into sliding-window `.npy` datasets
ready for ML model training (MLP, LSTM, etc.).

---

## Exact Regeneration Command

```bash
python dataset_builder.py data/example.csv artifacts/ --lookback 7 --target-col target
```

---

## CLI Reference
# Default (.npy — fastest at training time)
python dataset_builder.py data/example.csv artifacts/ --lookback 7

# Human-readable CSV
python dataset_builder.py data/example.csv artifacts/ --lookback 7 --format csv

# Columnar Parquet (best for large datasets or Spark pipelines)
python dataset_builder.py data/example.cs# Dataset Builder Pipeline

Converts a dated time-series CSV into sliding-window datasets for ML training (MLP, LSTM, etc.).

---

## Regeneration Command

```bash
python dataset_builder.py data/example.csv artifacts/ --lookback 7 --target-col target
```

---

## CLI Options
Positional:
input Path to input CSV (requires 'date' and target columns)
output_dir Output directory (created if absent)

Options:
--lookback N Window size — past N values as features [default: 7]
--stride N Step between windows [default: 1]
--target-col NAME Target column name [default: target]
--format FMT Export format: npy | csv | parquet [default: npy]
--split T V Te Train/val/test ratios, must sum to 1 [default: 0.70 0.15 0.15]

text

---

## Preprocessing Rules

1. **Sorted ascending by date**
2. **Duplicates: keep last occurrence per date**
3. **Missing dates ignored — no interpolation**
4. **X = past N observed values, y = next observed value**

---

## Output
artifacts/
├── train_X.npy / train.csv / train.parquet
├── val_X.npy / val.csv / val.parquet
├── test_X.npy / test.csv / test.parquet
└── metadata.json

text

---

## Dependencies
pandas>=1.3
numpy>=1.21
pyarrow>=7.0 # only needed for --format parquetv artifacts/ --lookback 7 --format parquet