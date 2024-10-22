# QGIS analysis

First download the data from overpass -> export to geojson
import as vector layer in qgis
refactor fields on all layers (remove @relation)
import the official campsites layer from this repo
do a hub distance analysis osm->nearest official campsite hub with meters and filter to less than 500m

I could not find a GUI way to do what I wanted (without resulting to manual mouse clicking and what is the fun in that) so I wrestled with chatgpt until I got some working code :)

run this script in the python console to get the missing campsites (those where no osm camp site exist within 500m)
```
# Get the official campsite layer and OSM layer
campsite_layer = QgsProject.instance().mapLayersByName('official')[0]
osm_layer = QgsProject.instance().mapLayersByName('osm_points_within_500m')[0]

# Extract unique HubName values from the OSM layer
unique_hubnames = set()
for feature in osm_layer.getFeatures():
    hubname = feature['HubName']  # Use the actual field name in your OSM layer
    if hubname:
        unique_hubnames.add(hubname)

# Create an expression to select campsites that are not in the OSM HubNames list
expression = f'"drupal_id" NOT IN ({",".join(f"\'{name}\'" for name in unique_hubnames)})'

# Apply the selection on the official campsite layer
campsite_layer.selectByExpression(expression)

# Print the number of selected features
selected_count = campsite_layer.selectedFeatureCount()
print(f"Selected {selected_count} campsites without a matching OSM point")

# If there are selected features, create a new memory layer with the selected campsites
if selected_count > 0:
    # Create a new memory layer with the same fields and geometry type
    new_layer = QgsVectorLayer("Point?crs=EPSG:4326", "Unmatched Campsites", "memory")  # Adjust CRS as needed

    # Copy fields from the original layer
    new_layer_data_provider = new_layer.dataProvider()
    new_layer_data_provider.addAttributes(campsite_layer.fields())
    new_layer.updateFields()

    # Add the selected features to the new layer
    new_layer_data_provider.addFeatures(campsite_layer.selectedFeatures())

    # Add the new layer to the project
    QgsProject.instance().addMapLayer(new_layer)

    print("New layer with unmatched campsites has been created and added to the project.")
else:
    print("No unmatched campsites found.")
```
