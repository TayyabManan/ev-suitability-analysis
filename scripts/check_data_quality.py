import os
import pandas as pd
import geopandas as gpd

print("🔍 LAHORE EV PROJECT - DATA QUALITY CHECK")
print("=" * 50)

# Check census data
print("\n📊 CENSUS DATA:")
if os.path.exists('data/demographics/lahore_census_2023.csv'):
    census_df = pd.read_csv('data/demographics/lahore_census_2023.csv')
    print(f"✅ Census data loaded: {len(census_df)} records")
    print(f"   Total population: {census_df.loc[0, 'Population_2023']:,}")
else:
    print("❌ Census data missing")

# Check OSM boundary data
print("\n🗺️ BOUNDARY DATA:")
if os.path.exists('data/boundaries/lahore_boundary.shp'):
    boundary = gpd.read_file('data/boundaries/lahore_boundary.shp')
    print(f"✅ Lahore boundary loaded: {len(boundary)} features")
else:
    print("❌ Boundary data missing")

# Check infrastructure data
print("\n🏗️ INFRASTRUCTURE DATA:")
infrastructure_files = [
    ('fuel_stations.shp', 'Fuel stations'),
    ('lahore_roads.shp', 'Road network'),
    ('commercial_areas.shp', 'Commercial areas'),
    ('education.shp', 'Educational institutions'),
    ('healthcare.shp', 'Healthcare facilities')
]

total_infrastructure = 0
for filename, description in infrastructure_files:
    filepath = f'data/infrastructure/{filename}'
    if os.path.exists(filepath):
        try:
            gdf = gpd.read_file(filepath)
            print(f"✅ {description}: {len(gdf)} features")
            total_infrastructure += len(gdf)
        except:
            print(f"⚠️ {description}: File exists but couldn't read")
    else:
        print(f"❌ {description}: Not found")

# Check output files
print("\n📋 OUTPUT FILES:")
output_files = [
    ('outputs/maps/lahore_population_density.html', 'Population density map'),
    ('outputs/maps/lahore_infrastructure_overview.html', 'Infrastructure overview map'),
    ('outputs/reports/data_summary.md', 'Data summary report')
]

for filepath, description in output_files:
    if os.path.exists(filepath):
        size_kb = os.path.getsize(filepath) / 1024
        print(f"✅ {description}: {size_kb:.1f} KB")
    else:
        print(f"❌ {description}: Missing")

# Overall assessment
print("\n🎯 OVERALL ASSESSMENT:")
if total_infrastructure > 50:
    print("🟢 EXCELLENT: Rich infrastructure data collected")
elif total_infrastructure > 20:
    print("🟡 GOOD: Decent infrastructure data available")
elif total_infrastructure > 0:
    print("🟠 LIMITED: Some infrastructure data, may need alternatives")
else:
    print("🔴 MINIMAL: Very limited data, focus on creative proxies")

print(f"\nTotal infrastructure points collected: {total_infrastructure}")

print("\n📝 NEXT STEPS:")
print("1. Open your HTML maps in a browser to review")
print("2. If data looks good, proceed to economic data collection")
print("3. If data is limited, focus on proxy indicators")
print("4. Document any data gaps for your methodology")

print("\n🚀 Ready for Week 2 data collection!")