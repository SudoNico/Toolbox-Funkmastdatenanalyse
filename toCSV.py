import csv
import os


# checks that the xml line contains the correct atribute and returns the corresponding value
def finde(search, first, skip, line):
    if line.find(search) != -1:
        start = line.find(">")+1
        end = line.find("<",start)
        first = line[start:end]
        skip = True
    return(first, skip)


def toCSV(inputdirectory, outputdirectory, elements, end):

    # an entry is initially empty
    Entry = [""] * len(elements)

    for file in os.listdir(inputdirectory):

        # CSV-Header
        data = [elements]

        filepath = os.path.join(inputdirectory, os.fsdecode(file))
        if os.path.isfile(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        
                        # search if the row contains one of the required attributes
                        # skip is used to end the search when the value of the row is found
                        skip = False    

                        # search for every element
                        for i, element in enumerate(elements):
                            Entry[i], skip = finde(element, Entry[i], skip, line)
                            if skip: break

                        # Entry is added to the data array
                        # </ResponseRecord> corresponds to the end of an entry
                        if line.find(end) != -1:

                            data.append(Entry)
                            Entry = [""] * len(elements)

                #data array with one entry per row is stored in a CSV
                with open(os.path.join(outputdirectory, os.fsdecode(file))+".csv", 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile, delimiter = ",")
                    writer.writerows(data)

            except PermissionError:
                print(f"Skipping {file}: Permission denied")
            except Exception as e:
                print(f"Error reading {file}: {e}")




