import pandas as pd
import numpy as np
import folium
import geopandas as gpd
from shapely.geometry import Point
import os

# Ensure output directory exists
os.makedirs('outputs/analysis', exist_ok=True)
os.makedirs('outputs/maps', exist_ok=True)

print("⚡ LAHORE EV CHARGING STATION SITE SELECTION ANALYSIS")
print("=" * 60)

# Lahore Census Data (embedded for reliability)
lahore_data = {
    'Tehsil': ['Lahore City', 'Model Town', 'Shalimar', 'Lahore Cantt', 'Raiwind'],
    'Population_2023': [4123354, 3244906, 2670140, 1885098, 1080637],
    'Area_SqKm': [214, 353, 272, 466, 467],
    'Population_Density': [19268, 9192, 9817, 4045, 2314],
    'Annual_Growth_Rate': [2.08, 3.04, 2.66, 2.43, 4.12],
    'Household_Size': [6.5, 6.5, 6.3, 6.3, 6.3],
    'Lat': [31.5204, 31.5204, 31.5404, 31.5004, 31.4204],
    'Lon': [74.3587, 74.3287, 74.3687, 74.3387, 74.3887]
}

census_df = pd.DataFrame(lahore_data)

print("\n📊 DEMOGRAPHIC FOUNDATION:")
for _, row in census_df.iterrows():
    print(f"🏛️ {row['Tehsil']}: {row['Population_2023']:,} people, {row['Population_Density']:,.0f}/sq.km")

# Step 1: Define EV Site Selection Criteria
print("\n⚡ STEP 1: DEFINING SITE SELECTION CRITERIA")
print("-" * 40)

criteria_weights = {
    'population_density': 0.30,  # High density = more potential users
    'growth_rate': 0.20,  # Future demand potential
    'accessibility': 0.25,  # Easy to reach
    'economic_activity': 0.15,  # Commercial activity level
    'infrastructure': 0.10  # Existing infrastructure
}

print("📋 Criteria and Weights:")
for criterion, weight in criteria_weights.items():
    print(f"   {criterion.replace('_', ' ').title()}: {weight:.0%}")

# Step 2: Score each tehsil on criteria
print("\n⚡ STEP 2: SCORING TEHSILS")
print("-" * 40)


def normalize_score(values, higher_is_better=True):
    """Normalize values to 0-100 scale"""
    min_val, max_val = min(values), max(values)
    if higher_is_better:
        return [(val - min_val) / (max_val - min_val) * 100 for val in values]
    else:
        return [(max_val - val) / (max_val - min_val) * 100 for val in values]


# Calculate scores for each criterion
census_df['density_score'] = normalize_score(census_df['Population_Density'])
census_df['growth_score'] = normalize_score(census_df['Annual_Growth_Rate'])

# Accessibility score (inverse of area - smaller area = more accessible)
census_df['accessibility_score'] = normalize_score(census_df['Area_SqKm'], higher_is_better=False)

# Economic activity score (based on density + size)
economic_activity = census_df['Population_2023'] * census_df['Population_Density'] / 1000000
census_df['economic_score'] = normalize_score(economic_activity)

# Infrastructure score (based on existing development - higher density areas)
census_df['infrastructure_score'] = census_df['density_score']

# Calculate weighted composite score
census_df['composite_score'] = (
        census_df['density_score'] * criteria_weights['population_density'] +
        census_df['growth_score'] * criteria_weights['growth_rate'] +
        census_df['accessibility_score'] * criteria_weights['accessibility'] +
        census_df['economic_score'] * criteria_weights['economic_activity'] +
        census_df['infrastructure_score'] * criteria_weights['infrastructure']
)

# Rank by composite score
census_df = census_df.sort_values('composite_score', ascending=False).reset_index(drop=True)
census_df['priority_rank'] = range(1, len(census_df) + 1)

print("🏆 TEHSIL RANKINGS:")
for _, row in census_df.iterrows():
    print(f"#{row['priority_rank']}: {row['Tehsil']} - Score: {row['composite_score']:.1f}")

# Step 3: Recommend specific site locations
print("\n⚡ STEP 3: SPECIFIC SITE RECOMMENDATIONS")
print("-" * 40)

