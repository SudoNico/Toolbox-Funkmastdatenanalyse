import folium
import csv 
import os

def createMap(Directory):
    locations = []

    # uses the coordinates saved in add-coordinates
    with open(os.path.join(Directory,"Koordinates.csv"), "r") as f:
        csvFile = csv.reader(f, delimiter=",")
        next(csvFile)
        i = 1
        for line in csvFile:

            # uses the converted coordinates instead of the original ones
            lat = line[0]
            lat = lat[1:]

            long = line[1]
            long = long[1:] 

            entries = line[4]  
            locations.append((lat,long,str(i),entries))
            i +=1

    lats = [float(loc[0]) for loc in locations]
    longs = [float(loc[1]) for loc in locations]

    # calculates the center of all coordinates to center the map
    avg_lat = sum(lats) / len(lats)
    avg_long = sum(longs) / len(longs)

    map_center = [avg_lat, avg_long]
    my_map = folium.Map(location=map_center, zoom_start=10)

    # adds the coordinates
    for lat, lon, label, entries in locations:
        popup_text = f"<b>{label}</b><br>Entries: {entries}"
        folium.Marker([lat, lon], popup=popup_text).add_to(my_map)

        my_map.save(os.path.join(Directory,"Map.html"))

        my_map