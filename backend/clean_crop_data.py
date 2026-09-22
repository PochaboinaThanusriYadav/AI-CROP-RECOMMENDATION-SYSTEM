import pandas as pd
import numpy as np

INPUT_FILE = "data/telangana_crop_clean.csv"
OUTPUT_FILE = "data/telangana_crop_final.csv"

print("Loading cleaned dataset...")

df = pd.read_csv(INPUT_FILE)

print("\nOriginal shape:")
print(df.shape)

# =====================================================
# 1. CLEAN SEASON NAMES
# =====================================================

df["season"] = (
    df["season"]
    .astype(str)
    .str.strip()
)

# Correct spelling variation
df["season"] = df["season"].replace({
    "Karif": "Kharif"
})

print("\nSeason distribution after normalization:")
print(df["season"].value_counts())

# =====================================================
# 2. NORMALIZE YEAR FORMAT
# =====================================================

def normalize_year(value):

    value = str(value).strip()

    if value == "2016":
        return "2016-2017"

    if value == "2017":
        return "2017-2018"

    if value == "2016-17":
        return "2016-2017"

    if value == "2017-18":
        return "2017-2018"

    if value == "2018-19":
        return "2018-2019"

    if value == "2019-2019":
        return "2019-2020"

    return value

df["year"] = df["year"].apply(normalize_year)

print("\nYear distribution after normalization:")
print(df["year"].value_counts().sort_index())

# =====================================================
# 3. CONVERT AREA COLUMNS TO NUMERIC
# =====================================================

df["normal_area"] = pd.to_numeric(
    df["normal_area"],
    errors="coerce"
)

df["actual_area"] = pd.to_numeric(
    df["actual_area"],
    errors="coerce"
)

# =====================================================
# 4. REMOVE NEGATIVE AREA VALUES
# =====================================================

df.loc[df["normal_area"] < 0, "normal_area"] = np.nan
df.loc[df["actual_area"] < 0, "actual_area"] = np.nan

# =====================================================
# 5. FILL MISSING AREA VALUES
# =====================================================
#
# We do NOT want to simply fill everything with 0.
#
# Instead:
# normal_area -> use 0 where unavailable
# actual_area -> use 0 where unavailable
#
# This is appropriate here because the dataset contains
# many legitimate zero-area records.

df["normal_area"] = df["normal_area"].fillna(0)
df["actual_area"] = df["actual_area"].fillna(0)

# =====================================================
# 6. REMOVE GENERIC CROP CATEGORIES
# =====================================================

generic_crops = [
    "Other food crops",
    "Other non-food crops",
    "Other oil seeds",
    "Other pulses"
]

df = df[
    ~df["crop"].isin(generic_crops)
].copy()

# =====================================================
# 7. REMOVE EMPTY / INVALID TEXT
# =====================================================

for column in ["district", "mandal", "crop", "season", "year"]:

    df[column] = (
        df[column]
        .astype(str)
        .str.strip()
    )

df = df[
    (df["district"] != "") &
    (df["mandal"] != "") &
    (df["crop"] != "") &
    (df["season"] != "") &
    (df["year"] != "")
].copy()

# =====================================================
# 8. REMOVE DUPLICATE RECORDS
# =====================================================

before_duplicates = len(df)

df = df.drop_duplicates()

after_duplicates = len(df)

print("\nDuplicate records removed:")
print(before_duplicates - after_duplicates)

# =====================================================
# 9. SAVE FINAL DATASET
# =====================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n======================================")
print("FINAL DATASET")
print("======================================")

print("Saved to:")
print(OUTPUT_FILE)

print("\nFinal shape:")
print(df.shape)

print("\nNumber of districts:")
print(df["district"].nunique())

print("\nNumber of mandals:")
print(df["mandal"].nunique())

print("\nNumber of crops:")
print(df["crop"].nunique())

print("\nSeasons:")
print(df["season"].value_counts())

print("\nYears:")
print(df["year"].value_counts().sort_index())

print("\nTop crops:")
print(df["crop"].value_counts().head(20))

print("\nRemaining missing values:")
print(df.isnull().sum())

print("\nSample:")
print(df.head(10).to_string(index=False))
