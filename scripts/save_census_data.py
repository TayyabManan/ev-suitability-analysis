import pandas as pd
import os

# Create data directory if it doesn't exist
os.makedirs('data/demographics', exist_ok=True)

# Lahore Census Data 2023
lahore_2023_data = {
    'Tehsil': ['Lahore District Total', 'Lahore Cantt', 'Lahore City', 'Model Town', 'Raiwind', 'Shalimar'],
    'Area_SqKm': [1772, 466, 214, 353, 467, 272],
    'Population_2023': [13004135, 1885098, 4123354, 3244906, 1080637, 2670140],
    'Male_2023': [6881801, 1005669, 2203776, 1687860, 581873, 1402623],
    'Female_2023': [6118958, 879143, 1917723, 1556362, 498419, 1267311],
    'Population_Density': [7338.68, 4045.27, 19268.01, 9192.37, 2314.00, 9816.69],
    'Household_Size': [6.4, 6.3, 6.5, 6.5, 6.3, 6.3],
    'Population_2017': [11119985, 1632702, 3644787, 2712398, 848541, 2281557],
    'Annual_Growth_Rate': [2.65, 2.43, 2.08, 3.04, 4.12, 2.66]
}

# Create DataFrame and save
df_census = pd.DataFrame(lahore_2023_data)
df_census.to_csv('data/demographics/lahore_census_2023.csv', index=False)

print("✅ Census data saved to data/demographics/lahore_census_2023.csv")
print("\nPreview:")
print(df_census.head())

# Calculate some basic statistics
total_pop = df_census.loc[0, 'Population_2023']
total_area = df_census.loc[0, 'Area_SqKm']
print(f"\n📊 Key Statistics:")
print(f"Total Population: {total_pop:,}")
print(f"Total Area: {total_area:,} sq.km")
print(f"Average Density: {total_pop/total_area:.0f} people/sq.km")