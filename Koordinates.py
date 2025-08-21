import os
import csv
from collections import Counter


def getKoordinates(directory,elements,latitude,longitude,format):

    Koordinates=[]

    for file in os.listdir(directory):
        filepath = os.path.join(directory, os.fsdecode(file))
        with open(filepath, mode ='r') as f:
            csvFile = csv.reader(f, delimiter=",")
            for line in csvFile:
                if line[elements.index(latitude)] != latitude and line[elements.index(latitude)] != "":
                    lat = line[elements.index(latitude)]
                    lon = line[elements.index(longitude)]

                    # converts coordinates in Decimal degrees format
                    if format == 2:
                        direction = lat[0]
                        degrees = int(lat[1:3])
                        minutes = int(lat[3:5])
                        seconds = float(lat[5:])
                        Dec_lat = degrees + minutes / 60 + seconds / 3600
                        Dec_lat = f"{direction}{Dec_lat:.4f}"

                        direction = lon[0]
                        degrees = int(lon[1:4])
                        minutes = int(lon[4:6])
                        seconds = float(lon[6:])
                        Dec_lon = degrees + minutes / 60 + seconds / 3600
                        Dec_lon = f"{direction}{Dec_lon:.4f}"

                        # file exists of the converted values, the original values and their counts
                        Koordinates.append(f"{Dec_lat},{Dec_lon},{lat},{lon}")

                    else:
                        Koordinates.append(f"{lat},{lon},{lat},{lon}")

    # counts the amount of entries for an coordinate
    counter = Counter(Koordinates)

    return counter

                    