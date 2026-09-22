import pandas as pd

INPUT_FILE = "data/telangana_crop_final.csv"
OUTPUT_FILE = "data/crop_location_profile.csv"

print("Loading final crop dataset...")

df = pd.read_csv(INPUT_FILE)

# =====================================================
# GROUP BY LOCATION + SEASON + CROP
# =====================================================

profile = (
    df.groupby(
        [
            "district",
            "mandal",
            "season",
            "crop"
        ],
        as_index=False
    )
    .agg(
        records=("crop", "count"),
        total_normal_area=("normal_area", "sum"),
        total_actual_area=("actual_area", "sum"),
        average_normal_area=("normal_area", "mean"),
        average_actual_area=("actual_area", "mean")
    )
)

# =====================================================
# CALCULATE HISTORICAL CULTIVATION SHARE
# =====================================================

location_totals = (
    profile.groupby(
        ["district", "mandal", "season"]
    )["total_actual_area"]
    .transform("sum")
)

profile["cultivation_share"] = (
    profile["total_actual_area"] /
    location_totals
)

# Handle locations where total actual area is zero
profile["cultivation_share"] = (
    profile["cultivation_share"]
    .fillna(0)
)

# =====================================================
# SORT BY LOCATION AND CULTIVATION
# =====================================================

profile = profile.sort_values(
    [
        "district",
        "mandal",
        "season",
        "cultivation_share"
    ],
    ascending=[True, True, True, False]
)

# =====================================================
# SAVE
# =====================================================

profile.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n======================================")
print("CROP LOCATION PROFILE")
print("======================================")

print("Output file:")
print(OUTPUT_FILE)

print("\nShape:")
print(profile.shape)

print("\nColumns:")
print(profile.columns.tolist())

print("\nSample:")
print(profile.head(20).to_string(index=False))

# =====================================================
# TEST EXAMPLE
# =====================================================

print("\n======================================")
print("EXAMPLE LOCATION")
print("======================================")

example = profile[
    (profile["district"] == "Mancherial") &
    (profile["mandal"] == "Jannaram") &
    (profile["season"] == "Kharif")
]

print(
    example[
        [
            "district",
            "mandal",
            "season",
            "crop",
            "total_actual_area",
            "cultivation_share"
        ]
    ].head(10).to_string(index=False)
)