# Define potential EV charging locations based on known Lahore landmarks
potential_sites = {
    'Lahore City': [
        {'name': 'Liberty Market Area', 'lat': 31.5497, 'lon': 74.3436, 'type': 'Commercial Hub'},
        {'name': 'Mall Road Business District', 'lat': 31.5656, 'lon': 74.3242, 'type': 'Commercial'},
        {'name': 'Anarkali Bazaar Area', 'lat': 31.5804, 'lon': 74.3137, 'type': 'Commercial Hub'}
    ],
    'Model Town': [
        {'name': 'Model Town Commercial Area', 'lat': 31.5100, 'lon': 74.3200, 'type': 'Commercial'},
        {'name': 'University of Punjab', 'lat': 31.5497, 'lon': 74.3436, 'type': 'Educational Hub'}
    ],
    'Shalimar': [
        {'name': 'Shalimar Gardens Area', 'lat': 31.5884, 'lon': 74.3755, 'type': 'Tourist/Residential'},
        {'name': 'GT Road Commercial', 'lat': 31.5600, 'lon': 74.3800, 'type': 'Commercial'}
    ],
    'Lahore Cantt': [
        {'name': 'DHA Commercial Area', 'lat': 31.4697, 'lon': 74.2599, 'type': 'Premium Residential'},
        {'name': 'Fortress Stadium Area', 'lat': 31.5204, 'lon': 74.3587, 'type': 'Sports/Entertainment'}
    ],
    'Raiwind': [
        {'name': 'Raiwind Road Commercial', 'lat': 31.4200, 'lon': 74.3900, 'type': 'Developing Commercial'}
    ]
}

# Create detailed site analysis
site_recommendations = []

for _, tehsil_row in census_df.iterrows():
    tehsil_name = tehsil_row['Tehsil']
    tehsil_score = tehsil_row['composite_score']
    tehsil_rank = tehsil_row['priority_rank']

    if tehsil_name in potential_sites:
        for site in potential_sites[tehsil_name]:
            site_score = tehsil_score + np.random.uniform(-5, 5)  # Add site-specific variation

            site_recommendations.append({
                'Site_Name': site['name'],
                'Tehsil': tehsil_name,
                'Priority_Rank': tehsil_rank,
                'Site_Type': site['type'],
                'Latitude': site['lat'],
                'Longitude': site['lon'],
                'Tehsil_Score': tehsil_score,
                'Site_Score': max(0, site_score),
                'Population_Served': tehsil_row['Population_2023'],
                'Growth_Potential': tehsil_row['Annual_Growth_Rate'],
                'Recommendation': 'High Priority' if site_score > 70 else 'Medium Priority' if site_score > 50 else 'Future Consideration'
            })

sites_df = pd.DataFrame(site_recommendations)
sites_df = sites_df.sort_values('Site_Score', ascending=False).reset_index(drop=True)

print("🎯 TOP 5 RECOMMENDED SITES:")
for i, row in sites_df.head().iterrows():
    print(f"{i + 1}. {row['Site_Name']} ({row['Tehsil']})")
    print(f"   Score: {row['Site_Score']:.1f} | Type: {row['Site_Type']} | {row['Recommendation']}")

# Step 4: Create detailed analysis map with branding
print("\n⚡ STEP 4: CREATING BRANDED ANALYSIS MAP")
print("-" * 40)

# Create map
m = folium.Map(location=[31.5204, 74.3587], zoom_start=11, tiles='OpenStreetMap')

# Add tehsil boundaries (approximate circles)
for _, row in census_df.iterrows():
    # Size circle based on composite score
    radius = max(2000, row['composite_score'] * 100)

    color = ['red', 'orange', 'yellow', 'lightgreen', 'lightblue'][row['priority_rank'] - 1]

    folium.Circle(
        location=[row['Lat'], row['Lon']],
        radius=radius,
        popup=f"""
        <b>{row['Tehsil']}</b><br>
        Priority Rank: #{row['priority_rank']}<br>
        Composite Score: {row['composite_score']:.1f}<br>
        Population: {row['Population_2023']:,}<br>
        Density: {row['Population_Density']:,.0f}/sq.km<br>
        Growth Rate: {row['Annual_Growth_Rate']:.1f}%
        """,
        color='black',
        fill=True,
        fillColor=color,
        fillOpacity=0.3
    ).add_to(m)

# Add recommended sites
for _, row in sites_df.iterrows():
    # Color based on recommendation level
    if row['Recommendation'] == 'High Priority':
        icon_color = 'red'
        icon = 'star'
    elif row['Recommendation'] == 'Medium Priority':
        icon_color = 'orange'
        icon = 'bolt'
    else:
        icon_color = 'blue'
        icon = 'info-sign'

    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=f"""
        <b>{row['Site_Name']}</b><br>
        Tehsil: {row['Tehsil']}<br>
        Site Score: {row['Site_Score']:.1f}<br>
        Type: {row['Site_Type']}<br>
        Priority: {row['Recommendation']}<br>
        Population Served: {row['Population_Served']:,}<br>
        Growth Rate: {row['Growth_Potential']:.1f}%
        """,
        icon=folium.Icon(color=icon_color, icon=icon)
    ).add_to(m)

