from datetime import datetime, timedelta
import os
import csv
import seaborn as sns
import matplotlib.pyplot as plt


# get a Time period
def getTimeRange(directory, elements, begin, end):

    start_list=[]
    stop_list=[]

    # for every csv file
    for file in os.listdir(directory):
        with open(os.path.join(directory, os.fsdecode(file)), mode ='r') as f:
            csvFile = csv.reader(f, delimiter=",")
            for line in csvFile:

                # for every csv line except the header
                if line[elements.index(begin)] != begin:

                    # list for the timestamps from the start element
                    timestamp = line[elements.index(begin)]
                    start = datetime.strptime(timestamp, "%Y%m%d%H%M%S%z")
                    start_list.append(start)

                    # list for the timestamps from the end element
                    timestamp = line[elements.index(end)]
                    stop = datetime.strptime(timestamp, "%Y%m%d%H%M%S%z")
                    stop_list.append(stop)
    
    # returns the earliest and latest values of the timestamp lists
    start = min(start_list)
    stop = max(stop_list)

    # calculates the time difference
    difference = stop - start

    return start, stop, difference


def getheatmap(directory, elements, begin, end):
    start, stop, difference = getTimeRange(directory, elements, begin, end)

    Stunden = []
    days = []
    current_day = start.date()

    # day values for X axis 
    while current_day <= stop.date():
        days.append(current_day)
        current_day += timedelta(days=1)

    # hour values for Y axis
    for i in range(24):
        Stunden.append(str(i)+"h")

    data = [[0 for x in range(len(days))] for y in range(24)]


    for file in os.listdir(directory):
        filepath = os.path.join(directory, os.fsdecode(file))
        with open(filepath, mode ='r') as f:
            csvFile = csv.reader(f, delimiter=",")
            for line in csvFile:

                # for every csv line except the header
                if line[elements.index(begin)] != begin:
                    temp_start = datetime.strptime(line[elements.index(begin)], "%Y%m%d%H%M%S%z")
                    temp_stop = datetime.strptime(line[elements.index(end)], "%Y%m%d%H%M%S%z")

                    current = temp_start
                    while current <= temp_stop:

                        # get index
                        hour_index = current.hour
                        day_index = (current.date() - start.date()).days

                        # write in 2d-Array
                        if 0 <= hour_index < 24 and 0 <= day_index < len(days):
                            data[hour_index][day_index] += 1

                        current += timedelta(hours=1)
                
    sns.heatmap(data, cmap='coolwarm',linewidths=0.5,xticklabels=days,yticklabels=Stunden)
    plt.show()