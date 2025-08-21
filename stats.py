import csv
import statistics as stats
import heapq
import os
from collections import Counter


def Mean(elements, element, directory):

    values = []

    # check if directory is a directory or just one file
    # makes it posible to handle both file and directory
    if os.path.isfile(directory):
        files = [directory]
    else:
        files = [os.path.join(directory, f) for f in os.listdir(directory)]


    # adds all for the statistics needed values inside an Array
    for file in files:
        with open(file, "r") as f:
            csvFile = csv.reader(f, delimiter=",")
            for line in csvFile:
                if line[elements.index(element)] != element:
                    number = int(line[elements.index(element)])
                    values.append(number)

    # calculates the mean, median, mode and the three highest and lowest values
    Durchschnitt = stats.mean(values)
    Median = stats.median(values)
    Mode = stats.mode(values)


    return(Durchschnitt, Median, Mode)


def getMinMax(what, n, elements, element, directory):

    values = []

    # check if directory is a directory or just one file
    # makes it posible to handle both file and directory
    if os.path.isfile(directory):
        files = [directory]
    else:
        files = [os.path.join(directory, f) for f in os.listdir(directory)]

    # adds all for the statistics needed values inside an Array
    for file in files:
        with open(file, "r") as f:
            csvFile = csv.reader(f, delimiter=",")
            for line in csvFile:
                if line[elements.index(element)] != element:
                    number = int(line[elements.index(element)])
                    values.append(number)

    # 1 -> n smallest
    if what == 1:
        result = heapq.nsmallest(int(n), values)

    # 2 -> n highest
    if what == 2:
        result = heapq.nlargest(int(n), values)

    return result


# returns a counter with the count off every value
def calc(directory, elements, element):
    element_index = elements.index(element)
    data = []
    
    for file in os.listdir(directory):
        with open(os.path.join(directory, os.fsdecode(file)), "r") as f:
            csvFile = csv.reader(f, delimiter=",")
            for line in csvFile:
                value = line[element_index]
                if value != element:
                    data.append(value)
                    
    counter = Counter(data)

    return counter

# returns a list of all values an element has
def getUnique(directory,elements,element):
    element_index = elements.index(element)

    data = set()

    for file in os.listdir(directory):
        with open(os.path.join(directory, os.fsdecode(file)), "r") as f:
            csvFile = csv.reader(f, delimiter=",")
            for line in csvFile:
                value = line[element_index]
                if value != element:
                        data.add(value)
    
    return data
    
