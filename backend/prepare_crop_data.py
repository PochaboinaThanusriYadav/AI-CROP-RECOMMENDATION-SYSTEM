import pandas as pd

INPUT_FILE = "data/telangana_FINAL_DATASET.csv"
OUTPUT_FILE = "data/telangana_crop_clean.csv"

print("Loading dataset...")

df = pd.read_csv(INPUT_FILE)

print("\nOriginal shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

# ---------------------------------------
# Check source types
# ---------------------------------------

print("\nSource types:")
print(df["source_type"].value_counts(dropna=False))

# ---------------------------------------
# Keep actual crop-area records
# ---------------------------------------

df = df[
    df["source_type"]
    .astype(str)
    .str.strip()
    .str.lower()
    .eq("crop_area")
].copy()

print("\nAfter selecting crop_area records:")
print(df.shape)

# ---------------------------------------
# Remove aggregate/non-individual crop rows
# ---------------------------------------

aggregate_names = [
    "total",
    "grand total",
    "total food crops",
    "total pulses",
    "total oil seeds",
    "total cereals",
    "total commercial crops"
]

df["crop"] = df["crop"].astype(str).str.strip()

df = df[
    ~df["crop"].str.lower().isin(aggregate_names)
].copy()

# ---------------------------------------
# Remove rows without essential fields
# ---------------------------------------

df = df.dropna(
    subset=[
        "year",
        "season",
        "district",
        "mandal",
        "crop"
    ]
)

# ---------------------------------------
# Clean text fields
# ---------------------------------------

for column in ["year", "season", "district", "mandal", "crop"]:
    df[column] = (
        df[column]
        .astype(str)
        .str.strip()
    )

# ---------------------------------------
# Keep useful columns
# ---------------------------------------

columns = [
    "year",
    "season",
    "district",
    "mandal",
    "crop",
    "normal_area",
    "actual_area"
]

df = df[columns]

# ---------------------------------------
# Save cleaned dataset
# ---------------------------------------

df.to_csv(OUTPUT_FILE, index=False)

print("\nCleaned dataset saved:")
print(OUTPUT_FILE)

print("\nFinal shape:")
print(df.shape)

print("\nNumber of crops:")
print(df["crop"].nunique())

print("\nCrop names:")
print(sorted(df["crop"].unique()))

print("\nSample:")
print(df.head(10))
