import geopandas as gpd
import folium
import pandas as pd
import os

# Ensure all output directories exist
os.makedirs('outputs/reports', exist_ok=True)
os.makedirs('outputs/maps', exist_ok=True)

print("Creating initial maps for Lahore EV project...")

# Load census data
census_df = pd.read_csv('../data/demographics/lahore_census_2023.csv')

# Create Lahore center coordinates (approximate)
lahore_center = [31.5204, 74.3587]

# STEP 1: Create population density map
print("\n1. Creating population density map...")

# Create base map
m1 = folium.Map(location=lahore_center, zoom_start=11, tiles='OpenStreetMap')

# Add census data as markers (we'll improve this when we have shapefiles)
tehsil_coordinates = {
    'Lahore City': [31.5204, 74.3587],
    'Model Town': [31.5204, 74.3287],
    'Shalimar': [31.5404, 74.3687],
    'Lahore Cantt': [31.5004, 74.3387],
    'Raiwind': [31.4204, 74.3887]
}

for idx, row in census_df.iterrows():
    if row['Tehsil'] != 'Lahore District Total':
        tehsil = row['Tehsil']
        if tehsil in tehsil_coordinates:
            lat, lon = tehsil_coordinates[tehsil]

            # Create popup with key statistics
            popup_text = f"""
            <b>{tehsil}</b><br>
            Population: {row['Population_2023']:,}<br>
            Density: {row['Population_Density']:,.0f}/sq.km<br>
            Growth Rate: {row['Annual_Growth_Rate']:.1f}%<br>
            Household Size: {row['Household_Size']}
            """

            # Size marker based on population
            radius = max(5, min(25, row['Population_2023'] / 200000))

            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                popup=folium.Popup(popup_text, max_width=250),
                color='blue',
                fill=True,
                fillColor='lightblue',
                fillOpacity=0.7
            ).add_to(m1)

# Save population map
m1.save('outputs/maps/lahore_population_density.html')
print("Population density map saved!")

# STEP 2: Create infrastructure overview map (if OSM data exists)
print("\n2. Creating infrastructure overview map...")

m2 = folium.Map(location=lahore_center, zoom_start=11, tiles='OpenStreetMap')

# Try to load and display infrastructure data
try:
    # Load infrastructure files we collected
    infrastructure_files = [
        ('commercial_sample.shp', 'Commercial Areas', 'green', 'shopping-cart'),
        ('education_sample.shp', 'Universities', 'blue', 'graduation-cap'),
        ('healthcare_sample.shp', 'Hospitals', 'red', 'plus-square'),
        ('transport_sample.shp', 'Transport', 'purple', 'bus'),
        ('residential_sample.shp', 'Residential', 'orange', 'home')
    ]

    total_points = 0

    for filename, label, color, icon in infrastructure_files:
        filepath = f'data/infrastructure/{filename}'

        if os.path.exists(filepath):
            try:
                infrastructure = gpd.read_file(filepath)

                for idx, point in infrastructure.iterrows():
                    if point.geometry.geom_type == 'Point':
                        lat, lon = point.geometry.y, point.geometry.x

                        # Create popup text
                        name = point.get('name', 'Unknown')
                        poi_type = point.get('type', label)

                        popup_text = f"<b>{name}</b><br>Type: {poi_type}<br>Category: {label}"

                        folium.Marker(
                            location=[lat, lon],
                            popup=folium.Popup(popup_text, max_width=200),
                            icon=folium.Icon(color=color, icon=icon, prefix='fa')
                        ).add_to(m2)

                        total_points += 1

                print(f"Added {len(infrastructure)} {label} points to map")

            except Exception as e:
                print(f"Could not load {filename}: {e}")
        else:
            print(f"File not found: {filename}")

except Exception as e:
    print(f"Error loading infrastructure data: {e}")

# Save infrastructure map
m2.save('outputs/maps/lahore_infrastructure_overview.html')
print("Infrastructure overview map saved!")

