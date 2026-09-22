import pandas as pd

PROFILE_FILE = "data/crop_location_profile.csv"

# =====================================================
# LOAD PROFILE
# =====================================================

profile = pd.read_csv(PROFILE_FILE)

# =====================================================
# NORMALIZE TEXT
# =====================================================

for column in ["district", "mandal", "season", "crop"]:
    profile[column] = (
        profile[column]
        .astype(str)
        .str.strip()
    )

# =====================================================
# RECOMMEND CROPS
# =====================================================

def recommend_crops(
    district,
    mandal,
    season,
    top_n=5
):

    district = str(district).strip()
    mandal = str(mandal).strip()
    season = str(season).strip()

    # ---------------------------------------------
    # Find exact location + season
    # ---------------------------------------------

    result = profile[
        (profile["district"].str.lower() == district.lower()) &
        (profile["mandal"].str.lower() == mandal.lower()) &
        (profile["season"].str.lower() == season.lower())
    ].copy()

    # ---------------------------------------------
    # If exact mandal data is unavailable,
    # fall back to district + season
    # ---------------------------------------------

    if result.empty:

        result = profile[
            (profile["district"].str.lower() == district.lower()) &
            (profile["season"].str.lower() == season.lower())
        ].copy()

    # ---------------------------------------------
    # If still no data, return empty result
    # ---------------------------------------------

    if result.empty:
        return []

    # ---------------------------------------------
    # Sort by historical cultivation share
    # ---------------------------------------------

    result = result.sort_values(
        "cultivation_share",
        ascending=False
    )

    # ---------------------------------------------
    # Select top crops
    # ---------------------------------------------

    result = result.head(top_n)

    recommendations = []

    for _, row in result.iterrows():

        recommendations.append({
            "crop": row["crop"],
            "cultivation_share": round(
                float(row["cultivation_share"]) * 100,
                2
            ),
            "historical_actual_area": round(
                float(row["total_actual_area"]),
                2
            ),
            "records": int(row["records"])
        })

    return recommendations

# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    print("\nTesting crop recommendation...\n")

    recommendations = recommend_crops(
        district="Mancherial",
        mandal="Jannaram",
        season="Kharif",
        top_n=5
    )

    if not recommendations:

        print("No recommendations found.")

    else:

        print("Recommendations:")

        for index, item in enumerate(
            recommendations,
            start=1
        ):

            print(
                f"{index}. "
                f"{item['crop']} | "
                f"Historical Share: "
                f"{item['cultivation_share']}% | "
                f"Actual Area: "
                f"{item['historical_actual_area']} acres"
            )
