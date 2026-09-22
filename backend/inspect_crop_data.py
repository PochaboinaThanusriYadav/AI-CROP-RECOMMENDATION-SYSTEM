import pandas as pd

FILE = "data/telangana_crop_clean.csv"

print("Loading cleaned dataset...")

df = pd.read_csv(FILE)

print("\n======================================")
print("DATASET OVERVIEW")
print("======================================")

print("Shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\n======================================")
print("DISTRICTS")
print("======================================")

print("Number of districts:", df["district"].nunique())

print(df["district"].value_counts().head(20))

print("\n======================================")
print("SEASONS")
print("======================================")

print(df["season"].value_counts())

print("\n======================================")
print("YEARS")
print("======================================")

print(df["year"].value_counts().sort_index())

print("\n======================================")
print("CROPS")
print("======================================")

crop_counts = df["crop"].value_counts()

print("Total unique crops:", crop_counts.shape[0])

print("\nTop 30 crops:")
print(crop_counts.head(30))

print("\n======================================")
print("AREA INFORMATION")
print("======================================")

print("\nNormal area statistics:")
print(df["normal_area"].describe())

print("\nActual area statistics:")
print(df["actual_area"].describe())

print("\n======================================")
print("SAMPLE RECORDS")
print("======================================")

print(df.head(10).to_string(index=False))
