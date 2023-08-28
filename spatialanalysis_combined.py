import pandas as pd
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import pysal.lib as ps
from pysal.explore import esda

# Nischay Thakur
# GEOG376 Project
# UID:116553957

# Load data
population_data = pd.read_csv("New_York_City_Population_By_Neighborhood_Tabulation_Areas.csv")
geo_data = gpd.read_file("geo_export_0f7088a2-d921-4857-abfe-d1b8301ebe1b.shp")


# Merge datasets
merged_data = geo_data.merge(population_data, left_on="ntacode", right_on="NTA Code")

# Calculate area (in square kilometers) and population density
merged_data["area"] = merged_data["geometry"].area / 10**6
merged_data["population_density"] = merged_data["Population"] / merged_data["area"]

# Create figure and axes for the subplots
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle("Spatial Analysis of NYC Population Density", fontsize=16)

# Create a choropleth map
merged_data.plot(column="population_density", cmap="viridis", legend=True, ax=axes[0, 0])
axes[0, 0].set_title("Population Density by Neighborhood")

# Spatial analysis: LISA
# Calculate spatial weights matrix
w = ps.weights.Queen.from_dataframe(merged_data)

# Row-standardize the weights matrix
w.transform = "r"

# Compute Local Moran's I
local_moran = esda.Moran_Local(merged_data["population_density"], w)

# Create a new column for LISA cluster categories
merged_data["lisa_cluster"] = "Not Significant"
merged_data.loc[local_moran.p_sim < 0.05, "lisa_cluster"] = "Significant"

# Map LISA clusters
merged_data.plot(column="lisa_cluster", categorical=True, legend=True, cmap="coolwarm", ax=axes[0, 1])
axes[0, 1].set_title("LISA Clusters of Population Density")

# Create a scatterplot of Moran's I
sns.scatterplot(x=local_moran.Is, y=local_moran.y, hue=merged_data["lisa_cluster"], ax=axes[1, 0])
axes[1, 0].set_title("Moran Scatterplot")
axes[1, 0].set_xlabel("Local Moran's I")
axes[1, 0].set_ylabel("Population Density")

# Hide empty subplot
axes[1, 1].axis("off")

plt.tight_layout()
plt.show()

