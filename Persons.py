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

    def add_visit(self, time, location):
        self.visits.append({"time": time, "location": location})


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
                            t = datetime.strptime(startTime, "%Y%m%d%H%M%S%z")
                        except Exception:
                            continue
                        person.add_visit(t, location)

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

    if not visits:
        return [space]

    sequences = []
    window_start = start
    window_end = window_start + timedelta(minutes=time)

    idx = 0
    seq = ""
    last = None

    while window_start <= end:
        # collect all visits inside this window
        while idx < len(visits) and visits[idx]["time"] < window_end:
            loc = visits[idx]["location"]
            if loc and loc != last:
                seq += loc
            last = loc
            idx += 1

        # finish window
        if seq:
            sequences.append(seq)
        else:
            sequences.append(space)

        # advance window
        seq = ""
        last = None
        window_start = window_end
        window_end = window_start + timedelta(minutes=time)

    return sequences

