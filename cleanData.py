import os
import csv

def removedouble(directory, elements):

    # CSV-header
    header = ""
    for element in elements:
        header = header + element + ","
    
    # one object in save is one output-line
    save = []
    save.append(header + "\n")

    unique_lines = set()
    filecount = 0

    for file in os.listdir(directory):

        # Defining the file name format file_x with x for a sequentially increasing number
        inputpath = os.path.join(directory, os.fsdecode(file))
        outputpath = os.path.join(directory, "file_")

        with open(inputpath, mode ='r') as f:
            for line in f:

                # duplicate rows are removed
                if line not in unique_lines:
                    if line.find(elements[0])==-1:
                        unique_lines.add(line)
                        save.append(line)

                    # Standardization of the number of entries per CSV to 10000 entries
                    if len(save) == 10001:
                        with open(outputpath + str(filecount) + ".csv", "w", newline="") as savefile:
                            savefile.writelines(save)
                            filecount+=1
                            save = []
                            save.append(header + "\n")
        
        os.remove(inputpath)
                
    # remaining entries
    if len(save) > 1:
        with open(outputpath + str(filecount) + ".csv", "w", newline="") as savefile:
            savefile.writelines(save)



def removeWithout(directory,elements,without):

    filecount = 0

    for file in os.listdir(directory):
        data = []

        # overwrite every file without entrys with value
        inputpath = os.path.join(directory, os.fsdecode(file))

        # saves the ones without the value inside an Array
        with open(inputpath, "r", newline="") as f:
            csvFile = csv.reader(f, delimiter=",")
            for line in csvFile:
                if line and len(line) > elements.index(without):
                    if line[elements.index(without)] != "":
                        data.append(line)
        
        # rerides the inputfile without the entries with the value
        with open(inputpath, "w", newline="") as f:
            csvwriter = csv.writer(f, delimiter=",")
            csvwriter.writerows(data)

        filecount += 1








            