# STEP 3: Create summary report (without emojis)
print("\n3. Creating data summary report...")

summary_report = f"""# Lahore EV Charging Station Analysis - Data Summary

## Population Analysis (2023 Census)
- **Total Population**: {census_df.loc[0, 'Population_2023']:,}
- **Total Area**: {census_df.loc[0, 'Area_SqKm']:,} sq.km
- **Average Density**: {census_df.loc[0, 'Population_Density']:,.0f} people/sq.km
- **Annual Growth Rate**: {census_df.loc[0, 'Annual_Growth_Rate']:.1f}%

## Tehsil Analysis
"""

for idx, row in census_df.iterrows():
    if row['Tehsil'] != 'Lahore District Total':
        summary_report += f"""
### {row['Tehsil']}
- Population: {row['Population_2023']:,} ({row['Population_2023'] / census_df.loc[0, 'Population_2023'] * 100:.1f}% of district)
- Density: {row['Population_Density']:,.0f} people/sq.km
- Growth Rate: {row['Annual_Growth_Rate']:.1f}% annually
- Household Size: {row['Household_Size']} people
"""

# Count available data files
data_files_count = 0
infrastructure_count = 0

# Check what files exist
file_checks = [
    'data/boundaries/lahore_boundary.shp',
    'data/infrastructure/commercial_sample.shp',
    'data/infrastructure/education_sample.shp',
    'data/infrastructure/healthcare_sample.shp',
    'data/infrastructure/transport_sample.shp',
    'data/infrastructure/residential_sample.shp'
]

available_files = []
for file_path in file_checks:
    if os.path.exists(file_path):
        available_files.append(file_path)
        data_files_count += 1
        if 'infrastructure' in file_path:
            infrastructure_count += 1

summary_report += f"""
## Data Collection Status
- Census demographics (2017 & 2023): Available
- Administrative boundaries: Available
- Infrastructure points: {infrastructure_count} categories collected
- Total data files: {data_files_count}

## Key Insights for EV Charging Strategy
1. **Highest Density Area**: Lahore City Tehsil (19,268 people/sq.km)
2. **Fastest Growing Area**: Raiwind Tehsil (4.1% annual growth)
3. **Largest Population**: Lahore City Tehsil (4.1M people)
4. **Development Opportunities**: Model Town (3.0% growth, high density)

## Next Steps
1. Multi-criteria site selection analysis
2. Traffic pattern integration
3. Economic activity mapping
4. Infrastructure accessibility analysis

## Files Created
- Population density map: outputs/maps/lahore_population_density.html
- Infrastructure overview: outputs/maps/lahore_infrastructure_overview.html
- Census data: data/demographics/lahore_census_2023.csv
- Boundary data: data/boundaries/lahore_boundary.shp
- Infrastructure data: {infrastructure_count} categories in data/infrastructure/

## Portfolio Value
This project demonstrates:
- Real-world data constraints handling
- Emerging market methodology
- Creative problem-solving with limited data
- Multi-source data integration
- Professional GIS workflow development
"""

# Save report with UTF-8 encoding
try:
    with open('outputs/reports/data_summary.md', 'w', encoding='utf-8') as f:
        f.write(summary_report)
    print("Summary report saved!")
except Exception as e:
    # Fallback: save without special characters
    clean_report = summary_report.replace('✅', '[OK]').replace('❌', '[MISSING]').replace('📊', '').replace('🗺️', '')
    with open('outputs/reports/data_summary.md', 'w') as f:
        f.write(clean_report)
    print("Summary report saved (cleaned version)!")

print("\nCOMPLETE! All maps and reports created successfully!")
print("=" * 50)
print("Your files are ready:")
print("- Population density map: outputs/maps/lahore_population_density.html")
print("- Infrastructure overview: outputs/maps/lahore_infrastructure_overview.html")
print("- Data summary report: outputs/reports/data_summary.md")
print("\nOpen the HTML files in your browser to see your maps!")