import os
import csv
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from phonenumbers import geocoder
import math
from datetime import datetime, timedelta

badNumbers = set()

def hasMultiple(directory,elements, AttributeA, AttributeB):
    # check if directory is a directory or just one file
    # makes it posible to handle both file and directory
    if os.path.isfile(directory):
        files = [directory]
    else:
        files = [os.path.join(directory, f) for f in os.listdir(directory)]

    indexA = elements.index(AttributeA)
    
    indexB = elements.index(AttributeB)

    #creates a dictionary with all elements of the first attribute as key and attribute 2 as value
    #checking for 1:1 mapping
    Dict = {}

    for file in files:
        with open(file, "r") as f:
            csvFile = csv.reader(f, delimiter=",")
            for line in csvFile:

                #skip header and entries without one of the elements
                if line[indexA] == AttributeA:
                    continue

                if line[indexA] == "" or line[indexA] == "0":
                    continue

                if line[indexB] == "" or line[indexB] == "0":
                    continue

                if line[indexA] not in Dict:
                    Dict[line[indexA]] = line[indexB]

                if Dict[line[indexA]] != line[indexB]:
                    return(AttributeA + " has multiple elements of " + AttributeB)
                    
    
    return(AttributeA + " has only one element of " + AttributeB)

# A Person for the List, can have multiple iMSIs, iMEIs and phonenumbers
class Person:
    def __init__(self, iMSI, iMEI, mSISDN):
        self.iMSIList = []
        self.iMEIList = []
        self.mSISDNList = []
        self.line_count = 0
        self.location = ""
        self.addiMSI(iMSI)
        self.addiMEI(iMEI)
        self.addSISDN(mSISDN)
        self.line_count += 1
        self.visits = []

    def addiMSI(self, iMSI):
        if iMSI and iMSI not in self.iMSIList:
            self.iMSIList.append(iMSI)

    def addiMEI(self, iMEI):
        if iMEI and iMEI not in self.iMEIList:
            self.iMEIList.append(iMEI)

    def addSISDN(self, mSISDN):
        if mSISDN and mSISDN not in self.mSISDNList and mSISDN != "0":
            self.mSISDNList.append(mSISDN)

    def increment_count(self):
        self.line_count+=1

    def add_visit(self, start, location, end):
        self.visits.append({"time": start, "end": end, "location": location})


def safe_str(val):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return ""
    return str(val).strip()


# function to create list of all Persons in the dataset
def ProfileList(project,directory,WithLocations,longsequence,space,time):

    RCT_lookup= lookup(os.path.join(project,"Funkmasten.csv"))
    
    if os.path.isfile(directory):
        files = [directory]
    else:
        files = [os.path.join(directory, f) for f in os.listdir(directory)]

    Persons = []

    iMSI_index, iMEI_index, mSISDN_index = {}, {}, {}

    for file in files:
        with open(file, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                iMSI = safe_str(row.get("iMSI", ""))
                iMEI = safe_str(row.get("iMEI", ""))
                mSISDN = safe_str(row.get("mSISDN", ""))

                if not (iMSI or iMEI or mSISDN):
                    continue

                # find Person by Index
                person = None
                if iMSI and iMSI in iMSI_index:
                    person = iMSI_index[iMSI]
                elif iMEI and iMEI in iMEI_index:
                    person = iMEI_index[iMEI]
                elif mSISDN and mSISDN in mSISDN_index:
                    person = mSISDN_index[mSISDN]

                # if no Person found create new one
                if not person:
                    person = Person(iMSI, iMEI, mSISDN)
                    Persons.append(person)
                else:
                    person.addiMSI(iMSI)
                    person.addiMEI(iMEI)
                    person.addSISDN(mSISDN)
                    person.increment_count()

                # update index
                for ims in person.iMSIList:
                    iMSI_index[ims] = person
                for ime in person.iMEIList:
                    iMEI_index[ime] = person
                for ms in person.mSISDNList:
                    mSISDN_index[ms] = person

                # save Movement Sequence
                if WithLocations:
                    startTime = row.get("startTime")
                    
                    lat = safe_str(row.get("latitude"))
                    if not lat:
                        lat = safe_str(row.get("latitudeDec"))

                    lon = safe_str(row.get("longitude"))
                    if not lon:
                        lon = safe_str(row.get("longitudeDec"))
                    
                    location = None

                    if lat and lon and RCT_lookup:
                            key = (lat.strip(), lon.strip())
                            location = RCT_lookup.get(key)
                        
                    if startTime and location:
                        try:
                            start = datetime.strptime(startTime, "%Y%m%d%H%M%S%z")
                            end = row.get("endTime")
                            end = datetime.strptime(end, "%Y%m%d%H%M%S%z")

                        except Exception:
                            continue
                        person.add_visit(start, location, end)

    # sort visited radio cell towers by time visited
    if WithLocations:
        for p in Persons:
            p.visits.sort(key=lambda v: v["time"])

    if longsequence:
        # find global earliest and latest time
            all_times = [v["time"] for p in Persons for v in p.visits]
            if all_times:
                start = min(all_times)
                end   = max(all_times)

                for p in Persons:
                    p.sequences = split(p.visits,start,end,time,space)
    
    return Persons


#Locates a Phonenumber, returns its country
def LocatePhoneNumber(Number):
    if Number and not Number.startswith("+"):
        Number = "+" + Number

    try:
        phoneNumber = phonenumbers.parse(Number)
    except NumberParseException:
        badNumbers.add(Number)
        return "badNumber"
 
    geolocation = geocoder.description_for_number(phoneNumber,"de")
    
    return geolocation

#Load a lookup dict from coordinates to radio cell tower symbol
def lookup(RCT_csv):

    lookup = {}
    with open(RCT_csv, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lat = safe_str(row.get("Latitude"))
            lon = safe_str(row.get("Longitude"))
            mast = safe_str(row.get("Funkmast"))

            if lat and lon and mast:
                key = (lat.strip(), lon.strip())
                lookup[key] = mast
    return lookup

#builds a simple sequence
def build_sequence(visits):
    seq = ""
    last = None
    for v in visits:
        loc = v["location"]
        if loc and loc != last:
            seq += loc
        last = loc
    return seq

#splits a sequence in periods
def split(visits, start, end, time, space):
    sequences = []
    window = timedelta(minutes=time)

    visits = sorted(visits, key=lambda v: v["time"])
    x = 0
    n = len(visits)

    current = start
    while current < end:
        next_window = current + window
        symbols = []

        # move x forward to skip past visits that ended before this period        
        while x < n and visits[x]["end"] < current:
            x += 1


        # collect visits that overlap this window
        j = x
        last = None
        while j < n and visits[j]["time"] < next_window:
            loc = visits[j]["location"]
            if loc != last:      # collapse consecutive duplicates inside same period
                symbols.append(loc)
            last = loc
            j += 1

        sequences.append("".join(symbols) if symbols else space)
        current = next_window

    return sequences

