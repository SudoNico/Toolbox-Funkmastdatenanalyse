import os

# extracts all attributes with values
def getElements(directory):

    unique = []

    for file in os.listdir(directory):
        filepath = os.path.join(directory, os.fsdecode(file))
        if os.path.isfile(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:

                        #extracts the name of the attribute
                        start = line.find("<")+1
                        end = line.find(">")

                        #Checks if a value follows or if it is just a node in the XML tree
                        hasValue = line.find("<",start)
                        
                        if hasValue != -1:
                            if line[start:end] not in unique:
                                unique.append(line[start:end])

            except PermissionError:
                print(f"Skipping {file}: Permission denied")
            except Exception as e:
                print(f"Error reading {file}: {e}")
    return(unique)
    