# NOW add branded title (after sites_df is created)
title_html = f'''
<div style="position: fixed; 
            top: 10px; left: 50%; transform: translateX(-50%);
            background-color: white; border:2px solid grey; z-index:9999; 
            font-size:16px; padding: 10px; box-shadow: 3px 3px 5px rgba(0,0,0,0.3);
            border-radius: 5px;">
<h3 style="margin:0; text-align:center; color:#333;">Lahore EV Charging Station Site Selection Analysis</h3>
<p style="margin:5px 0 0 0; text-align:center; font-size:12px; color:#666;">Multi-Criteria Analysis | Population: 13M+ | {len(sites_df)} Recommended Sites</p>
<p style="margin:3px 0 0 0; text-align:center; font-size:10px; color:#999; font-style: italic;">
    By Tayyab Manan | GIS Portfolio Project
</p>
</div>
'''
m.get_root().html.add_child(folium.Element(title_html))

# Add professional branding and copyright
branding_html = '''
<div style="position: fixed; 
            bottom: 10px; right: 10px; 
            background-color: rgba(255,255,255,0.95); border:1px solid #ccc; z-index:9999; 
            font-size:11px; padding: 8px 12px; box-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            border-radius: 5px; max-width: 250px;">
<div style="text-align: center; margin-bottom: 5px;">
    <strong style="color: #2c3e50; font-size: 12px;">© 2025 Tayyab Manan</strong>
</div>
<div style="text-align: center; margin-bottom: 3px; color: #7f8c8d; font-size: 10px;">
    GIS Analyst & Spatial Developer
</div>
<div style="text-align: center; margin-bottom: 5px;">
    <a href="#"  return false;" 
       style="color: #3498db; text-decoration: none; font-size: 10px; font-weight: bold;">
        🌐 View More Projects
    </a>
</div>
<div style="text-align: center; font-size: 9px; color: #95a5a6; border-top: 1px solid #ecf0f1; padding-top: 3px;">
    Lahore EV Infrastructure Analysis<br>
    Multi-Criteria Spatial Decision Support
</div>
</div>
'''
m.get_root().html.add_child(folium.Element(branding_html))

# Add legend
legend_html = '''
<div style="position: fixed; 
            bottom: 50px; left: 50px; width: 300px; height: 220px; 
            background-color: white; border:2px solid grey; z-index:9999; 
            font-size:12px; padding: 15px; box-shadow: 3px 3px 5px rgba(0,0,0,0.3);
            border-radius: 5px; overflow: hidden;">
<h4 style="margin-top:0; margin-bottom:10px; color:#333; border-bottom: 1px solid #ccc; padding-bottom: 5px;">
    EV Charging Station Analysis
</h4>

<div style="margin-bottom: 12px;">
<b style="color:#333;">📍 Recommended Sites:</b><br>
<div style="margin: 3px 0;">
    <i class="fa fa-star" style="color:red; width: 15px;"></i> 
    <span style="margin-left: 5px;">High Priority (Phase 1: 0-6 months)</span>
</div>
<div style="margin: 3px 0;">
    <i class="fa fa-bolt" style="color:orange; width: 15px;"></i> 
    <span style="margin-left: 5px;">Medium Priority (Phase 2: 6-18 months)</span>
</div>
<div style="margin: 3px 0;">
    <i class="fa fa-info" style="color:blue; width: 15px;"></i> 
    <span style="margin-left: 5px;">Future Consideration (Phase 3: 18+ months)</span>
</div>
</div>

<div>
<b style="color:#333;">🏛️ Tehsil Priority Zones:</b><br>
<div style="margin: 2px 0; font-size: 11px;">
    <span style="color:#ff4444; font-size:14px; width: 15px; display: inline-block;">●</span> 
    <span>Rank #1: Lahore City</span>
</div>
<div style="margin: 2px 0; font-size: 11px;">
    <span style="color:#ff8800; font-size:14px; width: 15px; display: inline-block;">●</span> 
    <span>Rank #2: Shalimar</span>
</div>
<div style="margin: 2px 0; font-size: 11px;">
    <span style="color:#ffbb00; font-size:14px; width: 15px; display: inline-block;">●</span> 
    <span>Rank #3: Model Town</span>
</div>
<div style="margin: 2px 0; font-size: 11px;">
    <span style="color:#88bb00; font-size:14px; width: 15px; display: inline-block;">●</span> 
    <span>Rank #4: Raiwind</span>
</div>
<div style="margin: 2px 0; font-size: 11px;">
    <span style="color:#4488bb; font-size:14px; width: 15px; display: inline-block;">●</span> 
    <span>Rank #5: Lahore Cantt</span>
</div>
</div>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Save map
m.save('outputs/maps/ev_site_analysis_branded.html')
print("✅ Branded analysis map saved: outputs/maps/ev_site_analysis_branded.html")

# Generate reports (same as before)
print("\n⚡ STEP 5: GENERATING ANALYSIS REPORT")
print("-" * 40)

# Save detailed results
census_df.to_csv('outputs/analysis/tehsil_analysis.csv', index=False)
sites_df.to_csv('outputs/analysis/site_recommendations.csv', index=False)

print("✅ Analysis complete with professional branding!")
print("📁 Branded map: outputs/maps/ev_site_analysis_branded.html")
print("📊 Data files: outputs/analysis/")